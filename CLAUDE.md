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
uv run train.py > run.log 2>&1
```

Extract key metric:
```bash
grep "^map50_95:" run.log
```

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
