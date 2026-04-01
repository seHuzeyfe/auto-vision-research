# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

CV_AgenticTune is an autonomous computer vision fine-tuning system inspired by Karpathy's autoresearch project (reference repo under `autoresearch/`).

The core loop: **modify config → git commit → train (5 min) → measure mAP → keep if improved / discard if not → repeat forever.**

The model is **pretrained** — we are fine-tuning/hyperparameter-tuning, not training from scratch.

## How to Run

```bash
uv run train.py
```

Redirect output for the agent loop:
```bash
uv run --no-sync train.py > run.log 2>&1
```

Extract key metric:
```bash
grep "^map50_95:" run.log
```

**Important**: Always use `uv run --no-sync` to preserve the CUDA-compiled torch installation.

## Key Metric

**mAP50-95** (higher is better). This is the primary optimization target.

## Project Structure

- `train.py` — YOLO fine-tuning script with tunable config block (agent modifies this)
- `program.md` — Agent loop instructions (setup, experiment loop, rules)
- `results.tsv` — Experiment log (tab-separated, not git-tracked)
- `autoresearch/` — Reference repository only, not part of this project
- `spec.md` — Original project specification
- `plan.md` — Implementation plan

## Agent Instructions

- Read `program.md` for the full experiment loop protocol
- Only modify the config block in `train.py` (between `# ---- CONFIGURATION` and `# ---- END CONFIGURATION` markers)
- Git log is long-term memory — write detailed commit messages (What/Why/Context)
- Data: user provides Ultralytics-format dataset YAML path
- Use `/experiment` skill to start the autonomous loop
- Use `/analyze-results` skill to review experiment history

## Dependencies

Managed via `uv`. See `pyproject.toml`:
- `ultralytics` — YOLO training framework
- `ruff` — linting

## Experiment History & Findings (autoresearch/mar29, ~100 experiments)

### Best Configuration (mAP50-95: 0.4177)
Reached after ~50 experiments on branch `autoresearch/mar29`.

Key departures from Ultralytics defaults:
| Parameter | Default | Best Found | Impact |
|-----------|---------|------------|--------|
| `OPTIMIZER` | `auto` | `SGD` | BATCH=16+SGD was the first major jump (+0.0154) |
| `BATCH` | auto | `16` | Largest single improvement vs baseline |
| `WEIGHT_DECAY` | 0.0005 | `0.001` | Part of winning combo with warmup |
| `WARMUP_EPOCHS` | 3.0 | `6.0` | Longer warmup helped significantly (+0.0044) |
| `FLIPLR` | 0.5 | `0.3` | Biggest single improvement in session 2 (+0.0084) |
| `ERASING` | 0.4 | `0.0` | Disabling erasing was beneficial |

### What Was Exhaustively Tried and Failed
- **Optimizers**: Adam, AdamW (OOM), NAdam (much worse), RAdam (much worse) — SGD dominates
- **Batch sizes**: 8 (worse), 12 (worse), 20 (too slow), 32 (OOM) — 16 is optimal
- **Image sizes**: 320 (much worse), 704 (too slow) — 640 is optimal for 6GB VRAM
- **LR variants**: 0.005, 0.008, 0.012, 0.015, 0.02, 0.05 — 0.01 is optimal
- **LRF variants**: 0.001, 0.02, 0.05, 0.1 — 0.01 is optimal
- **Momentum**: 0.9, 0.94, 0.95 — 0.937 is optimal
- **WARMUP_EPOCHS**: 1, 5, 6.5, 7 — 6.0 is optimal
- **WARMUP_MOMENTUM**: 0.5, 0.85, 0.9 — 0.8 is optimal
- **COS_LR**: Tried True (worse, even after config improvements)
- **WEIGHT_DECAY**: 0.0005, 0.002 — 0.001 is optimal
- **FLIPLR**: 0.0, 0.1, 0.2, 0.4 — 0.3 is the sweet spot (non-monotonic)
- **FLIPUD**: 0.5 — much worse (data has vertical structure)
- **Augmentation** (all worse): DEGREES, TRANSLATE variants, SCALE variants, SHEAR, HSV_H/S/V variants, MOSAIC reduction, MIXUP, COPY_PASTE, ERASING
- **Loss weights**: BOX (5.0, 6.5, 7.0, 8.0), CLS (0.3, 0.6, 0.7), DFL (1.0, 1.2, 2.0) — all defaults optimal
- **Regularization**: DROPOUT variants, NBS=32, FREEZE=5/10
- **Other**: RECT=True, TIME variations, SEED variants, CLOSE_MOSAIC variants

### Key Insights
1. **VRAM constraint**: 6GB GPU. BATCH=16 → 4.4GB. BATCH=32 OOM. IMGSZ>640 requires fewer epochs per 5-min budget and hurts.
2. **Epoch count**: ~6 epochs per 5-min run is the sweet spot. TIME changes didn't help (longer→overfitting, shorter→underfitting).
3. **SGD superior**: All adaptive optimizers (Adam, AdamW, NAdam, RAdam) performed worse — likely because the model is already well-pretrained and SGD's simpler dynamics work better for fine-tuning near a good local minimum.
4. **Augmentation mostly harmful**: The pretrained model already has good augmentation baked in. Most augmentation increases hurt. Only FLIPLR reduction helped — likely because the defect dataset has horizontal directionality that the default 0.5 flip probability disrupts.
5. **Diminishing returns**: After ~50 experiments, parameter space was largely exhausted. Single-parameter changes yielded at most ±0.01 mAP variation.
