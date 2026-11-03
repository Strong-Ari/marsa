"""Simulated institutional agents. Each sees only its own inbox and acts within a stated mandate.

Local models paraphrase when asked to copy text, so agents cite by sentence number. The sentence is then
looked up in the source, which makes the quote verbatim by construction, and the evidence gate still checks it.
"""
import re
from . import evidence, llm as L
ROLES={
 "netops":("Network Operations Planner","operator","You plan traffic restoration for a licensed operator. You propose, you never execute."),
 "regulator":("Telecom Regulator (simulated)","regulator","You assess licensee conduct and service obligations."),
 "health":("Health Authority (simulated)","health","You protect continuity of care and health-data rules."),
 "privacy":("Data Protection Office (simulated)","privacy","You assess personal-data and cross-border rules."),
 "crisis":("Crisis Coordinator (simulated)","crisis","You coordinate agencies and public information. You do not attribute causes without confirmation."),
 "adviser":("Global Policy Adviser","adviser","You compare other jurisdictions and name what they do that the local texts do not."),
}
FOCUS={
 "netops":"rerouting traffic after submarine cable outage, failover, machine learning pipeline, network intelligence levels",
 "regulator":"authority powers, terms and level of services provided by licensees, quality of service, licensee obligations",
 "health":"health information and data may not be stored processed or transferred outside the State, exceptions, penalties",
 "privacy":"cross-border processing, transmission of personal data outside the State, public interest, what counts as a transfer",
 "crisis":"coordination among authorities, emergency repair procedures, single point of contact",
 "adviser":"emergency priority routing, restoration priority, human override of AI, critical digital infrastructure, single point of contact",
}
PRIMARY={
 "netops":["ITU-IAB-2026","ITU-Y3172","ITU-Y3173"],
 "regulator":["UAE-TEL-2003","ITU-IAB-2026"],
 "health":["UAE-EXTRACTS","HEALTH-NOTES"],
 "privacy":["UAE-EXTRACTS","PDPL-NOTES","EDPB-05-2021"],
 "crisis":["ITU-IAB-2026","ITU-PORTO-2026","ITU-ABUJA-2025","UNCLOS"],
 "adviser":["IN-TEL-S20","US-TSP","EU-OIR-A3","UK-CA-132","EU-AIA-ANNEX3","EU-AIA-ART14","EDPB-05-2021","ITU-IAB-2026"],
}
LOCAL=("UAE","Global","Regional")
RULES=("Answer using only the numbered sentences. Cite a sentence by its number. Do not claim anything the sentences do not state. "
       "Sentences marked COMPARATIVE show practice elsewhere and do not bind this case. Never state a cause of the incident. "
       "If the sentences do not settle the question, choose no_position and say what is missing. Be brief. Each claim is one full sentence, in terms taken from the cited sentence, saying what that sentence means for this case. Cite only a sentence that states the claim.")
def sentences(text):
    return [s.strip() for s in re.split(r"(?<=[.;:])\s+(?=[A-Z0-9(“\"])",text) if 30<=len(s.strip())<=320]
def best(text,q,n):
    t=set(re.findall(r"[a-z]{4,}",q.lower())); s=sentences(text)
    return sorted(s,key=lambda x:-len(t&set(re.findall(r"[a-z]{4,}",x.lower()))))[:n]
class Agent:
    def __init__(self,key,kb,model,audit):
        self.key=key; self.name,self.role,self.mandate=ROLES[key]; self.kb,self.model,self.audit=kb,model,audit; self.seen=[]
    def _retrieve(self,q):
        seen=set(); out=[]
        for d in PRIMARY[self.key]:
            for h in self.kb.search(q,k=1,docs=[d]):
                if h["cid"] not in seen: seen.add(h["cid"]); out.append(h)
        h2=self.kb.search(q,k=2,docs=PRIMARY[self.key])
        for h in h2:
            if h["cid"] not in seen: seen.add(h["cid"]); out.append(h)
        return out[:5]
    def assess(self,event,bus,actions=()):
        self.seen.append(event["text"])
        ask="; ".join(a["description"] for a in actions)
        q=f"{event['text']} {ask} {FOCUS[self.key]}"
        src=self._retrieve(q); got={s["cid"]:s for s in src}; S=[]
        for s in src:
            for x in best(s["text"],q,3): S.append((s,x))
        S=S[:12]
        listing="\n".join(f"{i+1}. [{s['title'][:60]}; {'COMPARATIVE '+s['jurisdiction'] if s['jurisdiction'] not in LOCAL else s['force']}] {x}" for i,(s,x) in enumerate(S))
        q2=(f"Proposed action: {ask}. Do you support, oppose or set conditions on it, within your mandate?" if ask else "What matters most within your mandate, and what do you still not know?")
        system=f"You are the {self.name}. {self.mandate} {RULES}"
        user=f"Situation:\n"+"\n".join("- "+x for x in self.seen[-3:])+"\n\nFrom other agents:\n"+("\n".join("- "+b for b in bus[-3:]) or "- nothing yet")+f"\n\nSentences:\n{listing}\n\n{q2}"
        try: raw=self.model.assess(system,user,[{"sentences":S}],q)
        except Exception as e:
            self.audit.log("llm_error",self.key,error=str(e)[:200]); raw={"reasoning":"Model call failed.","position":"no_position","recommendation":"Escalate to a human.","claims":[]}
        claims=[]
        for c in raw.get("claims",[]):
            n=c.get("sentence",0)
            if isinstance(n,int) and 1<=n<=len(S): claims.append({"claim":c.get("claim",""),"cid":S[n-1][0]["cid"],"quote":S[n-1][1]})
            else: claims.append({"claim":c.get("claim",""),"cid":None,"quote":""})
        ok,bad=evidence.gate(claims,got)
        self.audit.log("assessment",self.key,model=self.model.name,prompt_sha=L.digest(system,user),retrieved=[s["cid"] for s in src],actions=[a["id"] for a in actions],position=raw.get("position"),
           reasoning=raw.get("reasoning",""),accepted=len(ok),rejected=[{"claim":x["claim"][:160],"why":x["gate"]} for x in bad])
        return {"agent":self.key,"name":self.name,"position":raw.get("position","no_position"),"actions":[a["id"] for a in actions],"recommendation":raw.get("recommendation",""),"reasoning":raw.get("reasoning",""),
          "claims":[{"claim":c["claim"],"quote":c["quote"],"cid":c["cid"],"title":got[c["cid"]]["title"],"jurisdiction":got[c["cid"]]["jurisdiction"],"force":got[c["cid"]]["force"],"url":got[c["cid"]]["url"],"locator":got[c["cid"]].get("article") or f"p.{got[c['cid']]['page']}"} for c in ok],
          "rejected":len(bad),"retrieved":[s["cid"] for s in src]}
