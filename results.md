---
layout: page
title: Results
nav: results
kicker: Toy Validation
permalink: /results/
---

The current results are strongest on the toy harness. They show mechanism, stability, and failure-repair evidence for `replicator_nashmtl`, not benchmark-level superiority on QM9 or NYUv2.

## High-signal summary

<div class="stat-list">
  <div class="stat"><strong>Baseline story:</strong> plain Nash-MTL is stable, but it stays essentially non-adaptive in the toy setup.</div>
  <div class="stat"><strong>Mechanism story:</strong> the tuned replicator version changes the optimization path and produces final weights that differ from plain Nash.</div>
  <div class="stat"><strong>Stability story:</strong> the old hard-case collapse on <code>init=1</code> was real, and the repaired design avoids that one-hot behavior while remaining adaptive.</div>
  <div class="stat"><strong>Scope note:</strong> the figures validate scheduler behavior and control. They do not yet prove better real-data benchmark performance.</div>
</div>

## Figure set

<div class="figure-list">
  <article class="figure-card">
    <img src="{{ '/imgs/fig1_toy_baseline_nashmtl.png' | relative_url }}" alt="Toy baseline trajectory under plain Nash-MTL">
    <h3>Figure 1. Plain Nash-MTL baseline</h3>
    <p>This is the stable reference behavior with no outer replicator scheduler.</p>
    <p>Why it matters: every other toy figure is interpreted relative to this control.</p>
  </article>

  <article class="figure-card">
    <img src="{{ '/imgs/fig2_toy_replicator_trajectory.png' | relative_url }}" alt="Toy trajectory under tuned replicator-augmented Nash-MTL">
    <h3>Figure 2. Replicator-augmented trajectory</h3>
    <p>This tuned version changes optimization behavior relative to the plain Nash baseline.</p>
    <p>Why it matters: it shows the method is not merely running; the outer scheduler is affecting the path.</p>
  </article>

  <article class="figure-card">
    <img src="{{ '/imgs/fig3_toy_weight_evolution.png' | relative_url }}" alt="Scheduler dynamics showing replicator shares, Nash weights, and final weights">
    <h3>Figure 3. Weight evolution and mechanism validation</h3>
    <p>This is the clearest mechanism figure. It separates <code>replicator_shares</code>, <code>nash_weights</code>, and <code>final_weights</code>.</p>
    <p>Why it matters: it is the cleanest proof that the outer scheduler is active, stable, and producing a real rebalancing effect.</p>
  </article>

  <article class="figure-card">
    <img src="{{ '/imgs/fig4_toy_old_collapse.png' | relative_url }}" alt="Old stress-test collapse behavior on the hard init equals one case">
    <h3>Figure 4. Old collapse mode</h3>
    <p>This captures the previous failure mode on the hard <code>init=1</code> case, where the scheduler became too aggressive and drifted toward one-hot behavior.</p>
    <p>Why it matters: it gives a concrete before-state rather than only claiming that earlier settings were unstable.</p>
  </article>

  <article class="figure-card">
    <img src="{{ '/imgs/fig5_toy_new_stable.png' | relative_url }}" alt="Stabilized behavior on the hard init equals one case">
    <h3>Figure 5. Repaired stable behavior</h3>
    <p>This shows the stabilized design on the same hard case after the signal and hyperparameter fixes.</p>
    <p>Why it matters: the collapse is not just hidden; the repaired scheduler remains normalized and adaptive without breaking into a selector.</p>
  </article>
</div>

## Notes distilled from the image folder

The strongest takeaways from `final_notes.txt`, `meaning.txt`, and `PaperBullets.txt` are:

- The core design goal is to augment Nash-MTL, not replace it. Nash remains the inner fairness mechanism, while the replicator layer provides slower long-run adaptation.
- The original toy setup was not enough because the outer scheduler was effectively inactive. The improved harness explicitly feeds scheduler signals and saves the right histories.
- The preferred scheduler signal is `qm9_proxy`, which blends relative loss, under-improvement, and underperformance into a smoother outer-control signal.
- The most informative figure is the weight-evolution plot because it exposes the exact relationship between scheduler state, bargaining weights, and final optimization weights.
- The repaired method is credible today as a stability and mechanism improvement. A clean benchmark-level win on real data remains an open question.

## Current limitations

- These results are still toy-centered.
- QM9 smoke runs launched, but they did not yet yield a finished comparison strong enough to headline.
- Under the final representative setup, some signal ablations looked similar, so the most persuasive story right now is scheduler responsiveness and stability rather than fine-grained signal separation.
