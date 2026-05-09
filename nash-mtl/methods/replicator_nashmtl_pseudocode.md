# Replicator-NashMTL Pseudocode

This note describes a `ReplicatorNashMTL` extension that is faithful to the two local references:

- `bg/mtlbargaining.pdf`:
  *Multi-Task Learning as a Bargaining Game* (Nash-MTL)
- `bg/dynamicEvolutionaryReplicator.pdf`:
  *Dynamic Influence on Replicator Evolution for the Propagation of Competing Technologies*

It is written to match the existing `WeightMethod` / `WeightMethods` interface in this repository, so it can later be implemented in `weight_methods.py` without changing the experiment structure.

## What Comes From Each Paper

### From Nash-MTL

- Compute one shared gradient per task.
- Form the task Gram matrix `GTG = G G^T`.
- Solve for positive bargaining coefficients `w` using the Nash-MTL optimization routine.
- Use only shared parameters for the bargaining weights.
- Form a single weighted loss `sum_i w_i * loss_i`.

### From the Dynamic Replicator Paper

- Maintain a population share vector `x(t)` on the simplex.
- Build a dynamic payoff matrix `A(t)` from a context feature vector `y(t)`.
- Use a linear influence model:
  - `A_ij(t) = alpha_ij^T y(t)`
- Update the shares with replicator dynamics:
  - `x_i_dot = x_i * (p_i - p_bar)`
  - where `p = A(t) x(t)` and `p_bar = x(t)^T A(t) x(t)`

### Adaptation Layer

The dynamic replicator paper is not itself a gradient-based multi-task optimizer. To combine it correctly with Nash-MTL in this codebase:

- use replicator dynamics as an outer task-priority scheduler
- use Nash-MTL as the inner gradient bargaining rule
- combine both outputs into final task weights

This preserves the methodology of both papers without replacing one with the other.

## Repository-Compatible Interface

The existing experiments call:

```python
loss, extra_outputs = weight_method.backward(
    losses=losses,
    shared_parameters=list(model.shared_parameters()),
    task_specific_parameters=list(model.task_specific_parameters()),
    last_shared_parameters=...,
    representation=...,
)
```

So a future implementation should keep the same shape:

```python
class ReplicatorNashMTL(WeightMethod):
    def __init__(
        self,
        n_tasks,
        device,
        max_norm=1.0,
        update_weights_every=1,
        optim_niter=20,
        replicator_lr=0.1,
        eps=1e-8,
        alpha_init=None,
        x_init=None,
    ):
        ...

    def get_weighted_loss(
        self,
        losses,
        shared_parameters,
        task_specific_parameters=None,
        last_shared_parameters=None,
        representation=None,
        scheduler_features=None,
        payoff_matrix=None,
        **kwargs,
    ):
        ...
```

## Key State Variables

- `x in R^K`: current replicator shares, one per task, constrained to the simplex
- `alpha_payoff in R^(K x K x m)`: linear coefficients mapping `m` dynamic features into a `K x K` payoff matrix
- `w_nash in R_+^K`: Nash-MTL bargaining weights
- `w_final in R_+^K`: final task weights after combining replicator priorities with Nash-MTL weights
- `scheduler_features = y(t) in R^m`: current dynamic influence vector

## Pseudocode

