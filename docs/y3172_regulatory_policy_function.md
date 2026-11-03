# Draft input: a regulatory-policy function for the ITU-T Y.3172 policy node

Team contribution for discussion. It is not an ITU document.

## Problem

Y.3172 defines a policy node that applies policies to model output, and notes that such output may be controlled by network operator policies. The text has no occurrence of "regulat", "legal" or "oversight". Y.3173 grades human and system roles, but does not link a level to the authority needed for an action. So an ML pipeline can comply with Y.3172 and still have no way to show that a crisis action was lawful.

## Proposal

Add an optional regulatory-policy function (RPF) inside the P node. It sits between model output and the SINK and is deterministic. It takes a proposed action and returns a verdict.

| Requirement | Text |
|---|---|
| REQ-RPF-01 | The RPF should evaluate each ML-derived action before the SINK applies it. |
| REQ-RPF-02 | The RPF should return ALLOW, HOLD or DENY, with the provision relied on and the legal status: clear, ambiguous or silent. |
| REQ-RPF-03 | An action that matches no rule should return HOLD. |
| REQ-RPF-04 | HOLD should name the human or institutional approver. |
| REQ-RPF-05 | The verdict, approver and decision should be logged in a tamper-evident form. |
| REQ-RPF-06 | Rule sets should be replaceable per jurisdiction and domain without changing the ML pipeline. |

## Verdict format

```json
{
  "action": "A3",
  "verdict": "HOLD",
  "legal_status": "ambiguous",
  "rules": ["R-HEALTH-TRANSIT", "R-PERSONAL-TRANSIT"],
  "approver": ["data_office", "health_authority", "regulator"],
  "citations": [{"doc": "UAE-EXTRACTS", "locator": "Federal Law 2/2019 Art. 13", "quote": "..."}],
  "gaps": ["G1"]
}
```

A JSON Schema is in `docs/verdict.schema.json`. MARSA is a working reference implementation.

## Link to Y.3173

An operator could state which levels are permitted per action class. For example, an action with HOLD status could never run above the "human and system" capability for action implementation.

## Possible routes

ITU-T Study Group 13 for the architecture, and a Kaleidoscope paper for the evaluation. The hackathon FAQ names both kinds of follow-up.
