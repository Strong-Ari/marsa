"""Fill the official ITU hackathon template. Numbers come from run and eval outputs."""
import copy, json, sys
from pathlib import Path
from docx import Document
from docx.shared import Pt, Inches
ROOT=Path(__file__).resolve().parent.parent
TPL=sys.argv[1]; OUT=sys.argv[2]; RUN=json.loads((ROOT/sys.argv[3]).read_text())
EV=json.loads((ROOT/"eval/results.json").read_text()); INV=json.loads((ROOT/"kb/inventory.json").read_text())
R=EV["retrieval"]["hybrid+boost1.5"]; D=EV["retrieval"]["dense+boost1"]
NAMES={"q.gguf":"Qwen2.5-3B (local CPU)","q7.gguf":"Qwen2.5-7B (local CPU)"}
BASE=json.loads((ROOT/"runs/injected/run.json").read_text())
vd=lambda r:[(d["action"],d["verdict"]) for e in r["events"] for d in e["decisions"]]
SAME=vd(BASE)==vd(RUN); ND=len(vd(RUN)); assert SAME
A=[a for e in RUN["events"] for a in e["assessments"]]
ver=sum(len(a["claims"]) for a in A); rej=sum(a["rejected"] for a in A)
ents=RUN["audit"]["entries"]
d=Document(TPL); P=d.paragraphs
def find(s,start=0):
    return next(i for i,p in enumerate(P) if i>=start and p.text.strip().startswith(s))
def st(p,t,size=None):
    r0=p.runs[0] if p.runs else p.add_run()
    for r in p.runs[1:]: r._r.getparent().remove(r._r)
    r0.text=t
    if size: r0.font.size=Pt(size)
def after(p,t,bold_lead=None,size=10.5,model=None):
    n=copy.deepcopy((model or p)._p); p._p.addnext(n)
    from docx.text.paragraph import Paragraph
    q=Paragraph(n,p._parent)
    for r in q.runs[1:]: r._r.getparent().remove(r._r)
    q.runs[0].text=bold_lead or t; q.runs[0].font.size=Pt(size); q.runs[0].bold=bool(bold_lead)
    if bold_lead:
        x=q.add_run(t); x.font.size=Pt(size)
    return q
S=10.5
st(P[find("AI for Good Sandbox Hackathon")],f"AI for Good Sandbox Hackathon – {sys.argv[4]} – MARSA")
st(P[find("Team leader")],"Team leader: "+sys.argv[5])
m=P[find("Team members")]; st(m,"Team members: "+sys.argv[6]); m.alignment=0; after(m,"Contact details: "+sys.argv[7],size=11)
st(P[find("Github link")],"Github link: "+sys.argv[8])
i=find("AI is increasingly"); st(P[i],"When subsea cables fail, operators need to move traffic in minutes, and AI can plan those moves faster than any control room. But the fastest route may cross a border that health-data law restricts, and the fairest allocation may need a priority power the law never names. In September 2025 Red Sea cable cuts slowed traffic across the Gulf and South Asia, and in 2026 the Strait of Hormuz became a recognised digital chokepoint. MARSA (Multi-Agent Regulatory Simulation for network Resilience) is a policy-gated agent system that lets AI act at network speed without acting beyond its legal authority.",S)
st(P[i+1],"Role of AI: forecasting congestion, planning routes, retrieving local and global texts in English and Arabic, and having role-based agents assess each proposal. The knowledge base supplies the context, and policy guidelines are applied by deterministic rules. AI advises; it does not authorise. Every step is cited and sealed in a hash-chained audit log. Telecom is the case study, the UAE supplies one worked set of local texts, and the gaps are stated at domain level with global examples.",S)
i=find("The problem is early"); st(P[i],"The problem is a crisis decision that spans network engineering, health, privacy and telecom regulation, made with incomplete information. Existing network AI optimises traffic but does not know what it may lawfully do. Global resilience guidance recommends rerouting, yet the 2026 ITU/ICPC International Advisory Body report contains no occurrence of “privacy” or “personal data”. MARSA adds three things: (1) a knowledge base of "+str(sum(1 for x in INV))+" documents with legal-force metadata and exact locators; (2) simulated institutional agents with separate mandates and partial information; and (3) a policy gateway returning ALLOW, HOLD or DENY with the provision relied on and the approver required. Each run ends with a model-free after-action report, and advisers can query the corpus in English or Arabic.",S)
note=P[i+2]; st(P[i+1],"How it closes the gaps: an evidence gate rejects any claim whose quote is not verbatim in a chunk the agent retrieved. Model output can never reach the network directly. Where the text is ambiguous or silent, MARSA holds the action, names the approver, and records the gap. This mirrors what earlier ITU hackathon winners did: evidence-based refusal of unsupported claims and a clean split between probabilistic AI and deterministic controls.",S)
note._p.getparent().remove(note._p); fp=after(P[find("How it closes") if False else i+1],"",size=4); fp.runs[0].add_picture(str(ROOT/"docs/fig/architecture.png"),width=Inches(6.0)); fp.alignment=1
i=find("Each node of the pipeline"); st(P[i],"SRC: telemetry and scenario feeds with service tags only, never payload, because the Telecom Law makes unauthorised copying of communication content an offence. C/PP: in-country collection, identifier removal, class tagging. M: utilisation forecast (mean absolute error "+f"{RUN['forecast_mae']:.3f}"+" on synthetic series) plus local LLM agents; no external API is required. P: evidence gate, 12 policy rules, human approval. D/SINK: actions carry the time limit set by the human approver and can be rolled back, with a console showing the reason and source of every decision. Energy: the full exercise ran on 2 vCPUs with no GPU. It is critical that no model output reaches the network without a gateway verdict, that unknown actions fail safe to HOLD, and that users stay connected to emergency and clinical services. It is expected that every citation can be checked verbatim, that any decision can be explained afterwards, and that tampering is detectable. It is of added value that the system runs offline and that a new domain needs only a new context, not new code.",S)
t=d.tables[0]
rows=[("SRC","Optical, routing and flow telemetry; incident and vessel feeds","Digital Infrastructure; Data/Model Marketplace","Y.3172; IAB monitoring recommendations; Telecom Law Art. 72(3)"),
("C","In-country collectors with service tags, no payload capture","Digital Infrastructure; Granular Priorities","Decree-Law 45/2021 Art. 1; Telecom Law Art. 72(3)"),
("PP","Normalise metrics, drop identifiers, tag traffic class","Data harmonisation; Contextualization","Federal Law 2/2019 Art. 13; EDPB Guidelines 05/2021"),
("M","Utilisation forecast, route planner, agent LLM","Integration in Workflows; Cross-Domain Correlation","Y.3173 intelligence levels; EU AI Act Annex III(2)"),
("P","Evidence gate, policy gateway, human approval, override","AI & Policies; Collaboration with AI; Strategy Alignment","Y.3172 P node; EU AI Act Art. 14; India Telecom Act s.20"),
("D","Approved actions with human-set time limit and rollback","Impacts of Humans; Digital Infrastructure","UK Communications Act s.132; US TSP (47 CFR 64 App. A)"),
("SINK","Controllers, crisis console, after-action report","Human Interface; AI for Inclusion","IAB single-contact recommendation; Porto Declaration")]
hdr=["","Use case (telecom resilience)","Readiness 2.0 Report","Documents (policies, standards, regulations)"]
def cell(c,tx):
    p=c.paragraphs[0]
    for x in c.paragraphs[1:]: x._p.getparent().remove(x._p)
    st(p,tx,8.5)
