III. System Model / Game Model

A. Multi-Task Learning Framework

* EvoNashMTL works in a multi-task learning (MTL) setting.
* This means:
    * One shared model
    * Multiple tasks
    * All tasks train the same core parameters
* Shared model parameters:

\theta

* Tasks:

T_1, T_2, ..., T_n

* Each task has its own loss function:

L_i(\theta)

* Loss = how poorly the model performs on task T_i.

⸻

At each training step:

* Every task computes its own preferred gradient:

g_i(t) = \nabla_\theta L_i(\theta_t)

* This gradient tells the model:
    * “Here’s how to improve my task.”

⸻

Core Problem:

* Different tasks may want different updates.
* Their gradients can:
    * agree
    * partially conflict
    * completely oppose each other

⸻

Main Challenge:

* One model cannot fully follow every task’s preferred direction at once.
* So the system must determine:

“How do we combine all task gradients fairly?”

⸻

Goal:

* Produce one shared update:

g_{\text{shared}}(t)

* This update should:
    * improve overall system performance
    * balance fairness
    * prevent task domination

⸻

Model Update:

\theta_{t+1} = \theta_t - \eta g_{\text{shared}}(t)

* Where:
    * \eta = learning rate
    * g_{\text{shared}}(t) = final shared gradient

⸻

Simple Summary:

* Tasks compete for influence
* Gradients conflict
* Shared update must balance all tasks fairly

⸻

B. Bargaining Game Interpretation

* EvoNashMTL treats tasks like players in a bargaining game.

⸻

In this framework:

* Each task wants:
    * maximum loss reduction
    * greater influence over the model update
* Shared model parameters are limited resources.

⸻

This means:

* Tasks cannot all fully “win”
* They must negotiate

⸻

Nash Bargaining does this by:

* Finding a shared gradient that:
    * gives balanced improvement
    * prevents one task from dominating
    * improves fairness across all tasks

⸻

Think of it like:

* Multiple hikers tied together
* Each wants to move in their own direction
* Nash bargaining chooses:

“What direction helps everyone most fairly?”

⸻

Benefits:

* Better fairness
* More balanced optimization
* Reduced domination
* Strong theoretical structure

⸻

Limitation of Standard Nash-MTL:

* Fairness is calculated mostly at the current step
* It does NOT strongly track:
    * long-term neglect
    * persistent weak tasks
    * historical underperformance

⸻

C. Problem Statement

Main Weakness of Existing Methods:

* Static weights:
    * Do not adapt
    * Ignore changing task difficulty
* Gradient conflict methods:
    * Focus on short-term correction
    * Often ignore long-term fairness
* Nash-MTL:
    * Improves stepwise fairness
    * Lacks strong adaptive memory

⸻

Real Problem:

* Some tasks may consistently fall behind over time.
* Without dynamic adjustment:
    * weaker tasks stay weak
    * stronger tasks dominate

⸻

Core Research Question:

\text{Can dynamic evolutionary scheduling improve long-term fairness and task balance in Nash bargaining-based multi-task learning?}

⸻

EvoNashMTL’s Solution:

* Track task improvement history
* Detect underperforming tasks
* Increase their bargaining priority
* Reduce dominance of already-strong tasks

⸻

Core Idea:
can
Short-term fairness:

* Nash bargaining

Long-term adaptation:

* Evolutionary scheduler

⸻

Final Objective:

* Fairer optimization
* Better neglected-task recovery
* Adaptive task balancing
* Stronger long-term system robustness

⸻

One-Line Summary

EvoNashMTL transforms multi-task learning from static gradient balancing into an adaptive bargaining system where task influence evolves based on historical performance.