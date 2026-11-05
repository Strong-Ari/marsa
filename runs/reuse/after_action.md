# After-action report: Reuse by a health ministry, same engine with a new context

Fictional exercise. Institutions are simulated roles. Only the scenario, the rule pack and the context documents change. The engine code is the same.

Audit head: `ebbd982258e8f68eaa7baeb6d4c82438f5e4da31a063b77b213fc8b2fd639acf`

## T+0 H_A1: Fail teleradiology over to the vendor's foreign region

- **Verdict:** DENY, law clear
- **Why:** Storing or processing health data abroad is barred unless a Health Authority decision defines the case.
- **Text relied on:** UAE-EXTRACTS Federal Law 2/2019 Art. 13: The health information and data related to the health services provided in the State may not be stored, processed,
- **Outcome:** Blocked by the gateway.

## T+20 H_A2: Keep the intensive care link on encrypted transit abroad

- **Verdict:** HOLD, law ambiguous
- **Why:** The statute bars transfer outside the State but does not say whether encrypted transit through a foreign network is a transfer. Cross-border processing is defined to include transmission outside the State; the public-interest route needs a named decision-maker.
- **Text relied on:** UAE-EXTRACTS Federal Law 2/2019 Art. 13: generated or transferred outside the State, unless in the cases defined by virtue of a decision issued
- **Elsewhere:** EDPB-05-2021: Defines a transfer through cumulative criteria, including data being made available to an importer
- **Outcome:** Human decision: approve conditional. Encrypted transit only, no storage abroad, reviewed by the Health Authority.

## T+45 H_A3: Let the AI reorder scans with no radiologist review

- **Verdict:** HOLD, law silent
- **Why:** AI output steering critical infrastructure needs a human able to override it. The UAE AI Charter states human oversight as a principle, so MARSA enforces it through the stricter global pattern. A clinical ordering decision needs a clinician. The UAE AI Charter states human oversight as a principle, and no rule found sets who reviews AI triage.
- **Text relied on:** UAE-AI-CHARTER Principle 6: human oversight over AI, aligning with ethical values and social standards to correct any errors or biases
- **Elsewhere:** EU-AIA-ANNEX3: High-risk class for critical digital infrastructure
- **Outcome:** Human decision: reject. A radiologist stays in the loop. The AI may suggest an order but not set it.

## T+70 H_A4: Give the patient the decision record for her case

- **Verdict:** ALLOW, law clear
- **Why:** A person may be told why a decision affected them. The audit log supplies the record.
- **Text relied on:** UAE-EXTRACTS Decree-Law 45/2021 Art. 18: The Data Subject shall have the right to object to any decisions resulting from automated processing, including profiling.
- **Outcome:** Executed by the gateway.
