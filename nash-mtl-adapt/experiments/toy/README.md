# Illustrative Example

Modification of the code in [CAGrad](https://github.com/Cranial-XIX/CAGrad).

## What This Toy Trainer Is Testing

This toy setup is now used as a scheduler-validation harness for `replicator_nashmtl`, not just a Pareto-front demo.

The main question it is meant to answer is:

- does the outer replicator scheduler visibly change task influence over time
- without immediately collapsing to one task
- and in a way that can be compared against plain `nashmtl`

## Scheduler Input Modes

The trainer constructs a direct `payoff_matrix` for `replicator_nashmtl` from one of several signal modes:

- `--scheduler-signal improvement`
  Uses trainer-side EMA losses and gives more support to tasks with worse recent improvement. This is the best default if you want the toy setup to match the EvoNashMTL story.
- `--scheduler-signal qm9_proxy`
  Uses a blended proxy signal based on current relative task loss, smoothed under-improvement, and relative underperformance. This is the closest toy-side approximation to the kind of per-task statistics that drive behavior in the real QM9-style training loop.
- `--scheduler-signal loss_ratio`
  Uses normalized current task losses. Useful as a simpler ablation.
- `--scheduler-signal loss_gap`
  Uses centered current task losses. Useful as a stronger stress-test mode.
- `--scheduler-signal none`
  Passes no explicit scheduler signal, so the method falls back to its internal behavior.

## What To Expect

When the scheduler is behaving well, inspect:

- `replicator_shares`
  These should move when the task signals meaningfully diverge.
- `nash_weights`
  These show the inner Nash bargaining solution before outer modulation.
- `final_weights`
  These show the actual task weights used in optimization.

Healthy behavior usually looks like:

- shares stay positive
- shares stay normalized
- shares move when tasks diverge
- shares do not collapse to nearly one-hot immediately
- final weights differ from the normalized Nash baseline when the scheduler is truly active

## Most Important Hyperparameters

The most important toy scheduler knobs are:

- `--scheduler-signal`
- `--toy-payoff-temperature`
- `--toy-payoff-gain`
- `--toy-ema-decay`
- `--toy-improvement-clip`
- `--toy-normalization-eps`
- `--replicator-lr`
- `--replicator-uniform-mix`
- `--replicator-modulation-strength`
- `--init-indices`

For fast debugging, `--init-indices 0` is currently the clearest representative case.

You can now make that explicit with:

- `--debug-init-preset representative`
  Uses the current best nontrivial toy debug case (`init=0`) if `--init-indices` is not manually set.
- `--debug-init-preset origin`
  Uses the origin case (`init=1`) if you specifically want to stress the signal near the symmetric center.

## Saved Outputs

Each run can save:

- Pareto trajectory plot
- scheduler history plot
- `.npz` histories containing losses, trajectory, replicator shares, Nash weights, final weights, and scheduler-side signals
- a text checks report

The checks report is intended to help answer whether the scheduler is working as intended, but the plots and saved histories are still the best source of truth.

## Why `qm9_proxy` Exists

The real QM9 trainer computes per-task losses at each optimization step and then updates task weighting over time. The toy trainer obviously does not contain the full graph-learning setup, but `--scheduler-signal qm9_proxy` is meant to mimic the same kinds of experiment-side statistics:

- current per-task loss scale
- smoothed loss improvement over time
- relative task underperformance

That makes the toy harness a closer conceptual proxy for QM9/NYUv2-style adaptive weighting than a purely geometric or purely visual toy would be.

## Baseline Comparison Mode

Use `--compare-baseline true` to save matched outputs for:

- `nashmtl`
- the target method given by `--method`

under the same initialization subset and run length. This makes it easier to show whether the scheduler changes behavior, not just whether it runs.

Example:

```bash
cd /Users/archi/Desktop/Coding/EvoNashMTL/nash-mtl-adapt
python3 -m experiments.toy.trainer \
  --method replicator_nashmtl \
  --compare-baseline true \
  --scheduler-signal improvement \
  --n-epochs 220 \
  --init-indices 0,1 \
  --out-path outputs/toy_compare
```

## Recommended Default After Tuning

After the one-knob-at-a-time toy tuning pass, the cleanest default for the QM9-proxy toy setup is:

- `--scheduler-signal qm9_proxy`
- `--debug-init-preset representative`
- `--replicator-update-every 1`
- `--replicator-lr 0.05`
- `--replicator-uniform-mix 0.05`
- `--replicator-modulation-strength 0.3`
- `--toy-payoff-temperature 0.1`
- `--toy-payoff-gain 5.0`

This setting gives a clear scheduler effect on the representative toy case without the flatter behavior of weaker settings or the more aggressive push of the strongest modulation choice.

## Completed Tuning Pass

The toy Phase 2 sweep has been completed using the following protocol:

- hold all other settings fixed while changing one knob
- inspect:
  - `shares_moved`
  - `no_one_hot_collapse`
  - `final_weights_differ_from_nash`
  - the scheduler history plot
- prefer the smallest setting that produces a clear, stable effect

The sweep used:

- `--scheduler-signal qm9_proxy`
- `--init-indices 0` for the representative comparison case
- `--replicator-uniform-mix 0.05`
- `--toy-payoff-temperature 0.1`
- `--toy-payoff-gain 5.0`

### 1. `replicator_update_every`

Tried:

- `1`
- `5`
- `10`

Observed:

- `1` gave the strongest clear movement while staying stable
- `5` was still good, but weaker
- `10` was visibly flatter

Chosen value:

- `--replicator-update-every 1`

### 2. `replicator_lr`

Tried:

- `0.02`
- `0.05`
- `0.1`

Observed:

- `0.02` was a bit too mild
- `0.05` was the best middle ground
- `0.1` was noticeably more aggressive

Chosen value:

- `--replicator-lr 0.05`

### 3. `replicator_modulation_strength`

Tried:

- `0.1`
- `0.3`
- `0.5`

Observed:

- `0.1` was too weak and often left `final_weights_differ_from_nash=False`
- `0.3` was the best conservative default
- `0.5` gave the strongest visible effect, but was more aggressive than needed for the default

Chosen value:

- `--replicator-modulation-strength 0.3`

### Final Default

The completed toy default is:

- `--scheduler-signal qm9_proxy`
- `--debug-init-preset representative`
- `--replicator-update-every 1`
- `--replicator-lr 0.05`
- `--replicator-uniform-mix 0.05`
- `--replicator-modulation-strength 0.3`
- `--toy-payoff-temperature 0.1`
- `--toy-payoff-gain 5.0`

This is the point where tuning should stop unless the toy setup is changed again.

Example:

```bash
cd /Users/archi/Desktop/Coding/EvoNashMTL/nash-mtl-adapt
python3 -m experiments.toy.trainer \
  --method replicator_nashmtl \
  --scheduler-signal qm9_proxy \
  --debug-init-preset representative \
  --n-epochs 220 \
  --replicator-update-every 1 \
  --replicator-lr 0.05 \
  --replicator-uniform-mix 0.05 \
  --replicator-modulation-strength 0.3 \
  --toy-payoff-temperature 0.1 \
  --toy-payoff-gain 5.0 \
  --out-path outputs/toy_final_default
```
