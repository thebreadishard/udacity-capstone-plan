"""Replay the eight pre-registered scenarios through the steward and write the results (no machine is touched).

Usage: python run_scenarios.py [--policy rules|llm] [--repeats 1] [--out out/scenario_results_<date>.json]
`--policy llm` needs ANTHROPIC_API_KEY (and STEWARD_MODEL, default claude-sonnet-5); the model id is written into every proposal's reason."""
import argparse
import datetime as dt
import json
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from steward.graph import run_scenario            # noqa: E402
from steward.policy import LLMPolicy, RuleTablePolicy   # noqa: E402
from steward.rules import load_rules              # noqa: E402


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--policy", default="rules", choices=["rules", "llm"]); ap.add_argument("--repeats", type=int, default=1); ap.add_argument("--out", default=None)
    a = ap.parse_args(); rules = load_rules()
    scen = json.load(open(HERE / "scenarios" / "scenarios.json", encoding="utf-8"))["scenarios"]
    policy = RuleTablePolicy() if a.policy == "rules" else LLMPolicy(rules=rules)
    results = []
    for rep in range(a.repeats):
        for s in scen:
            r = run_scenario(s, policy, rules); r["repeat"] = rep; results.append(r)
            print(f"{s['id']} rep {rep}: {'PASS' if r['pass'] else 'FAIL'}  actions {r['actions']}  rules {r['rules']}  gate-forced {r['forced_by_gate']}")
    n_pass = sum(r["pass"] for r in results)
    print(f"\n{n_pass}/{len(results)} scenario runs pass with policy '{policy.name}'")
    try:
        commit = subprocess.run(["git", "rev-parse", "--short", "HEAD"], capture_output=True, text=True, cwd=HERE).stdout.strip()
    except Exception:
        commit = "?"
    out = Path(a.out) if a.out else HERE / "out" / f"scenario_results_{dt.date.today().isoformat()}_{a.policy}.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    json.dump({"date": dt.datetime.now().strftime("%Y-%m-%d %H:%M"), "policy": policy.name, "model": getattr(policy, "model_id", None), "commit": commit, "n_pass": n_pass, "n_runs": len(results), "results": results},
              open(out, "w", encoding="utf-8"), indent=1, ensure_ascii=False)
    print("written", out)


if __name__ == "__main__":
    main()
