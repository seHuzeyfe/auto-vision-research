---
name: experiment
description: Run the autonomous CV training experiment loop — modify, train, measure, keep/discard, repeat
---

You are running the core CV_AgenticTune experiment loop. Follow this protocol strictly:

## Goal
Minimize `mAP 50-95` on the target dataset using Ultralytics YOLO. Prefer simpler code. Keep VRAM reasonable.

## Loop Protocol

1. **Establish baseline** (first run only)
   - Run training with current config, record mAP 50-95 and peak VRAM to `results.tsv`
   - Format: `run_id\tchange_description\tmap50_95\tpeak_vram_mb\tstatus`

2. **Propose a change**
   - One focused change at a time (hyperparameter, augmentation, architecture setting, etc.)
   - Prefer changes that are simple and well-motivated

3. **Apply the change**
   - Edit the relevant config or training file
   - Document what was changed and why

4. **Train** (~5 min budget)
   - Run: `uv run python main.py` (or appropriate training command)
   - Capture mAP 50-95 and peak VRAM from output

5. **Measure & decide**
   - If mAP improved (lower is better): keep the change, log `kept` in results.tsv
   - If mAP worsened or VRAM blew up unreasonably: revert the change, log `reverted`

6. **Repeat** from step 2

## Results Log
Always append to `results.tsv` after each run. Never delete prior entries.

## Stopping
Stop when the user says to stop, or after 10 iterations without improvement.
