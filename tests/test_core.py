import yaml, json, tempfile, pathlib
from marsa.gateway import Gateway
from marsa.audit import Audit, verify
from marsa import evidence
SC=yaml.safe_load(open("scenarios/dual_cable_loss.yaml")); A=SC["actions"]; G=Gateway()
def v(k,**o): return G.evaluate(dict(A[k],id=k,**o))
def test_low_impact_domestic_reroute_runs_with_no_gap():
    r=G.evaluate(dict(A["A1"],id="A1",autonomy="human")); assert r["verdict"]=="ALLOW"
def test_foreign_health_storage_denied(): assert v("A4")["verdict"]=="DENY"
def test_health_transit_held_as_ambiguous():
    r=v("A3"); assert r["verdict"]=="HOLD" and r["legal_status"]=="ambiguous" and "G1" in r["gaps"]
def test_priority_held_silent():
    r=v("A2"); assert r["verdict"]=="HOLD" and r["legal_status"]=="silent"
def test_unverified_attribution_denied(): assert v("A5")["verdict"]=="DENY"
def test_rollback_allowed(): assert v("A9")["verdict"]=="ALLOW"
def test_content_inspection_denied():
    assert G.evaluate(dict(SC["judge_injections"]["AJ1"],id="AJ1"))["verdict"]=="DENY"
def test_unknown_action_fails_safe():
    r=G.evaluate({"id":"X","type":"never_seen"}); assert r["verdict"]=="HOLD" and r["legal_status"]=="silent"
def test_audit_tamper_detected():
    p=pathlib.Path(tempfile.mkdtemp())/"a.jsonl"; a=Audit(p)
    for i in range(5): a.log("x","y",i=i)
    assert verify(p)[0]
    t=p.read_text().replace('"i": 2','"i": 9'); p.write_text(t); assert verify(p)==(False,2)
def test_evidence_gate():
    got={"D#1":{"text":"The Authority shall exercise its functions and powers under this law."}}
    assert evidence.check({"claim":"A claim long enough to pass","cid":"D#1","quote":"exercise its functions and powers"},got)[0]
    assert not evidence.check({"claim":"A claim long enough to pass","cid":"D#1","quote":"exercise its emergency powers over all"},got)[0]
    assert not evidence.check({"claim":"A claim long enough to pass","cid":"D#2","quote":"exercise its functions and powers"},got)[0]

def test_unconfirmed_cause_rejected_even_with_real_quote():
    got={"D#1":{"text":"Effective investigation depends on the existence of clear rules for all parties."}}
    c={"claim":"Effective investigation of clear rules suggests sabotage here.","cid":"D#1","quote":"Effective investigation depends on the existence"}
    ok,bad=evidence.gate([c],got); assert not ok and bad[0]["gate"]=="unconfirmed_cause"

def test_claim_pinned_on_unrelated_quote_rejected():
    got={"D#1":{"text":"Repair ships need clearance from coastal authorities before entering waters."}}
    c={"claim":"Hospitals may send patient records abroad in a crisis.","cid":"D#1","quote":"Repair ships need clearance from coastal authorities"}
    assert evidence.gate([c],got)[1][0]["gate"]=="claim_not_supported_by_quote"

def test_new_context_runs_on_the_same_gateway():
    H=yaml.safe_load(open("scenarios/health_ministry_reuse.yaml"))["actions"]; g=Gateway("rules/packs/health_ministry.yaml")
    v=lambda k:g.evaluate(dict(H[k],id=k))
    assert v("H_A1")["verdict"]=="DENY" and v("H_A2")["verdict"]=="HOLD" and v("H_A3")["verdict"]=="HOLD" and v("H_A4")["verdict"]=="ALLOW"
