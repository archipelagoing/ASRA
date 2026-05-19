---
layout: default
title: Home
---

# EvoNashMTL

EvoNashMTL is a research repository for adaptive multi-task learning. It explores whether Nash bargaining-based task balancing can be improved with an evolutionary scheduler that changes task influence over time.

The project combines:

- Nash bargaining for fair task-level gradient aggregation
- replicator-style scheduling for dynamic task prioritization
- implementation, experiments, and research notes around the evolving method

Core implementation lives in `nash-mtl-adapt/`, where the current `replicator_nashmtl` prototype extends Nash-MTL with outer scheduler shares that are combined with stepwise bargaining weights.
