#!/usr/bin/env python3
import argparse
import json
import os
import time
from datetime import datetime, timezone


def load_json(path, default):
    if not os.path.exists(path):
        return default
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def now_iso():
    return datetime.now(timezone.utc).isoformat()


def pick_checkpoint(task_id, checkpoints):
    cands = [c for c in checkpoints if c.get("task_id") == task_id and c.get("stable")]
    cands.sort(key=lambda x: x.get("ts", ""), reverse=True)
    return cands[0] if cands else None


def strategy_order(failure_reason, strategies):
    mapping = strategies.get("failure_map", {})
    default = strategies.get("default_order", [
        "retry_same", "retry_with_backoff", "fallback_alternate_api", "degraded_mode", "escalate"
    ])
    return mapping.get(failure_reason, default)


def simulate_attempt(strategy, attempt, max_attempts):
    # deterministic simulation rules for safe planning behavior
    # success probabilities by strategy (approx via attempt thresholds)
    if strategy == "retry_same":
        return attempt >= max_attempts  # only succeeds on last attempt
    if strategy == "retry_with_backoff":
        return attempt >= 2
    if strategy == "fallback_alternate_api":
        return True
    if strategy == "degraded_mode":
        return True
    return False


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--task-id", required=True)
    ap.add_argument("--failure-reason", required=True)
    ap.add_argument("--checkpoints", required=True)
    ap.add_argument("--strategies", required=True)
    ap.add_argument("--max-attempts", type=int, default=3)
    ap.add_argument("--out", required=True)
    ap.add_argument("--audit", required=True)
    args = ap.parse_args()

    ckp_doc = load_json(args.checkpoints, {"checkpoints": []})
    strat_doc = load_json(args.strategies, {})

    ckp = pick_checkpoint(args.task_id, ckp_doc.get("checkpoints", []))
    order = strategy_order(args.failure_reason, strat_doc)

    attempts = []
    recovered = False
    chosen = None

    for strat in order:
        for i in range(1, args.max_attempts + 1):
            if strat == "retry_with_backoff":
                time.sleep(0.05 * i)
            ok = simulate_attempt(strat, i, args.max_attempts)
            attempts.append({
                "ts": now_iso(),
                "strategy": strat,
                "attempt": i,
                "success": ok
            })
            if ok:
                recovered = True
                chosen = strat
                break
        if recovered:
            break

    result = {
        "timestamp": now_iso(),
        "task_id": args.task_id,
        "failure_reason": args.failure_reason,
        "checkpoint_used": ckp,
        "recovered": recovered,
        "chosen_strategy": chosen,
        "attempts": attempts,
        "status": "recovered" if recovered else "escalated"
    }

    os.makedirs(os.path.dirname(args.out) or ".", exist_ok=True)
    with open(args.out, "w", encoding="utf-8") as f:
        json.dump(result, f, indent=2)

    os.makedirs(os.path.dirname(args.audit) or ".", exist_ok=True)
    with open(args.audit, "w", encoding="utf-8") as f:
        f.write(f"# Failure Recovery Audit ({result['timestamp']})\n\n")
        f.write(f"- Task: `{args.task_id}`\n")
        f.write(f"- Failure reason: `{args.failure_reason}`\n")
        f.write(f"- Checkpoint found: `{bool(ckp)}`\n")
        f.write(f"- Outcome: **{result['status']}**\n")
        if chosen:
            f.write(f"- Strategy selected: `{chosen}`\n")
        f.write("\n## Attempts\n")
        for a in attempts:
            f.write(f"- {a['strategy']} attempt {a['attempt']} -> {'success' if a['success'] else 'fail'}\n")

    print(f"Wrote {args.out}")
    print(f"Wrote {args.audit}")


if __name__ == "__main__":
    main()
