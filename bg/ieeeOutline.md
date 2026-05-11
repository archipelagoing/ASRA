# EvoNashMTL: Evolutionary Scheduling for Nash Bargaining-Based Multi-Task Learning

---

# Abstract  
- Multi-task learning (MTL) improves efficiency by training a shared model across multiple related tasks.  
- Shared optimization creates gradient conflict, where task objectives compete for parameter influence.  
- Existing approaches such as static weighting, PCGrad, CAGrad, and MGDA address gradient conflicts with varying fairness and optimization trade-offs.  
- Nash-MTL frames MTL as a bargaining game, using Nash bargaining to ensure fair gradient aggregation across tasks.  
- However, Nash-MTL primarily focuses on short-term fairness at each optimization step and does not explicitly adapt to long-term task neglect.  
- EvoNashMTL introduces an evolutionary scheduler that dynamically adjusts task bargaining weights based on recent task improvement.  
- Task urgency is computed from loss improvement, and replicator dynamics evolve task priorities over time.  
- These evolved priorities are integrated into the Nash bargaining process before final shared gradient aggregation.  
- The architecture combines short-term fairness with long-term adaptive balancing.  
- This work aims to improve neglected-task recovery, fairness, adaptability, and strategic robustness in multi-task optimization.

---

# Keywords  
- Multi-task learning  
- Nash bargaining  
- Evolutionary scheduling  
- Replicator dynamics  
- Adaptive optimization  
- Gradient conflict  

---

# I. Introduction  

- Multi-task learning trains one model across multiple tasks simultaneously.  
- Shared architectures improve efficiency, representation learning, and generalization.  
- However, tasks compete for shared parameters during optimization.  
- Task gradients may conflict, causing:
  - instability  
  - domination by easier tasks  
  - neglect of slower-learning tasks  
- Traditional static weighting methods fail to adapt to evolving task difficulty.  
- Dynamic gradient balancing methods such as PCGrad and CAGrad improve conflict resolution but focus primarily on short-term optimization.  
- Nash-MTL introduced a fairness-based bargaining framework for task gradient aggregation.  
- Nash bargaining ensures balanced task progress through negotiated shared updates.  
- Despite its fairness advantages, Nash-MTL lacks explicit long-term adaptive scheduling.  
- EvoNashMTL extends Nash-MTL by introducing an evolutionary scheduling layer.  
- Task priorities evolve based on recent performance trends.  
- Underperforming tasks gain urgency, while dominant tasks temporarily lose bargaining influence.  
- EvoNashMTL’s core contribution is a dual-layer optimization framework:
  - Evolutionary scheduler  
  - Nash bargaining aggregator  
- This framework aims to combine:
  - fairness  
  - adaptability  
  - neglected-task recovery  
  - long-term strategic optimization  

---

# II. Related Work / Background  

II. Related Work / Background

* Multi-task learning (MTL) improves efficiency by jointly training a shared model across multiple related tasks, but shared optimization often produces conflicting gradients that destabilize training and create unfair task competition [1].
* Traditional task-balancing approaches such as:
    * equal weighting
    * uncertainty weighting
    * dynamic weight averaging
        provide basic balancing mechanisms, but they often fail to adapt effectively as task difficulty changes over time [1].

Gradient Conflict Mitigation

* PCGrad reduces destructive task interference through projected gradient surgery, directly modifying conflicting gradients before shared updates [2].
* CAGrad improves gradient coordination by balancing overall optimization progress with conflict aversion, producing more stable updates across competing tasks [3].
* MGDA frames MTL as a multi-objective optimization problem and seeks Pareto-efficient update directions across multiple task objectives [4].
* While these methods improve short-term gradient balancing, they primarily focus on immediate optimization conflicts rather than:
    * long-term task neglect
    * adaptive task recovery
    * evolving task priority

Nash Bargaining-Based Multi-Task Learning

* Nash-MTL models tasks as bargaining agents that negotiate shared gradient updates through Nash bargaining theory [1].
* This framework provides:
    * principled fairness
    * balanced utility improvement
    * stronger theoretical grounding than purely gradient-correction methods
* Nash-MTL significantly improves fairness in gradient aggregation, but it primarily optimizes fairness at each individual training step [1].
* It does not explicitly account for:
    * persistent underperformance
    * historical task neglect
    * dynamic long-term task reprioritization

Evolutionary Dynamics and Replicator Scheduling

* Replicator dynamics provide a formal adaptive framework where competing entities gain or lose influence based on relative fitness over time [5].
* Dynamic influence models for competing technologies demonstrate that replicator evolution can produce:
    * adaptive influence propagation
    * long-term strategic balancing
    * performance-responsive resource allocation [5]
* These principles are highly relevant to MTL scheduling, where task priorities may need to evolve according to historical optimization success.

EvoNashMTL Positioning

* EvoNashMTL extends Nash-MTL by integrating replicator-based evolutionary scheduling before bargaining aggregation.
* The architecture combines:
    * Nash bargaining for short-term fairness [1]
    * Replicator dynamics for long-term adaptive task weighting [5]
