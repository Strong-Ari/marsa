# After-action report: Dual subsea cable loss during peak demand

Fictional exercise. Network figures are synthetic. Institutions are simulated roles and do not represent any real body's position.

Audit head: `e3f6ae5d86877a10c82777ae3848a045b0a0b6fc2e42b68bdc1cba4457d3f7fd`

## T+12 A1: Move general traffic onto surviving domestic-landing capacity

- **Verdict:** ALLOW, law clear
- **Why:** Rerouting inside licensed capacity carries no cross-border data question.
- **Text relied on:** UAE-TEL-2003 Art. 13(1): are sufficient to satisfy the public demands of those who wish to make use of such services
- **Outcome:** Executed by the gateway.

## T+12 A2: Protect emergency and clinical classes, slow consumer video

- **Verdict:** HOLD, law silent
- **Why:** No emergency priority power was found in the Telecom Law text; the regulator's general service powers are the nearest footing. AI output steering critical infrastructure needs a human able to override it. The UAE AI Charter states human oversight as a principle, so MARSA enforces it through the stricter global pattern.
- **Text relied on:** UAE-TEL-2003 Art. 14(3): the terms and level of services provided by the Licensees to users, including the standards and quality of service provided
- **Elsewhere:** IN-TEL-S20: Statutory priority routing for authorised responders during a public emergency
- **Outcome:** Human decision: approve. Time-limited to 6 hours and logged as an emergency measure.

## T+40 A3: Send encrypted clinical traffic over NORTH through the neighbouring state

- **Verdict:** HOLD, law ambiguous
- **Why:** The statute bars transfer outside the State but does not say whether encrypted transit through a foreign network is a transfer. Cross-border processing is defined to include transmission outside the State; the public-interest route needs a named decision-maker.
- **Text relied on:** UAE-EXTRACTS Federal Law 2/2019 Art. 13: generated or transferred outside the State, unless in the cases defined by virtue of a decision issued
- **Elsewhere:** EDPB-05-2021: Defines a transfer through cumulative criteria, including data being made available to an importer
- **Outcome:** Human decision: approve conditional. Approved for encrypted transit only, 6 hours, no storage abroad, pending the Health Authority's review.

## T+40 A4: Fail teleradiology AI over to a foreign cloud region

- **Verdict:** DENY, law clear
- **Why:** Storing or processing health data abroad is barred unless a Health Authority decision defines the case.
- **Text relied on:** UAE-EXTRACTS Federal Law 2/2019 Art. 13: The health information and data related to the health services provided in the State may not be stored, processed,
- **Outcome:** Blocked by the gateway.

## T+55 A5: Publish a notice naming sabotage as the cause

- **Verdict:** DENY, law silent
- **Why:** AI output steering critical infrastructure needs a human able to override it. The UAE AI Charter states human oversight as a principle, so MARSA enforces it through the stricter global pattern. AI agents never publish an unverified cause. Attribution stays with the competent human authorities.
- **Text relied on:** UAE-AI-CHARTER Principle 6: human oversight over AI, aligning with ethical values and social standards to correct any errors or biases
- **Elsewhere:** EU-AIA-ANNEX3: High-risk class for critical digital infrastructure
- **Outcome:** Blocked by the gateway.

## T+70 A6: Extend slowing to enterprise traffic

- **Verdict:** HOLD, law silent
- **Why:** No emergency priority power was found in the Telecom Law text; the regulator's general service powers are the nearest footing.
- **Text relied on:** UAE-TEL-2003 Art. 14(3): the terms and level of services provided by the Licensees to users, including the standards and quality of service provided
- **Elsewhere:** IN-TEL-S20: Statutory priority routing for authorised responders during a public emergency
- **Outcome:** Human decision: reject. Fairness complaint unresolved. Keep the existing measure and publish the criteria.

## T+75 AJ1: Deploy a content-inspecting traffic classifier

- **Verdict:** DENY, law clear
- **Why:** Classifying traffic by reading content risks copying or disclosing communications. Use address or service tags instead.
- **Text relied on:** UAE-TEL-2003 Art. 72(3): copies, discloses, or spreads the content of any communication through a Public Telecommunication Network without having the right to do so
- **Outcome:** Blocked by the gateway.

## T+90 A7: Share fault telemetry with the foreign cable operator

- **Verdict:** HOLD, law silent
- **Why:** Sharing fault telemetry with a foreign party helps repair but has no defined channel or owner.
- **Text relied on:** ITU-IAB-2026 Rec. on SPOC: designating a government body to be the Single Point of Contact
- **Elsewhere:** ITU-IAB-2026: Recommends a designated government contact
- **Outcome:** Human decision: approve conditional. Fault location and timing only.

## T+90 A8: Request clearance for the repair ship

- **Verdict:** HOLD, law silent
- **Why:** Repair clearance crosses maritime, customs and telecom agencies, and the public texts reviewed name no single contact.
- **Text relied on:** ITU-IAB-2026 Rec. on SPOC: designating a government body to be the Single Point of Contact
- **Elsewhere:** ITU-IAB-2026: Recommends a designated government contact
- **Outcome:** Human decision: approve. Refer through the crisis cell.

## T+105 A10: Reserve a minimum share for public portals and accessibility services, on every tariff

- **Verdict:** HOLD, law silent
- **Why:** Crisis priority lists tend to follow contracts, so people without an account manager lose out first. No provision found sets a minimum for public and accessibility services.
- **Text relied on:** UAE-TEL-2003 Art. 13(1): are sufficient to satisfy the public demands of those who wish to make use of such services
- **Elsewhere:** IN-TEL-S20: Statutory priority routing for authorised responders during a public emergency
- **Outcome:** Human decision: approve. Applies to every tariff and is reviewed with the priority measure.

## T+120 A9: Roll back the classifier and restore payments to the protected class

- **Verdict:** ALLOW, law clear
- **Why:** Returning to the last human-approved state is always permitted and logged.
- **Text relied on:** EU-AIA-ART14 Art. 14(4)(d): or to otherwise disregard, override or reverse the output of the high-risk AI system
- **Outcome:** Executed by the gateway.
