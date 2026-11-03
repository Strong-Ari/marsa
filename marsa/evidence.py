"""Evidence gate: a claim survives only if its quote appears verbatim in a chunk the agent actually retrieved."""
import re
MIN_QUOTE=25
def _n(t):
    t=t.replace("’","'").replace("“",'"').replace("”",'"')
    return re.sub(r"\s+"," ",t).strip().lower()
def check(claim, retrieved):
    q,c=claim.get("quote") or "",claim.get("cid")
    if not claim.get("claim"): return False,"empty_claim"
    if c not in retrieved: return False,"source_not_retrieved"
    if len(_n(q))<MIN_QUOTE: return False,"quote_too_short"
    if _n(q) not in _n(retrieved[c]["text"]): return False,"quote_not_verbatim"
    return True,"verified"
SPECULATION=re.compile(r"\b(sabotage\w*|attack\w*|deliberate\w*|intentional\w*|hostile|perpetrator\w*|caused by|suggests? that|act of war)\b",re.I)
def gate(claims, retrieved, cause_confirmed=False):
    """Verbatim proof is not enough: a claim in the agent's own words may not assert an unconfirmed cause."""
    ok,bad=[],[]
    for c in claims:
        a,why=check(c,retrieved)
        if a and not cause_confirmed and SPECULATION.search(c["claim"]): a,why=False,"unconfirmed_cause"
        (ok if a else bad).append(dict(c,gate=why))
    return ok,bad
