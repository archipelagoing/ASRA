---
layout: page
title: Repo
nav: repo
kicker: Code and Structure
permalink: /repo/
---

The main implementation work happens inside `nash-mtl-adapt/`.

## Repository map

- `nash-mtl-adapt/`: implementation subproject with weighting methods, experiments, tests, and the current `replicator_nashmtl` prototype
- `imgs/`: figures and high-signal notes used to summarize the toy validation story
- `bg/`: background papers and explanation material for the project writeup
- `meta/`: planning notes, rubric material, and progress logs
- `outputs/`: saved toy outputs and diagnostic artifacts

## Where to start

If you want the code first:

- `nash-mtl-adapt/methods/weight_methods.py`
- `nash-mtl-adapt/tests/test_replicator_nashmtl.py`
- `nash-mtl-adapt/experiments/toy/trainer.py`

If you want the project framing first:

- `README.md`
- `nash-mtl-adapt/README.md`

## Quick start

<pre class="code-block"><code>cd nash-mtl-adapt
pip install -e .</code></pre>

Run the current toy integration:

<pre class="code-block"><code>cd nash-mtl-adapt/experiments/toy
python trainer.py --method replicator_nashmtl --log-weights true --replicator-lr 0.01</code></pre>

## Current status

The repository is in an active prototype stage.

- the core `replicator_nashmtl` method exists
- toy-level integration is available
- focused tests and logging hooks are in place
- broader experiment integration and benchmark polishing are still ongoing
