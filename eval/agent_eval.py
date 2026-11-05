"""How often does each agent cite a source that actually matches its mandate and event? Expected documents are set by hand."""
import json, sys
from pathlib import Path
ROOT=Path(__file__).resolve().parent.parent
H={"UAE-EXTRACTS","HEALTH-NOTES","CMS-HEALTH","TAMIMI-HEALTH","TROWERS-HEALTH"}; P={"UAE-EXTRACTS","PDPL-NOTES","PDPL-GUIDE","EDPB-05-2021"}
T={"UAE-TEL-2003","UAE-TEL-AR"}; I={"ITU-IAB-2026","ITU-PORTO-2026","ITU-ABUJA-2025","UNCLOS"}; N={"ITU-IAB-2026","ITU-Y3172","ITU-Y3173"}
EXP={("E1","netops"):N,("E2","netops"):N,("E2","regulator"):T,("E3","health"):H,("E4","netops"):N,("E4","health"):H,("E4","privacy"):P,("E5","crisis"):I,("E6","regulator"):T,
     ("J1","netops"):N,("J1","privacy"):P,("J1","regulator"):T,("E7","netops"):N,("E7","regulator"):T|I,("E7","crisis"):I,("E8","netops"):N,("E9","regulator"):T,("E9","crisis"):I}
COMP={"IN-TEL-S20","US-TSP","EU-OIR-A3","UK-CA-132","EU-AIA-ANNEX3","EU-AIA-ART14","EDPB-05-2021","ITU-IAB-2026"}
def score(path):
    r=json.loads(Path(path).read_text()); hit=tot=withc=0; miss=[]; adv=[0,0]
    for e in r["events"]:
        for a in e["assessments"]:
            docs={c["cid"].split("#")[0] for c in a["claims"]}
            if a["agent"]=="adviser": adv[0]+=1; adv[1]+=bool(docs&COMP); continue
            x=EXP.get((e["id"],a["agent"]))
            if not x: continue
            tot+=1; withc+=bool(docs); ok=bool(docs&x); hit+=ok
            if not ok: miss.append((e["id"],a["agent"]))
    return {"on_mandate":f"{hit}/{tot}","with_claims":f"{withc}/{tot}","adviser_on_topic":f"{adv[1]}/{adv[0]}","missed":miss,"verified":sum(len(a["claims"]) for e in r["events"] for a in e["assessments"]),"rejected":sum(a["rejected"] for e in r["events"] for a in e["assessments"])}
if __name__=="__main__":
    out={p:score(ROOT/p/"run.json") for p in sys.argv[1:]}
    print(json.dumps(out,indent=1)); (ROOT/"eval/agent_results.json").write_text(json.dumps(out,indent=1))
