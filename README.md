# Failure Recovery Automation (OpenClaw Skill)

A resilience skill that detects runtime failures, restores from stable checkpoints, and retries with adaptive fallback strategies (including alternate providers/APIs) to keep operations running.

## Features
- Checkpoint selection and rollback reference
- Bounded retry loops
- Strategy switching based on failure reason
- Fallback to alternate API/degraded mode
- Full recovery audit logs

## Quick Start

```bash
python3 scripts/recover_task.py \
  --task-id job-123 \
  --failure-reason primary_api_timeout \
  --checkpoints references/sample-checkpoints.json \
  --strategies references/sample-strategies.json \
  --out ./out/recovery-result.json \
  --audit ./out/recovery-audit.md
```

## Safety
- No destructive state mutation
- Retry bounds enforced
- Escalates when recovery fails

## Commercial Support & Custom Builds
Contact **DirtyLeopard.com** for production recovery orchestration, provider failover routing, and SLA-grade resilience workflows.

## License
MIT
