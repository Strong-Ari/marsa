"""Append-only audit log. Each entry hashes its predecessor, so any edit breaks the chain."""
import hashlib, json
from pathlib import Path
GENESIS = "0"*64
def _digest(prev, body): return hashlib.sha256((prev+json.dumps(body,sort_keys=True,ensure_ascii=False)).encode()).hexdigest()
class Audit:
    def __init__(self, path, clock=None):
        self.path=Path(path); self.path.parent.mkdir(parents=True,exist_ok=True); self.path.write_text("")
        self.prev=GENESIS; self.n=0; self.entries=[]; self.clock=clock or (lambda:0)
    def log(self, kind, actor, **data):
        body={"seq":self.n,"t_min":self.clock(),"kind":kind,"actor":actor,**data}
        h=_digest(self.prev,body); e={"prev":self.prev,"hash":h,"body":body}
        with self.path.open("a") as f: f.write(json.dumps(e,ensure_ascii=False)+"\n")
        self.prev=h; self.n+=1; self.entries.append(e); return h
def verify(path):
    prev=GENESIS
    for i,l in enumerate(Path(path).open()):
        e=json.loads(l)
        if e["prev"]!=prev or _digest(prev,e["body"])!=e["hash"]: return False,i
        prev=e["hash"]
    return True,None