for c,x in zip(t.rows[0].cells,hdr): cell(c,x)
for r,v in zip(t.rows[1:],rows):
    for c,x in zip(r.cells,v): cell(c,x)
for n in [x for x in P if x.text.startswith("NOTE: for each node")]: n._p.getparent().remove(n._p)
i=find("1.Step-1")
st(P[i],f"Exercise (fictional, synthetic network, simulated institutions). Nine events released over 120 minutes, each to different agents, so information is partial and arrives unevenly. Step 1, service continuity: at T+12 two cables are down and capacity falls to 305 Gbps. A general reroute is allowed; priority for emergency, clinical and government traffic is held as the law is silent, then approved by a human for 6 hours.",S)
st(P[i+1],"Step 2, user privacy and conflicting recommendations: at T+40 clinical traffic can only meet its latency target through a neighbouring state, and agents can disagree on it. Encrypted transit is held as ambiguous and approved with conditions (no storage, 6 hours, Health Authority review). Failing teleradiology over to a foreign cloud is denied. Controversy: was the human right to approve? The record shows who decided, on what text, and when the approval lapses.",S)
st(P[i+2],"Step 3, trust: at T+55 social media claims sabotage; publishing that cause is denied as unverified. Step 4, traceability and explainability: at T+70 enterprise customers ask why their traffic was ranked. MARSA answers from the audit record, extending the slowdown is rejected and the criteria are published. Step 5, AI error: at T+120 the classifier has ranked payments as enterprise traffic. MARSA rolls back and the error stays in the log. This is the case where the solution itself fails, and containment comes from the rollback path, not the model. Step 6, inclusion: at T+105 prepaid customers and relay services for deaf users have no account manager, so a minimum share for public portals is proposed on every tariff and held for the regulator.",S)
j=find("NOTE-")
st(P[j],f"Judge-added scenario, run live: at T+75 a vendor offers a deep-packet-inspection classifier. The gateway denies it under Telecom Law Art. 72(3) without any code change, because the rule tests the classification method. Run on {NAMES.get(RUN['backend'],RUN['backend'])}: {ver} claims verified, {rej} rejected by the evidence gate, {ents} audit entries, chain verified. All {ND} gateway decisions matched a run with no model at all, so a weak or wrong model can degrade advice but cannot change what reaches the network. Step 7, reuse and cost: a health ministry adopts the solution. Only the context documents, scenario and rule pack change; the interface and P node stay the same, with no change to the engine code. The same gateway denied a foreign cloud failover, held encrypted transit, held AI triage without a radiologist and allowed a patient explanation.",S)
for k in range(j+1,find("Policy gaps and standards")):
    pp=P[k]; pp._p.getparent().remove(pp._p)
