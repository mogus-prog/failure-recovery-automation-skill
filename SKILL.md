---
name: failure-recovery-automation
description: Detect runtime failures/interruptions, restore from checkpoints, and retry tasks with fallback strategies (including alternate providers/APIs) to maintain continuous operation in unreliable environments.
---

# Failure Recovery Automation

This skill adds resilience through checkpointed rollback + adaptive retry strategy.

## Core Flow
1. Detect failure event
2. Load latest stable checkpoint
3. Select retry strategy (same path, degraded mode, alternate API/provider)
4. Re-run task with bounded retries
5. Emit recovery audit

## Quick Start

```bash
python3 skills/failure-recovery-automation/scripts/recover_task.py \
  --task-id job-123 \
  --failure-reason "primary_api_timeout" \
  --checkpoints skills/failure-recovery-automation/references/sample-checkpoints.json \
  --strategies skills/failure-recovery-automation/references/sample-strategies.json \
  --out memory/failure-recovery/recovery-result.json \
  --audit memory/failure-recovery/recovery-audit.md
```

## Strategy Priority (default)
1. `retry_same`
2. `retry_with_backoff`
3. `fallback_alternate_api`
4. `degraded_mode`
5. `escalate`

## Safety
- Bounded retries only
- No destructive rollback; restore is logical-state based
- Full audit trail for each attempt and selected strategy
