"""Retrieval benchmark and adversarial evidence-gate test. Writes eval/results.json."""
import json, random, yaml
from pathlib import Path
from marsa.kb import KB
from marsa import evidence
ROOT=Path(__file__).resolve().parent.parent
kb=KB(); G=yaml.safe_load((ROOT/"eval/golden.yaml").read_text()); res={"n_queries":len(G),"retrieval":{}}
for mode,boost in (("dense",1),("bm25",1),("hybrid",1),("hybrid",1.5)):
    h1=h5=rr=0; ar=[0,0]
    for g in G:
        rank=next((i for i,x in enumerate(kb.search(g["q"],k=5,mode=mode,boost_tier1=boost)) if x["doc"] in g["doc"]),None)
        h1+=rank==0; h5+=rank is not None; rr+=0 if rank is None else 1/(rank+1)
        if g.get("lang")=="ar": ar[0]+=1; ar[1]+=rank is not None
    res["retrieval"][f"{mode}+boost{boost}"]={"hit@1":round(h1/len(G),3),"hit@5":round(h5/len(G),3),"mrr":round(rr/len(G),3),"arabic_hit@5":f"{ar[1]}/{ar[0]}"}
r=random.Random(7); tier1=[x for x in kb.recs if x["tier"]==1 and len(x["text"])>400]; caught=0; passed=0; n=500
for i in range(n):
    c=r.choice(tier1); s=r.randrange(0,len(c["text"])-150); q=c["text"][s:s+120]; got={c["cid"]:c}
    passed+=evidence.check({"claim":"x","cid":c["cid"],"quote":q},got)[0]
    w=q.split(); j=r.randrange(1,len(w)-1); m=i%4  # interior word: removing an end word leaves a genuine substring
    if m==0: w[j]="not" if w[j]!="not" else "always"
    elif m==1: w[j]=str(r.randrange(10**6))
    elif m==2: del w[j]
    bad={"claim":"x","cid":c["cid"] if m!=3 else "FAKE#1","quote":" ".join(w)}
    caught+=not evidence.check(bad,got)[0]
res["evidence_gate"]={"genuine_quotes_passed":f"{passed}/{n}","tampered_quotes_rejected":f"{caught}/{n}"}
(ROOT/"eval/results.json").write_text(json.dumps(res,indent=1)); print(json.dumps(res,indent=1,ensure_ascii=False))
