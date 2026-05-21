---
layout: page
title: Method
nav: method
kicker: Design
permalink: /method/
---

`replicator_nashmtl` is a two-level weighting method.

## Inner level: Nash bargaining

At every optimization step, Nash-MTL computes a bargaining-based compromise over task gradients. This produces the raw `nash_weights`, which preserve the step-level fairness and conflict-handling behavior of the original method.

## Outer level: replicator scheduling

A slower replicator-style scheduler maintains task shares over time. Its role is not to override Nash, but to respond to slower training dynamics such as:

- which tasks are underperforming relative to others
- which tasks are improving more slowly
- which tasks may need more long-run support

The preferred toy signal is `qm9_proxy`, which blends:

- current relative task loss
- EMA-smoothed under-improvement
- relative task imbalance

## Final weighting rule

The final optimization weights come from combining the two levels:

- `nash_weights` supply the stepwise bargaining solution
- `replicator_shares` supply the slower adaptive allocation
- `final_weights` are formed by modulating Nash with the scheduler state

This hierarchy matters. The method is meant to stay recognizably Nash-MTL while gaining a controlled outer adaptation mechanism.

## Why the repaired version is more stable

The old failure mode came from an overly aggressive scheduler on the hard `init=1` case. The repaired setup stabilizes that behavior through:

- smoother improvement normalization
- clipping and payoff shaping
- gentler replicator learning dynamics
- nonzero uniform mixing
- moderated modulation strength

## Final toy settings

<pre class="code-block"><code>--scheduler-signal qm9_proxy
--debug-init-preset representative
--replicator-update-every 1
--replicator-lr 0.05
--replicator-uniform-mix 0.05
--replicator-modulation-strength 0.3
--toy-payoff-temperature 0.1
--toy-payoff-gain 5.0
--n-epochs 220</code></pre>

## What to inspect during runs

The most useful outputs are:

- `replicator_shares`
- `nash_weights`
- `final_weights`

Together they show whether changes are coming from the scheduler, the bargaining layer, or the interaction between them.
