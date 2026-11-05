"""Answer 'why was this done?' from the audit record, in plain words and with no model."""
import json, sys
from pathlib import Path
from .after_action import build
ROOT=Path(__file__).resolve().parent.parent
def explain(run,action):
    for d in build(run):
        if d["action"]==action:
            return f"At minute {d['t']}, this action was proposed: {d['description']}. The gateway returned {d['verdict']} because: {d['why']} Text relied on: {d['provision']}. {d['outcome']}"
    return f"No record of action {action}."
if __name__=="__main__":
    print(explain(json.loads((ROOT/sys.argv[1]/"run.json").read_text()),sys.argv[2]))
