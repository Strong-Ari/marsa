"""Check that every citation in rules and gaps appears verbatim in the knowledge base."""
import json, sys, yaml
from pathlib import Path
from .evidence import _n
ROOT=Path(__file__).resolve().parent.parent
def main():
    txt={}
    for l in (ROOT/"kb/chunks.jsonl").open():
        r=json.loads(l); txt.setdefault(r["doc"],[]).append(_n(r["text"]))
    items=[]
    for r in yaml.safe_load((ROOT/"rules/policy_rules.yaml").read_text())["rules"]:
        items+=[(r["id"],c) for c in r.get("citations",[])]
    for g in yaml.safe_load((ROOT/"rules/gaps.yaml").read_text())["gaps"]:
        items+=[(g["id"],c) for c in g.get("local_evidence",[])+g.get("global_examples",[])]
    for g,row in yaml.safe_load((ROOT/"rules/matrix.yaml").read_text())["rows"].items():
        items+=[(f"{g}/{k}",c) for k,c in row.items()]
    bad=[(i,c) for i,c in items if not any(_n(c["quote"]) in t for t in txt.get(c["doc"],[]))]
    print(f"{len(items)-len(bad)}/{len(items)} citations verified verbatim")
    for i,c in bad: print("MISSING",i,c["doc"],c["quote"][:90])
    return 1 if bad else 0
if __name__=="__main__": sys.exit(main())
