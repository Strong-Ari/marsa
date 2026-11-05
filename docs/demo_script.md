# Demo video script (max 7 minutes)

Required for shortlisted teams. Show the Incident Room page and a terminal.

1. **Setup, 45 s.** Show the laptop specs, `python -m marsa.validate` and `pytest`. Say that the network is synthetic and institutions are simulated.
2. **Main functions, 90 s.** Walk the figure: agents propose, evidence gate, policy gateway, human approval, audit chain.
3. **Scenario, expected outcome against real outcome, 3 min.**
   - T+12: general reroute expected ALLOW, priority expected HOLD. Show both.
   - T+40: encrypted transit expected HOLD as ambiguous, foreign cloud expected DENY. Show the cited Article 13 text and gap G1.
   - T+55: sabotage notice expected DENY.
   - T+120: classifier error, rollback expected ALLOW.
4. **Judge's event, 45 s.** Run `--inject J1` and show the DENY citing Telecom Law Art. 72(3).
5. **Tamper test, 30 s.** Edit one line of `audit.jsonl`, run verification, and show the chain break.
6. **Gaps, 40 s.** G1, G3, the global comparison and the proposed regulatory-policy function for Y.3172.