* This dual-layer design addresses key limitations in prior methods by introducing:
    * neglected-task recovery
    * dynamic bargaining influence
    * adaptive fairness memory
    * long-term strategic optimization

Core References

* Nash-MTL → bargaining fairness foundation [1]
* Dynamic Replicator Evolution → scheduler adaptation theory [5]
* PCGrad / CAGrad / MGDA → comparative gradient-balancing baselines [2][3][4]

Summary

* Prior MTL work largely focuses on:
    * static balancing
    * immediate gradient correction
    * short-term fairness
* EvoNashMTL uniquely combines:
    * bargaining fairness
    * evolutionary adaptation
    * long-term task prioritization
* This positions EvoNashMTL at the intersection of:
    * multi-task learning
    * game theory
    * replicator evolution
    * adaptive optimization systems. 

---

# III. System Model / Game Model  

A. Multi-Task Learning Framework

* EvoNashMTL operates within a standard multi-task learning (MTL) setting, where a single shared model is trained to optimize multiple related tasks simultaneously.
* The shared model contains global parameters:

\theta

* These parameters are updated using information from all tasks rather than from a single objective.
* Let the set of tasks be:

T_1, T_2, ..., T_n

* Each task represents an individual learning objective, prediction goal, or subproblem that depends on the same shared parameter space.
* Each task has its own task-specific loss function:

L_i(\theta)

* This loss measures how well the shared model performs on task T_i.
* During each training step t, each task computes its own gradient with respect to the shared parameters:

g_i(t) = \nabla_\theta L_i(\theta_t)

* These gradients represent the preferred update direction for each task.
* Since tasks often have competing objectives, these gradients may:
    * align
    * partially conflict
    * directly oppose one another
* This creates the central challenge of MTL:
    * How can one shared model update fairly improve multiple competing objectives?
* The overall goal is to aggregate these competing gradients into a single shared update direction:

g_{\text{shared}}(t)

* This shared gradient must balance:
    * optimization performance
    * fairness across tasks
    * stability of training
* Once the shared gradient is determined, the model parameters are updated as:

\theta_{t+1} = \theta_t - \eta g_{\text{shared}}(t)

* Where:
    * \eta is the learning rate
    * g_{\text{shared}}(t) is the final negotiated gradient update
* The design challenge is therefore not simply minimizing loss, but constructing a shared optimization strategy that prevents harmful task imbalance over time.

⸻

B. Bargaining Game Interpretation

* EvoNashMTL models the multi-task optimization process as a bargaining game among competing tasks.
* In this framework:
    * Each task acts as an individual bargaining player
    * Each player seeks to maximize its own improvement
    * Shared parameters act as limited optimization resources
* Each task’s utility depends on how much the final shared gradient reduces its own loss.
* Because all tasks share the same parameter space, no task can independently enforce its preferred update.
* Instead, tasks must effectively “negotiate” for influence over the final shared gradient.
* Nash bargaining provides a mathematically principled mechanism for this negotiation.
* The bargaining solution seeks a shared update that:
    * improves all tasks when possible
    * discourages domination by a single task
    * maximizes balanced collective progress
* This transforms the MTL optimization problem from:
    * pure gradient competition
* Into:
    * negotiated cooperative optimization
* Key advantages of the bargaining interpretation:
    * Promotes fairness
    * Encourages balanced utility gains
    * Reduces extreme task domination
    * Provides formal game-theoretic structure
* In standard Nash-MTL, bargaining fairness is optimized at each training step.
* However, bargaining alone does not explicitly incorporate long-term memory of:
    * neglected tasks
    * persistent underperformance
    * shifting optimization urgency
* EvoNashMTL addresses this by introducing evolutionary scheduling prior to bargaining aggregation.

⸻

C. Problem Statement

* Static task weighting methods assume task priorities remain fixed throughout training.
* In practice, this assumption is often unrealistic because:
    * Task difficulty evolves
    * Some tasks improve faster than others
    * Certain tasks may become persistently neglected
    * Optimization imbalance can worsen over time
* Existing gradient-balancing methods improve short-term conflict management, but they often lack mechanisms for:
    * long-term adaptation
    * neglected-task recovery
    * performance-responsive reprioritization
* Nash-MTL improves fairness through bargaining, but it primarily enforces fairness at individual optimization steps rather than across historical training behavior.
* This creates a key limitation:
    * A task may consistently underperform across many steps without sufficiently increasing its future bargaining influence.
* The central research question of EvoNashMTL is:

\text{Can dynamic evolutionary scheduling improve long-term fairness and task balance in Nash bargaining-based multi-task learning?}

* More specifically, EvoNashMTL seeks to determine whether:
    * Task improvement history can inform future bargaining power
    * Replicator dynamics can adaptively reallocate optimization influence
    * Long-term fairness can outperform purely stepwise fairness
    * Dynamic scheduling can improve neglected-task recovery without sacrificing total system performance
