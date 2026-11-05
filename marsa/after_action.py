"""Build the after-action report from gateway records. It uses no model, so every line traces to a rule or a human."""
import json, sys
from pathlib import Path
import yaml
ROOT=Path(__file__).resolve().parent.parent
def build(run):
    gaps={g["id"]:g for g in yaml.safe_load((ROOT/"rules/gaps.yaml").read_text())["gaps"]}; out=[]
    for e in run["events"]:
        for d in e["decisions"]:
            c=d["citations"][0] if d["citations"] else None
            ex=[x for g in d["gaps"] for x in gaps[g]["global_examples"]][:1]
            h=d.get("human")
            if d["verdict"]=="ALLOW": o="Executed by the gateway."
            elif d["verdict"]=="DENY": o="Blocked by the gateway."
            elif h: o=f"Human decision: {h['decision'].replace('_',' ')}. {h['note']}"
            else: o="Waiting for: "+", ".join(d["approver"]).replace("_"," ")+"."
            out.append({"action":d["action"],"t":e["t"],"verdict":d["verdict"],"legal_status":d["legal_status"],"description":d["description"],"why":" ".join(d["reasons"]),
              "provision":f"{c['doc']} {c['locator']}: {c['quote']}" if c else "No provision matched.","comparator":f"{ex[0]['doc']}: {ex[0]['why']}" if ex else "","gaps":d["gaps"],"outcome":o})
    return out
def markdown(run):
    L=[f"# After-action report: {run['scenario']['title']}","",run["scenario"]["note"],"",f"Audit head: `{run['audit']['head']}`","",]
    for d in build(run):
        L+=[f"## T+{d['t']} {d['action']}: {d['description']}","",f"- **Verdict:** {d['verdict']}, law {d['legal_status']}",f"- **Why:** {d['why']}",f"- **Text relied on:** {d['provision']}"]
        if d["comparator"]: L.append(f"- **Elsewhere:** {d['comparator']}")
        L+=[f"- **Outcome:** {d['outcome']}",""]
    return "\n".join(L)
if __name__=="__main__":
    d=sys.argv[1] if len(sys.argv)>1 else "runs/final"
    (ROOT/d/"after_action.md").write_text(markdown(json.loads((ROOT/d/"run.json").read_text()))); print(d)
