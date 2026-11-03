"""Build and query the MARSA knowledge base.

Pipeline follows the ITU reference notebook (parse, chunk, embed, FAISS) and adds
what auditors need: page and article locators, source hashes, legal-force metadata,
and hybrid dense + BM25 retrieval.
"""
from __future__ import annotations
import argparse, hashlib, html, json, pickle, re, zipfile
from pathlib import Path
import numpy as np, yaml

ROOT = Path(__file__).resolve().parent.parent
RAW, IDX = ROOT/"corpus"/"raw", ROOT/"kb"
EMBED_MODEL = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
ART = re.compile(r"(?m)^\s*(?:\*\*)?(Article\s*\(?\d+[A-Za-z]?\)?|Section\s+\d+[A-Z]*|Recommendation\s+\d+)\b")

def norm(t): return re.sub(r"[ \t]+"," ",t.replace("\xa0"," ")).strip()

def parse(path: Path):
    """Return a list of (page, text). HTML and text count as one page."""
    s = path.suffix.lower()
    if s == ".pdf":
        import pymupdf
        return [(i+1, p.get_text()) for i,p in enumerate(pymupdf.open(path))]
    if s == ".docx":
        from docx import Document
        return [(1, "\n".join(p.text for p in Document(path).paragraphs))]
    if s in (".html",".htm"):
        from bs4 import BeautifulSoup
        b = BeautifulSoup(path.read_text(errors="ignore"), "lxml")
        for x in b(["script","style","nav","footer","header","aside","form"]): x.decompose()
        return [(1, b.get_text("\n"))]
    return [(1, path.read_text(errors="ignore"))]

def chunks(pages, size=200, overlap=30):
    article = None; out = []
    for page, text in pages:
        paras = [re.sub(r"\s+"," ",p).strip() for p in re.split(r"\n\s*\n|(?=\n\s*Article\s*\(?\d)", text)]
        buf = []
        def flush():
            nonlocal buf
            if len(buf) >= 12: out.append({"page":page,"article":article,"text":" ".join(buf)})
            buf = buf[-overlap:] if len(buf) > overlap else []
        for p in paras:
            if not p: continue
            m = ART.match(p)
            if m:
                flush(); buf = []
                article = re.sub(r"\s+"," ",m.group(1))
            for w in p.split():
                buf.append(w)
                if len(buf) >= size: flush()
        flush()
    return out

def tokens(t): return re.findall(r"[a-z0-9؀-ۿ]+", t.lower())

def build():
    from sentence_transformers import SentenceTransformer
    import faiss
    from rank_bm25 import BM25Okapi
    m = yaml.safe_load((ROOT/"corpus"/"manifest.yaml").read_text())
    docs = [dict(d, tier=1) for d in m["documents"]]
    known = {"ai_strategies"}
    for f in sorted((ROOT/"corpus"/"reference_docs").iterdir()):
        docs.append({"id":"REF-"+re.sub(r"[^A-Za-z0-9]+","-",f.stem)[:40],"file":f"../reference_docs/{f.name}",
          "title":f.stem.replace("_"," "),"authority":"ITU reference set","jurisdiction":"Various","force":"soft_law",
          "role":["adviser"],"url":"https://github.com/CrashingGuru/ITUAIReadiness","tier":2})
    recs, report = [], []
    for d in docs:
        p = (RAW/d["file"]).resolve()
        sha = hashlib.sha256(p.read_bytes()).hexdigest()
        cs = chunks(parse(p))
        report.append({k:d.get(k) for k in("id","title","authority","jurisdiction","force","tier","url","caveat")}|{"sha256":sha,"chunks":len(cs)})
        for i,c in enumerate(cs):
            recs.append({"cid":f"{d['id']}#{i}","doc":d["id"],"title":d["title"],"authority":d["authority"],"jurisdiction":d["jurisdiction"],
              "force":d["force"],"tier":d["tier"],"role":d["role"],"url":d["url"],"sha256":sha,**c})
        print(d["id"],len(cs),flush=True)
    IDX.mkdir(exist_ok=True)
    with (IDX/"chunks.jsonl").open("w") as f:
        for r in recs: f.write(json.dumps(r,ensure_ascii=False)+"\n")
    (IDX/"inventory.json").write_text(json.dumps(report,indent=1,ensure_ascii=False))
    pickle.dump(BM25Okapi([tokens(r["text"]) for r in recs]), open(IDX/"bm25.pkl","wb"))
    model = SentenceTransformer(EMBED_MODEL)
    v = model.encode([r["text"] for r in recs],batch_size=32,normalize_embeddings=True,show_progress_bar=False,convert_to_numpy=True).astype("float32")
    ix = faiss.IndexFlatIP(v.shape[1]); ix.add(v); faiss.write_index(ix,str(IDX/"faiss.index"))
    print("indexed",len(recs))

class KB:
    def __init__(self):
        import faiss
        self.recs=[json.loads(l) for l in (IDX/"chunks.jsonl").open()]
        self.by={r["cid"]:r for r in self.recs}
        self.ix=faiss.read_index(str(IDX/"faiss.index"))
        self.bm=pickle.load(open(IDX/"bm25.pkl","rb"))
        self._m=None
        self.tier1=np.array([r["tier"]==1 for r in self.recs])
    @property
    def model(self):
        if self._m is None:
            from sentence_transformers import SentenceTransformer
            self._m=SentenceTransformer(EMBED_MODEL)
        return self._m
    def search(self,q,k=6,mode="hybrid",role=None,jurisdiction=None,boost_tier1=1.5,docs=None):
        """Reciprocal-rank fusion of dense and BM25, with filters and a domain-tier boost."""
        n=len(self.recs) if docs else 300; score=np.zeros(len(self.recs))
        if mode in("hybrid","dense"):
            v=self.model.encode([q],normalize_embeddings=True,convert_to_numpy=True).astype("float32")
            _,I=self.ix.search(v,n)
            for r,i in enumerate(I[0]): score[i]+=1/(60+r)
        if mode in("hybrid","bm25"):
            b=self.bm.get_scores(tokens(q))
            for r,i in enumerate(np.argsort(-b)[:n]):
                if b[i]>0: score[i]+=1/(60+r)
        if boost_tier1!=1: score=np.where(self.tier1,score*boost_tier1,score)
        out=[]
        for i in np.argsort(-score):
            if score[i]<=0 or len(out)>=k: break
            r=self.recs[i]
            if docs and r["doc"] not in docs: continue
            if role and role not in r["role"]: continue
            if jurisdiction and r["jurisdiction"] not in jurisdiction: continue
            out.append(dict(r,score=float(score[i])))
        return out

if __name__=="__main__":
    a=argparse.ArgumentParser();a.add_argument("cmd");x=a.parse_args()
    if x.cmd=="build": build()
