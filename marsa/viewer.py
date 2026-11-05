"""Build the self-contained Incident Room page from run outputs."""
import json, sys, yaml
from .after_action import build
from pathlib import Path
ROOT=Path(__file__).resolve().parent.parent
MAP=[
 {"node":"SRC","marsa":"Optical, BGP and flow telemetry; event feeds","readiness":"D13 Digital Infrastructure; D1 Data/Model Marketplace","docs":"Y.3172; IAB monitoring recommendations; Telecom Law Art. 72(3)"},
 {"node":"C","marsa":"In-country collectors with service tags, no payload capture","readiness":"D13; D12 Granular Priorities","docs":"Decree-Law 45/2021 Art. 1; Telecom Law Art. 72(3)"},
 {"node":"PP","marsa":"Normalise metrics, drop identifiers, tag traffic class","readiness":"D1; D4 Contextualization","docs":"Federal Law 2/2019 Art. 13; EDPB 05/2021"},
 {"node":"M","marsa":"Utilisation forecast, route planner, agent LLM","readiness":"D5 Integration in Workflows; D3 Cross-Domain Correlation","docs":"Y.3173; EU AI Act Annex III(2)"},
 {"node":"P","marsa":"Evidence gate, deterministic policy gateway, human approval","readiness":"D10 AI & Policies; D8 Collaboration with AI; D7 Strategy Alignment","docs":"Y.3172 P node; EU AI Act Art. 14; India Telecom Act s.20"},
 {"node":"D","marsa":"Approved actions with human-set time limit and rollback","readiness":"D9 Impacts of Humans; D13","docs":"UK Communications Act s.132; US TSP"},
 {"node":"SINK","marsa":"Network controllers, crisis cell console, after-action report","readiness":"D6 Human Interface; D11 AI for Inclusion","docs":"IAB SPOC recommendation; Porto Declaration"},
]
NAMES={"q.gguf":"Qwen2.5-3B Q4 (local CPU)","q7.gguf":"Qwen2.5-7B Q4 (local CPU)"}
def main(a="runs/final",out="viewer/marsa_incident_room.html"):
    r=lambda p:json.loads((ROOT/p).read_text())
    inj=r(a+"/run.json"); inj["backend"]=NAMES.get(inj["backend"],inj["backend"])
    base=dict(inj,events=[e for e in inj["events"] if not e["id"].startswith("J")])
    d={"run":base,"run_injected":inj,"gaps":yaml.safe_load((ROOT/"rules/gaps.yaml").read_text())["gaps"],
       "absence":r("eval/absence.json"),"matrix":yaml.safe_load((ROOT/"rules/matrix.yaml").read_text()),"aar":build(inj),"reuse":build(r("runs/reuse/run.json")),
       "chunks":[{k:c.get(k) for k in ("text","title","article","page","force","jurisdiction")} for c in map(json.loads,(ROOT/"kb/chunks.jsonl").open()) if c["tier"]==1],"rules":yaml.safe_load((ROOT/"rules/policy_rules.yaml").read_text())["rules"],"agent_eval":r("eval/agent_results.json")[a],"eval":r("eval/results.json"),"mapping":MAP,
       "inventory":[x for x in r("kb/inventory.json") if x["tier"]==1],
       "audit":[json.loads(l) for l in (ROOT/a/"audit.jsonl").open()]}
    t=(ROOT/"viewer/template.html").read_text().replace("/*__DATA__*/null",json.dumps(d,ensure_ascii=False).replace("</","<\\/").replace("\ufffd"," "))
    (ROOT/out).write_text(t); print(out,len(t))
if __name__=="__main__": main(*sys.argv[1:])
