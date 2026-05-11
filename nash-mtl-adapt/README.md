# EvoNashMTL `nash-mtl-adapt` Subproject

This directory is the implementation-facing part of the EvoNashMTL repository. The root `README.md` explains the project-level research idea; this README explains where the code lives, what was changed, and how to run the current experiments.

It began as an adapted Nash-MTL codebase and is now the main place where bargaining-based multi-task weighting methods are modified, compared, and extended with evolutionary scheduling behavior.

## What this subproject is for

The goal of this subdirectory is not to preserve the original upstream repository unchanged. Its role here is to provide:

- a working multi-task learning training framework
- the baseline Nash-MTL implementation
- comparative weighting baselines such as `pcgrad`, `cagrad`, `mgda`, and others
- the EvoNashMTL prototype method `replicator_nashmtl`

In this repo, the most important extension beyond standard Nash-MTL is the addition of a replicator-style scheduler that evolves task influence over time before combining it with Nash bargaining weights.

## EvoNashMTL method in this codebase

The method is exposed as:

```bash
--method replicator_nashmtl
```

Implementation location:

- [methods/weight_methods.py](/Users/archi/Desktop/Coding/EvoNashMTL/nash-mtl-adapt/methods/weight_methods.py:823)

The current implementation supports three payoff behaviors:

1. Identity fallback if neither `payoff_matrix` nor `scheduler_features` is provided
2. Direct `payoff_matrix` input from experiment code
3. Payoff construction from `scheduler_features + alpha_payoff_init`

The resulting task weights come from two layers:

- `replicator_shares`: outer evolutionary scheduler state
- `nash_weights`: inner Nash bargaining solution
- `final_weights`: combined weights used for the weighted loss

This is the main code path that operationalizes the EvoNashMTL idea in the repository.

## Current integration status

What is already present:

- `replicator_nashmtl` is registered as a selectable weight method
- smoke and focused tests exist in `tests/test_replicator_nashmtl.py`
- logging support exists for scheduler and bargaining outputs
- the toy experiment includes a simple dynamic direct-payoff path based on normalized current losses

What is still in progress:

- richer integration into the larger NYUv2 and QM9-style experiments
- more systematic multi-step behavioral verification
- fuller experiment documentation for EvoNashMTL-specific usage

## Setup

Install this subproject in editable mode from the repo root:

```bash
cd nash-mtl-adapt
pip install -e .
```

If you use the heavier experiments, you may also need the dependencies listed in:

- [requirements.txt](/Users/archi/Desktop/Coding/EvoNashMTL/nash-mtl-adapt/requirements.txt:1)

## Running experiments

General pattern:

```bash
cd nash-mtl-adapt/experiments/<experiment_name>
python trainer.py --method <method_name>
```

Available experiment folders here include:

- `toy`
- `quantum_chemistry`
- `nyuv2`

Examples:

```bash
cd nash-mtl-adapt/experiments/toy
python trainer.py --method replicator_nashmtl --log-weights true --replicator-lr 0.01
```

```bash
cd nash-mtl-adapt/experiments/toy
python trainer.py --method nashmtl
```

## Useful EvoNashMTL flags

Common flags already exposed in the experiment parsers:

- `--method replicator_nashmtl`
- `--replicator-lr`
- `--update-weights-every`
- `--log-weights`
- `--log-weights-every`

These are defined through:

- [experiments/utils.py](/Users/archi/Desktop/Coding/EvoNashMTL/nash-mtl-adapt/experiments/utils.py:24)

## What to inspect during runs

If you are testing EvoNashMTL behavior, inspect:

- `replicator_shares` to see how the scheduler is reallocating task influence
- `nash_weights` to see the bargaining solution at the current step
- `final_weights` to see what actually drives the weighted loss

This is especially useful when comparing:

- `nashmtl`
- `replicator_nashmtl`

For the current state of the repo, the toy experiment is the clearest place to observe these differences directly.

## Methods available in this codebase

This subproject currently exposes a unified API for multiple weighting methods, including:

- `nashmtl`
- `replicator_nashmtl`
- `pcgrad`
- `cagrad`
- `mgda`
- `imtl`
- `dwa`
- `uw`
- `ls`
- `scaleinvls`
- `rlw`
- `stl`

Method registration lives in:

- [methods/weight_methods.py](/Users/archi/Desktop/Coding/EvoNashMTL/nash-mtl-adapt/methods/weight_methods.py:1064)

## Notes on provenance

This directory was adapted from prior Nash-MTL code rather than written entirely from scratch. In the context of the EvoNashMTL repository, it should be understood as a modified experimental base for research iteration, not as a pristine mirror of the original upstream project.
