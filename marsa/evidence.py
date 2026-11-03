"""Evidence gate: a claim survives only if its quote appears verbatim in a chunk the agent actually retrieved."""
import re
MIN_QUOTE=25
def _n(t):
    t=t.replace("’","'").replace("“",'"').replace("”",'"')
    return re.sub(r"\s+"," ",t).strip().lower()
def check(claim, retrieved):
    q,c=claim.get("quote") or "",claim.get("cid")
    if len((claim.get("claim") or "").strip())<20: return False,"empty_claim"
    if c not in retrieved: return False,"source_not_retrieved"
    if len(_n(q))<MIN_QUOTE: return False,"quote_too_short"
    if _n(q) not in _n(retrieved[c]["text"]): return False,"quote_not_verbatim"
    return True,"verified"
SPECULATION=re.compile(r"\b(sabotage\w*|attack\w*|deliberate\w*|intentional\w*|hostile|perpetrator\w*|caused by|suggests? that|act of war)\b",re.I)
STOP=set("this that with from have been were will would should could their there which about under into such than then them they these those also only other more most must does shall sentence statute proposed action local texts text provide provides stated".split())
def words(t): return {w for w in re.findall(r"[a-z]{4,}",t.lower()) if w not in STOP}
def supports(claim,quote):
    """Cheap entailment proxy: the claim must reuse the cited sentence's own terms, so a claim cannot be pinned on an unrelated quote."""
    c,q=words(claim),words(quote)
    return len(c&q)>=2 and len(c&q)/max(len(c),1)>=0.25
def gate(claims, retrieved, cause_confirmed=False):
    """Verbatim proof is not enough: a claim in the agent's own words may not assert an unconfirmed cause."""
    ok,bad=[],[]
    for c in claims:
        a,why=check(c,retrieved)
        if a and not supports(c["claim"],c["quote"]): a,why=False,"claim_not_supported_by_quote"
        if a and not cause_confirmed and SPECULATION.search(c["claim"]): a,why=False,"unconfirmed_cause"
        (ok if a else bad).append(dict(c,gate=why))
    return ok,bad
