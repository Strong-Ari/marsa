"""Run a crisis exercise: release events, collect gated assessments, decide actions, and write the audit trail."""
import argparse, json, sys
from pathlib import Path
import yaml
from .audit import Audit, verify
from .gateway import Gateway
from .kb import KB
from . import agents as A, llm, network as N
ROOT=Path(__file__).resolve().parent.parent
def run(scenario,backend="extractive",inject=(),out="runs/latest",quiet=False,rules=None):
    sc=yaml.safe_load(Path(scenario).read_text()); out=ROOT/out; out.mkdir(parents=True,exist_ok=True)
    now={"t":0}; audit=Audit(out/"audit.jsonl",lambda:now["t"])
    kb=KB(); model=llm.make(backend); gw=Gateway(rules) if rules else Gateway()
    paths=N.default_paths(); fm,mae=N.forecast_model()
    agents={k:A.Agent(k,kb,model,audit,sc.get("context_docs")) for k in A.ROLES}
    audit.log("run_start","system",scenario=sc["id"],backend=model.name,chunks=len(kb.recs),rules=len(gw.rules),forecast_mae=round(mae,4))
    ev=list(sc["events"]); acts=dict(sc["actions"])
    for j in inject:
        x=sc["judge_injections"][j]; ev.append(dict(x,id=j))
        for p in x["proposals"]: acts[p]=sc["judge_injections"][p]
    ev.sort(key=lambda e:e["t"])
    protected=(); rec={"scenario":{k:sc[k] for k in("id","title","note")},"backend":model.name,"events":[],"gaps_triggered":{},"forecast_mae":round(mae,4)}
    bus=[]; extra=0
    for e in ev:
        now["t"]=e["t"]; audit.log("event_released","scenario",event=e["id"],recipients=e["to"],text=e["text"])
        for p in e.get("effects",{}).get("down",[]): paths[p].up=False
        for p,f in e.get("effects",{}).get("degrade",{}).items(): paths[p].capacity*=f
        ass=[]; props=[dict(acts[p],id=p) for p in e.get("proposals",[])]
        for k in e["to"]:
            a=agents[k].assess(e,bus,props); ass.append(a)
            for c in a["claims"]: bus.append(f"{a['name']}: {c['claim'][:120]}")
        dec=[]
        for pid in e.get("proposals",[]):
            act=dict(acts[pid],id=pid); v=gw.evaluate(act)
            audit.log("gateway_decision","gateway",action=pid,description=act["description"],verdict=v["verdict"],legal_status=v["legal_status"],rules=v["rules"],gaps=v["gaps"],citations=v["citations"])
            hd=sc.get("human_decisions",{}).get(pid); applied=False
            if v["verdict"]=="ALLOW": applied=True
            elif v["verdict"]=="HOLD":
                if hd:
                    applied=hd["decision"].startswith("approve")
                    audit.log("human_decision",hd["by"],action=pid,decision=hd["decision"],note=hd["note"])
                else: audit.log("human_pending","gateway",action=pid,approver=v["approver"])
            if applied and act["type"]=="prioritise": protected=tuple(act["classes"])
            if applied and pid=="A9": protected=tuple(set(protected)|{"payments"})
            if applied and pid=="A3": extra=paths["NORTH"].capacity
            if v["verdict"]=="HOLD" and v["legal_status"]!="clear":
                ad=agents["adviser"].assess(dict(e,text="Local texts are "+v["legal_status"]+" on this action. "+act["description"]),bus,[act]); ad["for_action"]=pid; ass.append(ad)
            for g in v["gaps"]: rec["gaps_triggered"].setdefault(g,[]).append({"event":e["id"],"action":pid})
            dec.append(dict(v,description=act["description"],human=hd,applied=applied))
        pos={a["agent"]:a["position"] for a in ass if a["actions"]}
        split=bool({"support"}&set(pos.values()) and {"oppose"}&set(pos.values()))
        if pos: audit.log("coordination","coordinator",positions=pos,disagreement=split)
        base=sum(p.capacity for p in paths.values() if p.up and p.id!="NORTH")+extra
        served,cap=N.allocate(paths,protected,available=base)
        audit.log("network_state","netops",capacity=round(cap),served=served,protected=list(protected))
        rec["events"].append({"id":e["id"],"t":e["t"],"text":e["text"],"to":e["to"],"assessments":ass,"decisions":dec,"positions":pos,"disagreement":split,"capacity":round(cap),"served":served})
        if not quiet: print(f"T+{e['t']:>3} {e['id']:<3} agents={len(ass)} verified={sum(len(a['claims']) for a in ass)} rejected={sum(a['rejected'] for a in ass)} decisions={[d['action']+':'+d['verdict'] for d in dec]}",flush=True)
    ok,bad=verify(out/"audit.jsonl"); audit.log("run_end","system",chain_ok_before_end=ok)
    rec["audit"]={"entries":audit.n,"head":audit.prev,"verified":ok}
    (out/"run.json").write_text(json.dumps(rec,indent=1,ensure_ascii=False))
    return rec
if __name__=="__main__":
    p=argparse.ArgumentParser(); p.add_argument("--scenario",default=str(ROOT/"scenarios/dual_cable_loss.yaml")); p.add_argument("--backend",default="extractive")
    p.add_argument("--inject",action="append",default=[]); p.add_argument("--rules"); p.add_argument("--out",default="runs/latest"); a=p.parse_args()
    r=run(a.scenario,a.backend,a.inject,a.out,rules=a.rules); print(json.dumps(r["audit"]),"gaps:",sorted(r["gaps_triggered"]))
