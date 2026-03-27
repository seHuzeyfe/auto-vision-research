# CV_AgenticTune — Testing Plan

## 1. Smoke Test

Run training on a small built-in dataset to verify the script works end-to-end:

```bash
uv run train.py > run.log 2>&1
```

**Expected**: Script completes without errors, prints parseable metric block.

**Default config uses `coco128.yaml`** — Ultralytics auto-downloads this small dataset.

## 2. Output Parsing

Verify metrics are grep-extractable from run.log:

```bash
grep "^map50_95:" run.log
grep "^peak_vram_mb:" run.log
grep "^map50_95:\|^map50:\|^precision:\|^recall:\|^training_seconds:\|^peak_vram_mb:\|^model:\|^epochs_completed:" run.log
```

**Expected**: Each grep returns exactly one line with a numeric value.

## 3. Git Workflow

Test the commit → run → keep/discard cycle:

1. Make a config change in train.py (e.g., `LR0 = 0.02`)
2. `git commit -am "experiment: test lr change"`
3. `uv run train.py > run.log 2>&1`
4. Extract metrics, append to results.tsv
5. Test discard: `git reset --hard HEAD~1` — verify train.py reverts, results.tsv survives (untracked)

## 4. Timing

Verify the 5-minute time budget:

- Default `TIME = 0.083` (~5 min)
- Training should complete in approximately 5 minutes regardless of epoch count
- `EPOCHS = 300` is a high ceiling — `TIME` is the real budget

**Check**: `grep "^training_seconds:" run.log` should show ~300s (plus startup overhead).

## 5. Edge Cases

### OOM
- Set `BATCH = 128` or `IMGSZ = 1280` to trigger OOM on limited GPUs
- Verify crash is detectable: `grep "^map50_95:" run.log` returns empty
- `tail -n 50 run.log` should show CUDA OOM traceback

### Crash Recovery
- Introduce a deliberate error (e.g., invalid DATA path)
- Verify error is visible in run.log
- Verify results.tsv can log `crash` status

### results.tsv Integrity
- Verify tab separation (not comma)
- Verify untracked by git (`git status` shows `results.tsv` as untracked)
- Verify rows persist across `git reset --hard HEAD~1`

## 6. Full Loop Test

Run the `/experiment` skill and verify:

1. Setup phase completes (branch created, baseline run)
2. Agent autonomously picks modifications
3. Commits follow the What/Why/Context format
4. Keep/discard logic works correctly
5. results.tsv accumulates rows
6. Loop continues without stopping to ask
