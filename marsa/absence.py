"""Absence test: a claim that a text is silent is backed by a counted term search, not by a model's impression."""
import json, re, sys
from pathlib import Path
ROOT=Path(__file__).resolve().parent.parent
TESTS=[("UAE-TEL-2003",["emergency","disaster","crisis","priority"]),
       ("ITU-IAB-2026",["privacy","personal data","data protection","data localisation","data localization","human oversight"]),
       ("ITU-Y3172",["regulat","legal","oversight"]),
       ("ITU-Y3173",["regulat","legal"])]
def main():
    t={}
    for l in (ROOT/"kb/chunks.jsonl").open():
        r=json.loads(l); t.setdefault(r["doc"],[]).append(r["text"].lower())
    out=[]
    for d,terms in TESTS:
        s=" ".join(t[d]); out.append({"doc":d,"counts":{x:len(re.findall(re.escape(x),s)) for x in terms}})
    (ROOT/"eval/absence.json").write_text(json.dumps(out,indent=1)); print(json.dumps(out,indent=0))
if __name__=="__main__": main()
