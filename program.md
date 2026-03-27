# CV_AgenticTune — Agent Program

This is the instruction set for the autonomous experiment loop. The agent reads this file and follows it indefinitely.

## Setup

To set up a new experiment, work with the user to:

1. **Agree on a run tag**: Propose a tag based on today's date (e.g., `mar27`). The branch `autoresearch/<tag>` must not already exist — this is a fresh run.
2. **Create the branch**: `git checkout -b autoresearch/<tag>`
3. **Read the in-scope files**: Read these files for full context:
   - `program.md` — this file, your instructions. Do not modify.
   - `train.py` — the config block you modify. Read the baseline values.
   - `CLAUDE.md` — project context.
4. **Confirm with user**:
   - Dataset YAML path (update `DATA` in train.py)
   - Model variant (update `MODEL` in train.py)
   - GPU availability
5. **Update train.py** config block with confirmed DATA and MODEL values.
6. **Initialize results.tsv** with just the header row:
   ```
   commit	map50_95	map50	precision	recall	memory_gb	status	description
   ```
7. **Confirm and go**: Confirm setup looks good. Once you get confirmation, kick off the experimentation.

## Experimentation

Each experiment runs on a single GPU. The training script runs for a **fixed time budget of ~5 minutes** (controlled by the `TIME` parameter). You launch it simply as: `uv run train.py`.

**What you CAN do:**
- Modify the config block in `train.py` (between `# ---- CONFIGURATION` and `# ---- END CONFIGURATION` markers). Everything in the config block is fair game: model variant, image size, batch size, optimizer, learning rate, augmentations, layer freezing, etc.

**What you CANNOT do:**
- Modify code outside the config block in `train.py`.
- Modify `program.md`, `pyproject.toml`, or any other file.
- Install new packages or add dependencies.

**The goal is simple: get the highest mAP50-95.** Since the time budget is fixed, you don't need to worry about training time — it's always ~5 minutes. Everything in the config block is fair game. The only constraint is that the code runs without crashing and finishes within the time budget.

**VRAM** is a soft constraint. Some increase is acceptable for meaningful mAP gains, but it should not blow up dramatically.

**Simplicity criterion**: All else being equal, simpler is better. Equal mAP from fewer config changes is a win. A marginal mAP gain from a fragile config combo? Probably not worth keeping.

**The first run**: Your very first run should always be to establish the baseline, so you will run the training script as-is.

## Output Format

Once the script finishes it prints a summary like this:

```
---
map50_95:         0.453200
map50:            0.672100
precision:        0.712300
recall:           0.623400
training_seconds: 285.3
peak_vram_mb:     4520.0
model:            yolo11s
epochs_completed: 47
```

You can extract the key metrics from the log file:

```
grep "^map50_95:\|^peak_vram_mb:" run.log
```

## Logging Results

When an experiment is done, log it to `results.tsv` (tab-separated, NOT comma-separated — commas break in descriptions).

The TSV has a header row and 8 columns:

```
commit	map50_95	map50	precision	recall	memory_gb	status	description
```

1. git commit hash (short, 7 chars)
2. map50_95 achieved (e.g. 0.453200) — use **0.000000** for crashes
3. map50 (e.g. 0.672100) — use **0.000000** for crashes
4. precision (e.g. 0.712300) — use **0.000000** for crashes
5. recall (e.g. 0.623400) — use **0.000000** for crashes
6. peak memory in GB, rounded to .1f (divide `peak_vram_mb` by 1024, e.g. 4520.0 MB = **4.4** GB) — use **0.0** for crashes
7. status: `keep`, `discard`, or `crash`
8. short text description of what this experiment tried

Example:

```
commit	map50_95	map50	precision	recall	memory_gb	status	description
a1b2c3d	0.4532	0.6721	0.7123	0.6234	4.4	keep	baseline yolo11s
b2c3d4e	0.4610	0.6890	0.7250	0.6310	4.5	keep	lr0=0.02
c3d4e5f	0.4500	0.6700	0.7100	0.6200	4.4	discard	cosine lr scheduler
d4e5f6g	0.0000	0.0000	0.0000	0.0000	0.0	crash	batch=128 (OOM)
```

## The Experiment Loop