* The proposed solution is to combine:
    * Evolutionary adaptation
    * Replicator-based task weighting
    * Nash bargaining fairness
* This transforms task optimization from:
    * static fairness
* Into:
    * historically adaptive strategic fairness.

---

# IV. Proposed Method: EvoNashMTL Architecture  

## A. Architecture Overview  

### Module 1: Task Loss Monitor  
- Tracks:
  - Current loss  
  - Previous loss  
- Computes task improvement:

latex p_i(t) = L_i(t-1) - L_i(t) 

- Measures short-term task progress.

---

### Module 2: Evolutionary Scheduler  

- Computes urgency fitness:

latex f_i(t) = \frac{1}{\epsilon + \max(p_i(t), 0)} 

- Interpretation:
  - Low improvement → higher urgency  
  - High improvement → lower urgency  

- Updates task bargaining weights:

latex w_i(t+1) = w_i(t) \cdot \frac{f_i(t)}{\bar{f}(t)} 

- Replicator dynamics evolve task influence over time.

---

### Module 3: Weighted Gradient Layer  

- Weighted gradient:

latex \tilde{g}_i(t) = w_i(t) \cdot g_i(t) 

- Scheduler modifies bargaining influence before aggregation.

---

### Module 4: Nash Bargaining Aggregator  

- Receives weighted gradients  
- Solves bargaining objective  
- Produces final shared update:

latex g_{\text{shared}}(t) 

---

## B. Full Pipeline  

text Task Losses ↓ Improvement Calculation ↓ Urgency Fitness ↓ Replicator Weight Update ↓ Weighted Gradients ↓ Nash Bargaining Aggregation ↓ Shared Gradient ↓ Model Parameter Update 

---

## C. Design Advantages  

- Dynamic long-term fairness  
- Neglected-task recovery  
- Adaptive scheduling  
- Strategic resource balancing  
- Improved robustness over static weighting  
- Enhanced interpretability through task weight evolution  

---

# V. Experimental Setup  

## Baselines  

- Equal weighting  
- Static weighting  
- PCGrad  
- CAGrad  
- MGDA  
- Original Nash-MTL  
- Evolutionary scheduler only  
- EvoNashMTL  

---

## Metrics  

- Total utility/performance  
- Fairness across tasks  
- Worst-task performance  
- Task variance  
- Weight stability  
- Adaptability  

---

## Experimental Goals  

- Evaluate fairness improvements  
- Measure long-term neglected-task recovery  
- Compare scheduler adaptability  
- Assess robustness under competing task difficulty  
- Benchmark against state-of-the-art MTL baselines  

---

## Simulation Design  

- Shared datasets/tasks  
- Identical model architecture across methods  
- Controlled hyperparameters  
- Comparative loss and performance tracking  
- Weight evolution visualization  

---

# VI. Results and Discussion  

## Expected Outcomes  

- EvoNashMTL should:
  - Improve fairness  
  - Reduce task neglect  
  - Maintain strong total performance  
  - Improve worst-task outcomes  
  - Show adaptive weight reallocation over time  

---

## Comparative Focus  

- Static weighting vs dynamic scheduling  
- Nash-MTL vs EvoNashMTL  
- Fairness-performance tradeoffs  
- Stability of replicator dynamics  
- Scheduler responsiveness  

---

## Suggested Figures  

### Figure 1  
- Full system architecture diagram  

### Figure 2  
- Task weight evolution curves  

### Figure 3  
- Task loss curves across baselines  

### Figure 4  
- Fairness metric over time  

---

## Suggested Tables  

### Table I  
- Baseline performance comparison  

Columns:
- Method  
- Total Performance  
- Worst Task  
- Fairness Score  
- Stability Score  
- Adaptability Score  

---

# VII. Conclusion  

- EvoNashMTL extends Nash-MTL through adaptive evolutionary scheduling.  
- Recent task improvement determines dynamic bargaining power.  
- Replicator dynamics introduce long-term memory into task prioritization.  
- Weighted Nash bargaining balances:
  - immediate fairness  
  - adaptive recovery  
- The architecture improves:
  - fairness  
  - adaptability  
  - neglected-task recovery  
  - strategic optimization robustness  
- EvoNashMTL offers a promising framework for dynamic resource allocation in multi-task systems.  
- Future work:
  - Larger benchmarks  
  - Alternative fitness formulations  
  - MARL applications  
  - Adaptive coalition systems  

---

# References  

## Core Required  
- [1] Multi-Task Learning as a Bargaining Game  
- [2] Dynamic Influence on Replicator Evolution for the Propagation of Competing Technologies  
- [3] PCGrad: Gradient Surgery for Multi-Task Learning  
- [4] CAGrad: Conflict-Averse Gradient Descent  
- [5] MGDA: Multi-Objective Optimization for MTL  

---

# Appendix (Optional if space permits)  

- Detailed scheduler pseudocode  
- Additional ablation studies  
- Hyperparameter sweeps  
- Weight normalization analysis  
- Sensitivity analysis for ε and replicator stability