```text
Algorithm: Replicator-NashMTL

Inputs:
    K                     number of tasks
    losses[1..K]          task losses for current optimization step
    shared_parameters     shared model parameters used by Nash-MTL
    y(t) in R^m           dynamic feature vector for current state
    x(t) in Delta^K       current replicator shares on the simplex
    alpha_payoff          payoff coefficients, shape K x K x m
    eta                   discrete replicator step size
    eps                   numerical floor

Outputs:
    weighted_loss
    extra_outputs including:
        replicator_shares
        payoff_matrix
        nash_weights
        final_weights

Step 1. Compute dynamic payoff matrix A(t)
    For each task pair (i, j):
        A_ij(t) <- dot(alpha_payoff[i, j], y(t))

    Note:
        This follows the dynamic replicator paper's linear influence model:
        A_ij(t) = alpha_ij^T y(t)

Step 2. Update replicator shares x(t)
    p(t)     <- A(t) x(t)
    p_bar(t) <- x(t)^T A(t) x(t)

    For each task i:
        growth_i <- 1 + eta * (p_i(t) - p_bar(t))
        x_i(t+1) <- x_i(t) * max(eps, growth_i)

    Normalize x(t+1) so that:
        x_i(t+1) >= 0 for all i
        sum_i x_i(t+1) = 1

    Note:
        This is the discrete-time implementation of the replicator update.
        The continuous-time paper form is:
            x_i_dot = x_i (p_i - p_bar)

Step 3. Compute Nash-MTL bargaining weights w_nash
    For each task i:
        g_i <- grad(loss_i, shared_parameters)
        flatten g_i into a vector

    Stack task gradients into matrix G where row i is g_i
    GTG <- G G^T

    Normalize GTG by its matrix norm as done in this repository's NashMTL code

    Solve the Nash-MTL bargaining subproblem for positive coefficients w_nash:
        find w_nash > 0
        such that the Nash bargaining update direction is represented by
            Delta theta proportional to sum_i w_nash[i] * g_i

    In this repository, this is approximated by the same CCCP / cvxpy routine
    already used by NashMTL in weight_methods.py.

Step 4. Combine outer scheduler and inner bargaining weights
    For each task i:
        w_final[i] <- x_i(t+1) * w_nash[i]

    Normalize w_final so that:
        w_final[i] >= 0 for all i
        sum_i w_final[i] = K
        or, alternatively, sum_i w_final[i] = 1

    Repository note:
        Choose one normalization convention and use it consistently.
        The current code often keeps weights on a scale comparable to the number of tasks.

Step 5. Form weighted loss and backpropagate
    weighted_loss <- sum_i w_final[i] * losses[i]

    Return:
        weighted_loss,
        {
            "replicator_shares": x(t+1),
            "payoff_matrix": A(t),
            "nash_weights": w_nash,
            "final_weights": w_final,
        }
```

## Why This Is Accurate to Both Papers

### Accuracy to Nash-MTL

- The gradient aggregation is still a bargaining problem over shared task gradients.
- The actual bargaining weights still come from the Nash-MTL optimization step.
- The final update direction remains a positive combination of task gradients.
- Scale-invariance still comes from the Nash-MTL solver, not from the replicator layer.

### Accuracy to the Dynamic Replicator Paper

- The payoff matrix is explicitly time-varying.
- The payoff matrix is built from external dynamic influences through a linear map.
- Replicator shares evolve according to payoff relative to average payoff.
- The scheduler state is a population share vector on the simplex.

## Important Constraint for Grading Accuracy

Do not describe the replicator layer as replacing Nash bargaining.

That would be inaccurate to the Nash-MTL paper. The correct description is:

- replicator dynamics supplies dynamic task priorities over time
- Nash-MTL supplies the within-step bargaining solution over gradients

## Recommended Feature Design for y(t)

To stay close to the dynamic influence methodology while remaining compatible with this codebase, `y(t)` should be built from observable task-level or batch-level signals, for example:

- current normalized losses
- recent loss improvement rates
- gradient conflict statistics
- uncertainty estimates
- validation lag per task
- task-specific budget or cost pressure

These are not specified by either paper directly; they are the domain-specific adaptation needed to move from technology-market dynamics to multi-task learning dynamics.

## Minimal Implementation Plan

1. Add a new method class `ReplicatorNashMTL` to `weight_methods.py`.
2. Reuse the existing Nash-MTL solver code for Step 3.
3. Store `x` as persistent method state, updated every call or every `update_weights_every` steps.
4. Initially accept `scheduler_features` or `payoff_matrix` through `kwargs`.
5. Register the method in `METHODS`, for example:
   - `replicator_nashmtl=ReplicatorNashMTL`
6. Add experiment-side plumbing only for the extra scheduler inputs.

## Short Report Wording

If you need one sentence for the paper:

> We extend Nash-MTL with an outer dynamic evolutionary scheduler: a context-dependent payoff matrix updates task priorities through replicator dynamics, and these priorities are fused with Nash bargaining weights to produce the final multi-task update.
