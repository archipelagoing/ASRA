---
layout: page
title: About
---

EvoNashMTL is a prototype multi-task learning method that combines Nash bargaining with evolutionary scheduling.

The central idea is to separate:

- short-term fairness across task gradients at each update
- long-term adaptation of task influence over training

In this repository, Nash bargaining provides the local weighting step, while replicator-style dynamics adjust task shares over time. The result is an adaptive bargaining-based MTL framework for experimentation, analysis, and writeup development.