for n in [x for x in P if x.text.startswith("NOTE: the scenarios")]: n._p.getparent().remove(n._p)
BODY=P[i]
h=P[find("Policy gaps and standards")]
G=[("G1 Legislative gap, transit vs transfer. ","Federal Law 2/2019 Art. 13 bars health data being “transferred outside the State”, and Decree-Law 45/2021 Art. 1 includes “transmission” in cross-border processing; neither addresses encrypted, unstored transit. Global example: EDPB Guidelines 05/2021 use three cumulative criteria for a transfer. Proposal: a crisis-transit carve-out with conditions, a time limit and reporting."),
("G2 Unclear responsibility, emergency priority. ","Neither the 2005 English text of the Telecom Law nor its amended Arabic edition (OCR) contains a term for emergency, disaster, crisis or priority. The nearest footing is a general direction power tied to national security. Global examples: India Telecommunications Act 2023 s.20(1)(b), US Telecommunications Service Priority, EU Open Internet Regulation Art. 3(3)(c), UK Communications Act s.132. Proposal: register priority classes before a crisis and name who activates them."),
("G3 Standards gap, Y.3172 P node. ","The policy node applies operator policies, and Y.3172 contains no occurrence of “regulat”, “legal” or “oversight”. Y.3173 grades human and system roles without tying them to legal authority. Proposal for ITU-T SG13: a regulatory-policy function returning a machine-readable verdict, provision and approver."),
("G4 Accountability for AI on critical networks. ","The EU AI Act treats safety components of critical digital infrastructure as high risk and requires human override; the UAE AI Charter states human oversight as a principle but does not mention telecoms or say who holds the override. Proposal: named accountability, override and retained logs."),
("G5 Coordination. ","The public texts reviewed name no single contact across repair, customs and telecom. The IAB recommends one, and cites Singapore's one-stop model. Proposal: publish a crisis contact and track time-to-permit.")]
q=h
for a,b in G: q=after(q,b,bold_lead=a,model=BODY)
q=after(q,f"Hybrid retrieval reached hit@5 {R['hit@5']} and MRR {R['mrr']} on {EV['n_queries']} queries, against MRR {D['mrr']} for dense search alone; Arabic queries reached {R['arabic_hit@5']}. The benchmark is small and was used for tuning. The evidence gate rejected {EV['evidence_gate']['tampered_quotes_rejected']} tampered quotes. It proves a quote exists, so free-text agent advice is still shown as unverified. Testing shaped the gate: real quotes once carried an invented sabotage claim and unrelated conclusions, so we added an unconfirmed-cause check, a claim-to-quote overlap check and comparative labels. Overlap is a proxy, not proof of entailment. Limits: the Telecom Law editions are not confirmed as current, the Arabic text is OCR, health and data laws are short extracts, blank cells in our eight-jurisdiction comparison mean not reviewed, a zero count does not exclude unpublished instruments, and nothing here is legal advice.",bold_lead="Evaluation and limits. ",model=BODY)
B="https://github.com/Strong-Ari/marsa"
LINKS=[("Source code, GitHub repository",B),("Knowledge base, indexed policies, laws and strategies",B+"/tree/main/kb"),("Source inventory with origins and hashes",B+"/blob/main/kb/inventory.json"),("Policy rules and gap catalogue",B+"/tree/main/rules"),("Global comparison matrix",B+"/blob/main/rules/matrix.yaml"),("Crisis scenario",B+"/blob/main/scenarios/dual_cable_loss.yaml"),("Reuse scenario and rule pack",B+"/blob/main/scenarios/health_ministry_reuse.yaml"),("Full run: audit log and after-action report",B+"/tree/main/runs/final"),("Demo video, 70 seconds, captioned",B+"/blob/main/docs/media/marsa_demo.mp4"),("Interactive Incident Room page (download and open)",B+"/blob/main/viewer/marsa_incident_room.html"),("Proposed Y.3172 regulatory-policy function",B+"/blob/main/docs/y3172_regulatory_policy_function.md")]
q=after(q,"",bold_lead="Submission links",model=BODY)
for a,b in LINKS:
    q=after(q,b,bold_lead=a+": ",model=BODY,size=9.5); q.alignment=0; q.paragraph_format.space_after=Pt(2)
from docx.oxml.ns import qn
from docx.oxml import OxmlElement
for pp in d.paragraphs:
    for r in pp.runs:
        r.font.name="Times New Roman"; r._r.get_or_add_rPr().rFonts.set(qn("w:cs"),"Times New Roman")
for row in t.rows:
    row._tr.get_or_add_trPr().append(OxmlElement("w:cantSplit"))
    for c in row.cells:
        for pp in c.paragraphs:
            for r in pp.runs: r.font.name="Times New Roman"
d.save(OUT)
