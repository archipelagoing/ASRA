import sys
from pathlib import Path

import torch


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from methods.weight_methods import WeightMethods


def _make_shared_parameter():
    return torch.nn.Parameter(torch.tensor([0.5, -0.25], dtype=torch.float32))


def _make_losses(shared_parameter):
    return torch.stack(
        (
            (shared_parameter[0] - 1.0) ** 2 + 0.5 * shared_parameter[1] ** 2,
            0.25 * shared_parameter[0] ** 2 + (shared_parameter[1] + 2.0) ** 2,
        )
    )


def _run_backward(method, shared_parameter, **kwargs):
    if shared_parameter.grad is not None:
        shared_parameter.grad.zero_()

    losses = _make_losses(shared_parameter)
    loss, extra_outputs = method.backward(
        losses=losses,
        shared_parameters=[shared_parameter],
        task_specific_parameters=None,
        last_shared_parameters=None,
        representation=None,
        **kwargs,
    )
    return loss, extra_outputs


def test_replicator_nashmtl_smoke_returns_final_weights():
    method = WeightMethods(
        method="replicator_nashmtl",
        n_tasks=2,
        device=torch.device("cpu"),
        update_weights_every=1,
        optim_niter=1,
        replicator_lr=0.5,
        replicator_update_every=1,
    )
    shared_parameter = _make_shared_parameter()

    loss, extra_outputs = _run_backward(method, shared_parameter)

    assert torch.is_tensor(loss)
    assert "final_weights" in extra_outputs
    assert extra_outputs["final_weights"].shape == (2,)
    assert torch.isfinite(extra_outputs["final_weights"]).all()


def test_replicator_nashmtl_falls_back_to_identity_payoff():
    method = WeightMethods(
        method="replicator_nashmtl",
        n_tasks=2,
        device=torch.device("cpu"),
        update_weights_every=1,
        optim_niter=1,
        replicator_lr=0.5,
        replicator_update_every=1,
    )
    shared_parameter = _make_shared_parameter()

    _, extra_outputs = _run_backward(method, shared_parameter)

    expected_payoff = torch.diag(torch.full((2,), 0.5, dtype=torch.float32))
    assert torch.allclose(extra_outputs["payoff_matrix"], expected_payoff)
    assert torch.allclose(
        extra_outputs["replicator_shares"],
        torch.full((2,), 0.5, dtype=torch.float32),
        atol=1e-6,
    )


def test_replicator_nashmtl_direct_payoff_updates_replicator_shares():
    method = WeightMethods(
        method="replicator_nashmtl",
        n_tasks=2,
        device=torch.device("cpu"),
        update_weights_every=1,
        optim_niter=1,
        replicator_lr=0.5,
        replicator_update_every=1,
        uniform_mix=0.0,
    )
    shared_parameter = _make_shared_parameter()
    payoff_matrix = torch.tensor([[2.0, 0.0], [0.0, 1.0]], dtype=torch.float32)

    _, first_outputs = _run_backward(
        method,
        shared_parameter,
        payoff_matrix=payoff_matrix,
    )
    _, second_outputs = _run_backward(
        method,
        shared_parameter,
        payoff_matrix=payoff_matrix,
    )

    first_shares = first_outputs["replicator_shares"]
    second_shares = second_outputs["replicator_shares"]

    assert torch.allclose(first_outputs["payoff_matrix"], payoff_matrix)
    assert not torch.allclose(first_shares, torch.full((2,), 0.5, dtype=torch.float32))
    assert not torch.allclose(second_shares, first_shares)


def test_replicator_nashmtl_delays_scheduler_updates():
    method = WeightMethods(
        method="replicator_nashmtl",
        n_tasks=2,
        device=torch.device("cpu"),
        update_weights_every=1,
        optim_niter=1,
        replicator_lr=0.5,
        replicator_update_every=3,
        uniform_mix=0.0,
    )
    shared_parameter = _make_shared_parameter()
    payoff_matrix = torch.tensor([[2.0, 0.0], [0.0, 1.0]], dtype=torch.float32)

    _, first_outputs = _run_backward(
        method,
        shared_parameter,
        payoff_matrix=payoff_matrix,
    )
    _, second_outputs = _run_backward(
        method,
        shared_parameter,
        payoff_matrix=payoff_matrix,
    )
    _, third_outputs = _run_backward(
        method,
        shared_parameter,
        payoff_matrix=payoff_matrix,
    )

    assert torch.allclose(
        first_outputs["replicator_shares"],
        second_outputs["replicator_shares"],
    )
    assert torch.allclose(
        second_outputs["replicator_shares"],
        third_outputs["replicator_shares"],
    )
