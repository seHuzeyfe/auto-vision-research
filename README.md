# automap

Autonomous hyperparameter search for YOLO computer vision models. An agent runs the training loop indefinitely — modifying config, training for 5 minutes, measuring mAP, keeping improvements and discarding regressions.

Inspired by [Andrej Karpathy's autoresearch](https://github.com/karpathy/autoresearch).

## What it does

The agent follows a simple loop:

1. Pick a config change (learning rate, augmentation, optimizer, etc.)
2. Commit it to git
3. Train for ~5 minutes
4. If mAP improved → keep the commit; if not → `git reset --hard`
5. Repeat

Git history becomes the research log. `results.tsv` tracks every experiment (including discarded ones).

## Setup

**Requirements:** Python 3.10+, CUDA GPU

```bash
# Install uv (if not already installed)
pip install uv

# Install dependencies
uv sync
```

## Usage

1. Set your model and dataset paths in `train.py`:
   ```python
   MODEL = "your_model.pt"
   DATA = r"path/to/dataset.yaml"
   ```

2. Run a single training session:
   ```bash
   uv run --no-sync train.py
   ```

3. Run the autonomous experiment loop (requires [Claude Code](https://claude.ai/code)):
   ```bash
   # In Claude Code terminal, on a fresh branch:
   /experiment or say "Kick off a new experiment"
   ```

## Project structure

```
train.py       — training script (edit the config block)
program.md     — agent loop protocol
results.tsv    — experiment log (gitignored, persists across resets)
CLAUDE.md      — context for Claude Code agent
```

## Credits

Loop design inspired by [karpathy/autoresearch](https://github.com/karpathy/autoresearch).  
Training powered by [Ultralytics YOLO](https://github.com/ultralytics/ultralytics).
