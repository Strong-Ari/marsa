# MARSA

Policy-gated multi-agent crisis response for telecom networks. Built for the ITU AI for Good Lab Hackathon: United Arab Emirates.

When subsea cables fail, AI can replan traffic in minutes. MARSA makes sure it stays within legal authority: agents retrieve and propose, deterministic code decides, and people approve whatever the law leaves open.

## How it works

1. **Knowledge base.** Laws, standards and strategies, with legal-force metadata and page or article locators. Hybrid dense and BM25 retrieval, based on the ITU reference pipeline.
2. **Agents.** Simulated roles (operator, regulator, health, data protection, crisis) receive different events at different times.
3. **Evidence gate.** A claim survives only if its quote is verbatim in a chunk the agent retrieved.
4. **Policy gateway.** Eleven rules return ALLOW, HOLD or DENY with the provision and the approver. Unknown actions fail safe to HOLD.
5. **Audit log.** Every prompt hash, retrieval, rejection, decision and human approval sits in a SHA-256 hash chain.

The solution follows the ITU-T Y.3172 pipeline: the P node holds the evidence gate, gateway and human approval.

## Run it

```bash
pip install -r requirements.txt
python -m marsa.validate                    # check every legal citation verbatim
python -m pytest -q tests
python -m marsa.run                         # no model needed
python -m marsa.run --inject J1 --out runs/injected   # add the judge's event
python -m marsa.run --backend "gguf:/path/model.gguf"
python -m marsa.run --backend "openai:http://localhost:11434/v1|qwen2.5:14b"   # Ollama or the ITU Sandbox
PYTHONPATH=. python eval/run_eval.py
python -m marsa.viewer                      # build the Incident Room page
```

`kb/chunks.jsonl` is included. To rebuild the index, place source files in `corpus/raw` and `corpus/reference_docs` (URLs and SHA-256 in `kb/inventory.json`) and run `python -m marsa.kb build`.

## Limits

- The network, traffic figures and scenario are synthetic. Institutions are simulated and do not represent any real body.
- The UAE Telecom Law text is a 2005 English edition, later amended, and the Arabic text prevails. Health and data laws are short verbatim extracts.
- The evidence gate proves a quote exists, not that it is relevant. Human reviewers remain necessary.
- A zero term count covers the indexed text only. It does not rule out unpublished instruments.
- This is not legal advice.
