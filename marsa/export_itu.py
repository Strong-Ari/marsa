"""Write the knowledge base in the layout used by the ITU reference notebook, so it can be reloaded there.
The notebook's CONFIG must name the same embedding model, which is recorded in config.json."""
import json, pickle, shutil
from pathlib import Path
from .kb import EMBED_MODEL
ROOT=Path(__file__).resolve().parent.parent
def main(out=ROOT/"kb_itu_format"):
    out.mkdir(exist_ok=True); docs=[]
    for l in (ROOT/"kb/chunks.jsonl").open():
        r=json.loads(l); docs.append({"source":r["doc"],"chunk_id":r["cid"],"text":r["text"],"title":r["title"],"force":r["force"],"jurisdiction":r["jurisdiction"],"page":r["page"],"url":r["url"]})
    shutil.copy(ROOT/"kb/faiss.index",out/"faiss.index"); pickle.dump(docs,open(out/"metadata.pkl","wb"))
    (out/"config.json").write_text(json.dumps({"embedding_model_name":EMBED_MODEL,"normalize_embeddings":True,"chunks":len(docs)},indent=1)); print(out,len(docs))
if __name__=="__main__": main()
