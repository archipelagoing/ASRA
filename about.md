---
layout: page
title: About
nav: about
kicker: Project Framing
permalink: /about/
---

EvoNashMTL is a research repository for multi-task learning centered on one question: can Nash bargaining-based task balancing be improved by adding an evolutionary scheduler that adapts task influence over time?

The repository treats multi-task optimization as two linked problems:

- short-term fairness: how to combine competing task gradients into one shared update
- long-term adaptation: how to stop stronger or easier tasks from dominating training over time

Nash-MTL handles the first problem by solving for fair task weights at each step. EvoNashMTL extends that idea with an outer replicator-style scheduler that tracks slower training dynamics and nudges long-run task emphasis.

## What the project currently is

This repository is best understood as:

- a modified experimental fork of Nash-MTL
- a working area for the `replicator_nashmtl` method
- a place to connect theory, implementation, toy validation, and paper-writing material

It is still in an active prototype stage rather than a polished benchmark release.

## What the current evidence supports

The strongest current claim is not benchmark superiority. The toy experiments support a narrower and more defensible story:

- plain Nash-MTL is a stable but non-adaptive reference
- the replicator-augmented method changes weighting behavior in a controlled way
- the old scheduler collapse mode on the hard toy case has been repaired

The project is therefore strongest today as a mechanism and stability contribution.
