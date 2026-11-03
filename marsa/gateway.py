"""Deterministic policy gateway. Agents propose; only this code decides what may reach the network."""
from pathlib import Path
import yaml
ROOT=Path(__file__).resolve().parent.parent
ORDER={"ALLOW":0,"HOLD":1,"DENY":2}
LEVEL={"low":0,"medium":1,"high":2}
STATUS={"clear":0,"ambiguous":1,"silent":2}
class Gateway:
    def __init__(self,path=ROOT/"rules"/"policy_rules.yaml"):
        self.rules=yaml.safe_load(Path(path).read_text())["rules"]
    @staticmethod
    def _match(when,a):
        for k,v in when.items():
            if k=="foreign_hop":
                if bool([h for h in a.get("hops",[]) if h not in("UAE","INT-WATERS","SPACE")])!=v: return False
            elif k=="impact_at_least":
                if LEVEL[a.get("impact","low")]<LEVEL[v]: return False
            elif isinstance(v,list):
                x=a.get(k)
                if isinstance(x,list):
                    if not set(x)&set(v): return False
                elif x not in v: return False
            elif a.get(k)!=v: return False
        return True
    def evaluate(self,a):
        hits=[r for r in self.rules if self._match(r.get("when",{}),a)]
        if not hits:
            return {"action":a["id"],"verdict":"HOLD","legal_status":"silent","rules":[],"approver":["human_duty_officer"],"citations":[],"gaps":[],"reasons":["No rule covers this action, so it cannot run automatically."]}
        return {"action":a["id"],"verdict":max(hits,key=lambda r:ORDER[r["verdict"]])["verdict"],
          "legal_status":max((r.get("legal_status","clear") for r in hits),key=lambda s:STATUS[s]),
          "rules":[r["id"] for r in hits],"approver":sorted({x for r in hits for x in r.get("approver",[])}),
          "citations":[c for r in hits for c in r.get("citations",[])],"gaps":sorted({g for r in hits for g in r.get("gaps",[])}),
          "reasons":[r["reason"] for r in hits]}