The experiment runs on a dedicated branch (e.g. `autoresearch/mar27`).

LOOP FOREVER:

1. **Review context**: Read `results.tsv` and `git log --oneline -20` to understand what's been tried and what worked.
2. **Choose a modification**: Pick one change (or a small related set) based on prior results.
3. **Edit train.py**: Modify ONLY the config block (between markers).
4. **Git commit** with structured message:
   ```
   experiment: <short title>

   What: <what was changed and to what values>
   Why: <hypothesis — what improvement is expected and why>
   Context: <what previous experiments informed this choice>
   ```
5. **Run the experiment**: `uv run train.py > run.log 2>&1` (redirect everything — do NOT use tee or let output flood your context)
6. **Extract results**: `grep "^map50_95:\|^peak_vram_mb:" run.log`
7. If the grep output is empty, the run crashed. Run `tail -n 50 run.log` to read the Python stack trace and attempt a fix. If you can't get things to work after more than a few attempts, give up.
8. **Record the results** in results.tsv (NOTE: do not commit the results.tsv file, leave it untracked by git)
9. If mAP50-95 improved (higher), you "advance" the branch, **keeping** the git commit.
10. If mAP50-95 is equal or worse, you **discard** — `git reset --hard HEAD~1`.

The idea is that you are a completely autonomous researcher trying things out. If they work, keep. If they don't, discard. And you're advancing the branch so that you can iterate.

**Timeout**: Each experiment should take ~5 minutes total (+ overhead for model loading and validation). If a run exceeds 10 minutes, kill it and treat it as a failure (discard and revert).

**Crashes**: If a run crashes (OOM, a bug, etc.), use your judgment: If it's something easy to fix (e.g. a typo, a bad value), fix it and re-run. If the idea itself is fundamentally broken (e.g. batch size too large for GPU), skip it, log `crash` as the status in the tsv, and move on.

### Commit Message Example

```
experiment: increase lr0 from 0.01 to 0.02

What: LR0 changed from 0.01 to 0.02, kept SGD optimizer
Why: baseline converged slowly in 5-min window, higher LR may reach
     better optima faster within the time budget
Context: baseline (a1b2c3d) showed steady loss decrease without plateau,
         suggesting room for faster convergence
```

On **discard**, the commit is reset but the results.tsv row remains — so the full history of what was tried (including failures) is always available.

## NEVER STOP

Once the experiment loop has begun (after the initial setup), do NOT pause to ask the human if you should continue. Do NOT ask "should I keep going?" or "is this a good stopping point?". The human might be asleep, or gone from the computer, and expects you to continue working **indefinitely** until you are manually stopped. You are autonomous. The loop runs until the human interrupts you, period.

If each experiment takes ~5 minutes then you can run approximately **12 experiments/hour**, for a total of about **100 overnight**. The user wakes up to a full results.tsv of experiment history, all completed by you while they slept.

## When You Run Out of Ideas

If you feel stuck, think harder. Here are YOLO fine-tuning directions to explore:

- **Learning rate**: Try 2x, 5x, 0.5x, 0.1x of current LR0. Try different LRF values.
- **Optimizer**: Cycle through SGD, Adam, AdamW, NAdam, RAdam.
- **Model size**: Try yolo11n (faster, more epochs in budget), yolo11m/l (more capacity).
- **Image size**: 320 (faster), 640, 800, 1024 (higher resolution).
- **Batch size**: -1 (auto), 8, 16, 32, 64.
- **Augmentation**: Vary mosaic, mixup, copy_paste, erasing. Try DEGREES > 0 for rotation. Try FLIPUD for vertical flip (useful for aerial/satellite data).
- **Loss weights**: Adjust BOX, CLS, DFL ratios.
- **Freezing**: Freeze backbone layers (FREEZE=10) to preserve pretrained features, or unfreeze all (FREEZE=None) for full adaptation.
- **Warmup**: More or fewer warmup epochs. Different warmup momentum.
- **Cosine LR**: Toggle COS_LR.
- **Combinations**: Combine two previous near-misses that individually didn't improve but might work together (e.g., higher LR + cosine schedule).
- **Undo**: If recent changes degraded something, try reverting a specific parameter while keeping others.
