# EvoNashMTL

EvoNashMTL is a research repository for multi-task learning (MTL) centered on a simple question:

Can Nash bargaining-based task balancing be improved by adding an evolutionary scheduler that adapts task influence over time?

The project combines:

- Nash bargaining for fair task-level gradient aggregation
- replicator-style scheduling for long-term adaptive task prioritization
- implementation notes, experiments, and paper-writing material for the evolving method

## Problem setting

In MTL, a shared model is trained on multiple tasks with losses `L_1, ..., L_n`. At each step, each task produces its own preferred gradient on the same shared parameters. Those gradients may align, partially conflict, or directly oppose one another.

This creates two linked optimization problems:

- short-term fairness: how to combine competing task gradients into one shared update
- long-term adaptation: how to stop stronger or easier tasks from dominating training over time

Nash-MTL addresses the first problem by treating tasks as bargaining agents and solving for fair task weights at each update. EvoNashMTL extends that idea by adding an outer scheduler that changes task influence dynamically based on performance-responsive signals.

## EvoNashMTL idea

EvoNashMTL uses a two-layer view of optimization:

1. An evolutionary scheduler maintains task shares over time.
2. A Nash bargaining layer computes fair stepwise task weights from the current gradient geometry.
3. Final task weights are formed by combining the scheduler shares with the Nash weights before the shared backward pass.

Conceptually:

- Nash bargaining handles local fairness at the current step
- replicator dynamics provide historical adaptation across steps

This makes EvoNashMTL a prototype for adaptive bargaining-based MTL rather than a pure static weighting method.

## Repository structure

- `nash-mtl-adapt/`: implementation subproject where the modified training code and weighting methods live
- `bg/`: background papers, explanation notes, and outline material for the project writeup
- `meta/`: planning notes, rubric material, and progress logs
- `oldASRA/`: older prototype material kept for reference

## Where the code lives

The main implementation work happens inside `nash-mtl-adapt/`.

That subproject contains:

- the modified weight-method implementation
- the experiment trainers
- the current `replicator_nashmtl` prototype
- focused tests and logging hooks for scheduler behavior

If you want implementation details or run commands, start with:

- [nash-mtl-adapt/README.md](/Users/archi/Desktop/Coding/EvoNashMTL/nash-mtl-adapt/README.md:1)

## Quick start

Install the implementation subproject:

```bash
cd nash-mtl-adapt
pip install -e .
```

Run the current toy integration:

```bash
cd nash-mtl-adapt/experiments/toy
python trainer.py --method replicator_nashmtl --log-weights true --replicator-lr 0.01
```

For detailed method flags, implementation notes, and experiment-level usage, see the subproject README above.

## Research framing

This repository is organized around the following research question:

Can dynamic evolutionary scheduling improve long-term fairness and task balance in Nash bargaining-based multi-task learning?

More specifically, the project studies whether:

- recent task improvement can influence future bargaining power
- replicator-style dynamics can reallocate task influence adaptively
- long-term neglected-task recovery can be improved without abandoning stepwise fairness

## What to inspect when running experiments

For `replicator_nashmtl`, the most useful outputs are:

- `replicator_shares`: the outer scheduler state over tasks
- `nash_weights`: the inner bargaining solution
- `final_weights`: the combined weights used for the actual weighted loss

These outputs help distinguish whether changes are coming from:

- the evolutionary scheduler
- the Nash solver
- their interaction

## Status

The repository is in an active prototype stage.

Current state:

- the core `replicator_nashmtl` method exists
- toy-level integration is available
- focused tests and logging are in place
- broader experiment integration and polishing are still ongoing

## Scope

This repository is an active research and prototyping workspace. It is best viewed as:

- a modified experimental fork of Nash-MTL
- a working area for EvoNashMTL method design
- a place to connect theory, implementation, and paper-writing artifacts

It should not yet be treated as a polished benchmark release.
