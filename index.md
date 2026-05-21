---
layout: default
title: Home
---

<section class="hero">
  <p class="eyebrow">Adaptive Multi-Task Learning</p>
  <h1>EvoNashMTL</h1>
  <p>EvoNashMTL is a research prototype that asks a narrow question with a concrete mechanism: can Nash bargaining-based multi-task weighting be improved by a slower evolutionary scheduler that adapts task influence over time?</p>
  <p>The current repository is strongest as a method and stability project. The toy harness shows that the outer scheduler can move, can alter final task weights relative to plain Nash-MTL, and can avoid the old one-hot collapse mode after repair.</p>
  <div class="hero-actions">
    <a class="button-link button-link--strong" href="{{ '/results/' | relative_url }}">View Results</a>
    <a class="button-link" href="{{ '/method/' | relative_url }}">Read the Method</a>
    <a class="button-link" href="{{ '/repo/' | relative_url }}">Browse the Repo</a>
  </div>
</section>

<section class="section grid grid--two">
  <article class="card">
    <p class="eyebrow">Core Idea</p>
    <h2>Two levels of task weighting</h2>
    <p>The method keeps Nash-MTL as the inner bargaining rule at each training step, then adds a slower replicator-style scheduler that updates task shares over time. Final weights are formed by modulating Nash weights with those scheduler shares.</p>
  </article>
  <article class="card">
    <p class="eyebrow">Current Evidence</p>
    <h2>Mechanism first, benchmarks later</h2>
    <p>The clearest current evidence is toy-level: the scheduler is active, the final optimization signal changes relative to plain Nash-MTL, and the hard stability case can be stabilized. Real benchmark superiority is still unconfirmed.</p>
  </article>
</section>

<section class="section">
  <p class="eyebrow">What This Site Covers</p>
  <div class="grid grid--two">
    <a class="card card-link" href="{{ '/about/' | relative_url }}">
      <h3>About</h3>
      <p>The project framing, research question, and current scope.</p>
    </a>
    <a class="card card-link" href="{{ '/results/' | relative_url }}">
      <h3>Results</h3>
      <p>All five toy figures, plus the strongest takeaways from the notes in <code>imgs/</code>.</p>
    </a>
    <a class="card card-link" href="{{ '/method/' | relative_url }}">
      <h3>Method</h3>
      <p>The two-level weighting design, tuned toy setup, and why the scheduler modulates Nash instead of replacing it.</p>
    </a>
    <a class="card card-link" href="{{ '/repo/' | relative_url }}">
      <h3>Repo</h3>
      <p>Where the code lives, how to run the prototype, and what to inspect during experiments.</p>
    </a>
  </div>
</section>
