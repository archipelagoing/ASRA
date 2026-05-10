# Evolutionary Scheduler for Multi-Task Learning

This repository explores an **evolutionary scheduler for multi-task learning** built around **Nash bargaining** and related game-theoretic ideas.

The project combines research notes, prototype notebooks, and a modified `nash-mtl` codebase focused on bargaining-based task weighting, allocation, and scheduling behavior in multi-task learning.

## What's in this repo

- `ASRA_implementations/` - Jupyter notebooks for scheduler prototypes and experiments
- `nash-mtl/` - adapted code related to *Multi-Task Learning as a Bargaining Game*
- `bg/` - background papers and supporting research context
- `meta/` - planning notes, rubric material, and project logs

## Quick start

For the notebook-based prototype, start in `ASRA_implementations/`.

For the MTL codebase:

```bash
cd nash-mtl
pip install -e .
```

Then see the experiment-specific READMEs inside `nash-mtl/experiments/` for dataset and run instructions.

## Status

This is an active research/prototype repository. The current focus is on testing evolutionary and bargaining-based schedulers against simpler baselines and refining their behavior for multi-task learning setups.
