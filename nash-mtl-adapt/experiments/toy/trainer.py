import wandb
import logging
from argparse import ArgumentParser
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import torch
from tqdm import tqdm

from experiments.toy.problem import Toy
from experiments.toy.utils import plot_2d_pareto, plot_scheduler_history
from experiments.utils import (
    common_parser,
    extract_weight_method_parameters_from_args,
    log_scheduler_outputs,
    set_logger,
    str2bool,
)
from methods.weight_methods import WeightMethods

set_logger()


def build_improvement_payoff_matrix(
    prev_loss_ema=None,
    loss_ema=None,
    temperature=1.0,
    gain=1.0,
    improvement_clip=5.0,
    normalization_eps=1e-3,
    eps=1e-8,
):
    if prev_loss_ema is None or loss_ema is None:
        raise ValueError("prev_loss_ema and loss_ema are required for improvement payoff")

    denom = prev_loss_ema.abs().clamp_min(normalization_eps)
    improvement = (prev_loss_ema - loss_ema) / denom
    improvement = torch.clamp(
        improvement,
        min=-improvement_clip,
        max=improvement_clip,
    )
    need = torch.clamp(improvement.mean() - improvement, min=0.0)
    scores = torch.softmax((gain * need) / max(temperature, eps), dim=0)
    return torch.diag(scores), improvement.detach(), need.detach()


def build_loss_ratio_payoff_matrix(losses, temperature=1.0, gain=1.0, eps=1e-8):
    losses_detached = losses.detach()
    normalized_losses = losses_detached / losses_detached.mean().abs().clamp_min(eps)
    centered_losses = normalized_losses - normalized_losses.mean()
    need = torch.clamp(centered_losses, min=0.0)
    scores = torch.softmax((gain * centered_losses) / max(temperature, eps), dim=0)
    return torch.diag(scores), normalized_losses.detach(), need.detach()


def build_loss_gap_payoff_matrix(losses, temperature=1.0, gain=1.0, eps=1e-8):
    losses_detached = losses.detach()
    centered_losses = losses_detached - losses_detached.mean()
    need = torch.clamp(centered_losses, min=0.0)
    scores = torch.softmax((gain * centered_losses) / max(temperature, eps), dim=0)
    return torch.diag(scores), centered_losses.detach(), need.detach()


def build_qm9_proxy_payoff_matrix(
    losses,
    prev_loss_ema=None,
    loss_ema=None,
    temperature=1.0,
    gain=1.0,
    improvement_clip=5.0,
    normalization_eps=1e-3,
    eps=1e-8,
):
    losses_detached = losses.detach()
    normalized_losses = losses_detached / losses_detached.mean().abs().clamp_min(eps)
    underperformance = torch.clamp(normalized_losses - 1.0, min=0.0)

    if prev_loss_ema is None or loss_ema is None:
        improvement_need = torch.zeros_like(losses_detached)
    else:
        denom = prev_loss_ema.abs().clamp_min(normalization_eps)
        improvement = (prev_loss_ema - loss_ema) / denom
        improvement = torch.clamp(
            improvement,
            min=-improvement_clip,
            max=improvement_clip,
        )
        improvement_need = torch.clamp(improvement.mean() - improvement, min=0.0)

    proxy_signal = 0.5 * underperformance + 0.5 * improvement_need
    scores = torch.softmax((gain * proxy_signal) / max(temperature, eps), dim=0)
    return torch.diag(scores), proxy_signal.detach(), improvement_need.detach()


def append_history(history, key, value):
    if value is None:
        return
    if isinstance(value, torch.Tensor):
        value = value.detach().cpu().numpy()
    history[key].append(np.array(value, dtype=np.float32))


def save_run_artifacts(out_path, method_type, all_traj, scheduler_histories, checks_summary):
    np.savez(
        out_path / f"{method_type}_trajectories.npz",
        **{
            f"init_{init_idx}_traj": run_data["traj"]
            for init_idx, run_data in all_traj.items()
        },
        **{
            f"init_{init_idx}_start": run_data["init"]
            for init_idx, run_data in all_traj.items()
        },
    )

    for init_idx, history in scheduler_histories.items():
        np.savez(
            out_path / f"{method_type}_init_{init_idx}_history.npz",
            steps=np.array(history["steps"], dtype=np.int32),
            task_losses=np.array(history["task_losses"], dtype=np.float32),
            trajectory=np.array(history["trajectory"], dtype=np.float32),
            replicator_shares=np.array(history["replicator_shares"], dtype=np.float32),
            nash_weights=np.array(history["nash_weights"], dtype=np.float32),
            final_weights=np.array(history["final_weights"], dtype=np.float32),
            trainer_loss_ema=np.array(history["trainer_loss_ema"], dtype=np.float32),
            improvement=np.array(history["improvement"], dtype=np.float32),
            need=np.array(history["need"], dtype=np.float32),
        )
        if history["replicator_shares"]:
            plot_scheduler_history(
                {
                    "steps": np.array(history["steps"], dtype=np.int32),
                    "replicator_shares": np.array(
                        history["replicator_shares"], dtype=np.float32
                    ),
                    "nash_weights": np.array(history["nash_weights"], dtype=np.float32),
                    "final_weights": np.array(history["final_weights"], dtype=np.float32),
                },
                out_path / f"{method_type}_init_{init_idx}_scheduler.png",
            )

    report_lines = []
    for init_idx, summary in checks_summary.items():
        report_lines.append(f"init={init_idx}")
        report_lines.append(f"  shares_positive: {summary['shares_positive']}")
        report_lines.append(f"  shares_normalized: {summary['shares_normalized']}")
        report_lines.append(f"  shares_moved: {summary['shares_moved']}")
        report_lines.append(f"  no_one_hot_collapse: {summary['no_one_hot_collapse']}")
        report_lines.append(
            f"  final_weights_differ_from_nash: {summary['final_weights_differ_from_nash']}"
        )
        report_lines.append(
            f"  max_share_deviation: {summary['max_share_deviation']:.6f}"
        )
        report_lines.append(
            f"  max_final_vs_nash_diff: {summary['max_final_vs_nash_diff']:.6f}"
        )
        report_lines.append(
            f"  max_relative_loss_gap: {summary['max_relative_loss_gap']:.6f}"
        )
        report_lines.append("")

    (out_path / f"{method_type}_checks.txt").write_text("\n".join(report_lines))


def save_comparison_summary(base_out_path, method_names):
    report_lines = [
        "Toy baseline comparison mode",
        f"shared_init_indices: {args.init_indices}",
        f"shared_n_epochs: {args.n_epochs}",
        f"baseline_method: {method_names[0]}",
        f"target_method: {method_names[1]}",
        f"scheduler_signal: {args.scheduler_signal}",
        "",
        "Output folders:",
    ]
    for method_name in method_names:
        report_lines.append(f"  {method_name}: {(base_out_path / method_name).as_posix()}")

    report_lines.extend(
        [
            "",
            "What to inspect:",
            "  - Pareto plot in each method folder",
            "  - scheduler history plots for replicator_nashmtl",
            "  - *_checks.txt files for movement, collapse, and Nash-difference checks",
            "  - *_history.npz files for direct analysis",
        ]
    )
    (base_out_path / "comparison_summary.txt").write_text("\n".join(report_lines))


def evaluate_scheduler_checks(history, movement_threshold, diff_threshold, collapse_threshold):
    shares = np.array(history["replicator_shares"], dtype=np.float32)
    nash = np.array(history["nash_weights"], dtype=np.float32)
    final_weights = np.array(history["final_weights"], dtype=np.float32)
    task_losses = np.array(history["task_losses"], dtype=np.float32)

    if shares.size == 0:
        return dict(
            shares_positive=True,
            shares_normalized=True,
            shares_moved=False,
            no_one_hot_collapse=True,
            final_weights_differ_from_nash=False,
            max_share_deviation=0.0,
            max_final_vs_nash_diff=0.0,
            loss_diverged=False,
            max_relative_loss_gap=0.0,
        )

    share_sums = shares.sum(axis=1)
    shares_positive = bool(np.all(shares > 0.0))
    shares_normalized = bool(np.allclose(share_sums, 1.0, atol=1e-4))
    max_share_deviation = float(np.max(np.abs(shares - 0.5)))
    loss_gap = np.abs(task_losses[:, 0] - task_losses[:, 1])
    mean_loss_scale = np.maximum(np.mean(np.abs(task_losses), axis=1), 1e-8)
    relative_loss_gap = loss_gap / mean_loss_scale
    loss_diverged = bool(np.max(relative_loss_gap) > movement_threshold)
    shares_moved = bool(max_share_deviation > movement_threshold)
    no_one_hot_collapse = bool(np.max(shares) < collapse_threshold)
    n_tasks = final_weights.shape[1]
    nash_sums = np.clip(nash.sum(axis=1, keepdims=True), a_min=1e-8, a_max=None)
    normalized_nash = (nash / nash_sums) * n_tasks
    max_final_vs_nash_diff = float(np.max(np.abs(final_weights - normalized_nash)))
    final_weights_differ_from_nash = bool(max_final_vs_nash_diff > diff_threshold)

    return dict(
        shares_positive=shares_positive,
        shares_normalized=shares_normalized,
        shares_moved=shares_moved if loss_diverged else True,
        no_one_hot_collapse=no_one_hot_collapse,
        final_weights_differ_from_nash=final_weights_differ_from_nash,
        max_share_deviation=max_share_deviation,
        max_final_vs_nash_diff=max_final_vs_nash_diff,
        loss_diverged=loss_diverged,
        max_relative_loss_gap=float(np.max(relative_loss_gap)),
    )


def main(method_type, device, n_iter, scale, scheduler_kwargs=None):
    if scheduler_kwargs is None:
        scheduler_kwargs = {}

    weight_methods_parameters = extract_weight_method_parameters_from_args(args)
    n_tasks = 2

    F = Toy(scale=scale)

    all_traj = dict()
    scheduler_histories = dict()
    checks_summary = dict()

    # the initial positions
    inits = [
        torch.Tensor([-8.5, 7.5]),
        torch.Tensor([0.0, 0.0]),
        torch.Tensor([9.0, 9.0]),
        torch.Tensor([-7.5, -0.5]),
        torch.Tensor([9, -1.0]),
    ]
    if args.debug_init_preset == "representative" and not args.init_indices:
        selected_indices = [0]
    elif args.debug_init_preset == "origin" and not args.init_indices:
        selected_indices = [1]
    elif args.init_indices:
        selected_indices = [int(idx) for idx in args.init_indices.split(",")]
    else:
        selected_indices = list(range(len(inits)))

    for i in selected_indices:
        init = inits[i]
        traj = []
        x = init.clone()
        x.requires_grad = True
        x = x.to(device)
        trainer_loss_ema = None
        trainer_prev_loss_ema = None
        history = dict(
            steps=[],
            task_losses=[],
            trajectory=[],
            replicator_shares=[],
            nash_weights=[],
            final_weights=[],
            trainer_loss_ema=[],
            improvement=[],
            need=[],
        )

        method = WeightMethods(
            method=method_type,
            device=device,
            n_tasks=n_tasks,
            **weight_methods_parameters[method_type],
        )

        optimizer = torch.optim.Adam(
            [
                dict(params=[x], lr=1e-3),
                dict(params=method.parameters(), lr=args.method_params_lr),
            ],
        )

        for step_idx in tqdm(range(n_iter)):
            traj.append(x.cpu().detach().numpy().copy())
            history["steps"].append(step_idx)
            history["trajectory"].append(x.detach().cpu().numpy().copy())

            optimizer.zero_grad()
            f = F(x, False)
            append_history(history, "task_losses", f)
            scheduler_step_kwargs = dict(scheduler_kwargs)
            signal_values = None
            need = None
            if method_type == "replicator_nashmtl":
                current_losses = f.detach()
                if trainer_loss_ema is None:
                    trainer_loss_ema = current_losses.clone()
                    trainer_prev_loss_ema = current_losses.clone()
                else:
                    trainer_prev_loss_ema = trainer_loss_ema.clone()
                    trainer_loss_ema = (
                        args.toy_ema_decay * trainer_loss_ema
                        + (1.0 - args.toy_ema_decay) * current_losses
                    )
                append_history(history, "trainer_loss_ema", trainer_loss_ema)
                if args.scheduler_signal == "improvement":
                    payoff_matrix, signal_values, need = build_improvement_payoff_matrix(
                        prev_loss_ema=trainer_prev_loss_ema,
                        loss_ema=trainer_loss_ema,
                        temperature=args.toy_payoff_temperature,
                        gain=args.toy_payoff_gain,
                        improvement_clip=args.toy_improvement_clip,
                        normalization_eps=args.toy_normalization_eps,
                    )
                elif args.scheduler_signal == "loss_ratio":
                    payoff_matrix, signal_values, need = build_loss_ratio_payoff_matrix(
                        current_losses,
                        temperature=args.toy_payoff_temperature,
                        gain=args.toy_payoff_gain,
                    )
                elif args.scheduler_signal == "loss_gap":
                    payoff_matrix, signal_values, need = build_loss_gap_payoff_matrix(
                        current_losses,
                        temperature=args.toy_payoff_temperature,
                        gain=args.toy_payoff_gain,
                    )
                elif args.scheduler_signal == "qm9_proxy":
                    payoff_matrix, signal_values, need = build_qm9_proxy_payoff_matrix(
                        current_losses,
                        prev_loss_ema=trainer_prev_loss_ema,
                        loss_ema=trainer_loss_ema,
                        temperature=args.toy_payoff_temperature,
                        gain=args.toy_payoff_gain,
                        improvement_clip=args.toy_improvement_clip,
                        normalization_eps=args.toy_normalization_eps,
                    )
                else:
                    payoff_matrix = None
                if payoff_matrix is not None:
                    scheduler_step_kwargs["payoff_matrix"] = payoff_matrix
                append_history(history, "improvement", signal_values)
                append_history(history, "need", need)
            _, extra_outputs = method.backward(
                losses=f,
                shared_parameters=(x,),
                task_specific_parameters=None,
                last_shared_parameters=None,
                representation=None,
                **scheduler_step_kwargs,
            )
            append_history(history, "replicator_shares", extra_outputs.get("replicator_shares"))
            append_history(history, "nash_weights", extra_outputs.get("nash_weights"))
            append_history(history, "final_weights", extra_outputs.get("final_weights"))
            if args.log_weights and (step_idx % args.log_weights_every) == 0:
                log_scheduler_outputs(
                    extra_outputs,
                    step=step_idx,
                    prefix=f"toy init={i}",
                )
                if method_type == "replicator_nashmtl":
                    logging.info(
                        "toy init=%s step %s | scheduler_signal=%s | trainer_loss_ema=%s | signal_values=%s | need=%s",
                        i,
                        step_idx,
                        args.scheduler_signal,
                        trainer_loss_ema.detach().cpu().tolist(),
                        None if signal_values is None else signal_values.cpu().tolist(),
                        None if need is None else need.cpu().tolist(),
                    )
            optimizer.step()

        all_traj[i] = dict(init=init.cpu().detach().numpy().copy(), traj=np.array(traj))
        scheduler_histories[i] = history
        checks_summary[i] = evaluate_scheduler_checks(
            history,
            movement_threshold=args.scheduler_movement_threshold,
            diff_threshold=args.final_nash_diff_threshold,
            collapse_threshold=args.share_collapse_threshold,
        )
        logging.info("toy init=%s checks=%s", i, checks_summary[i])

    return all_traj, scheduler_histories, checks_summary


def run_method_and_save(method_type, out_path, device):
    out_path.mkdir(parents=True, exist_ok=True)
    logging.info("Logs and plots are saved in: %s", out_path.as_posix())

    all_traj, scheduler_histories, checks_summary = main(
        method_type=method_type,
        device=device,
        n_iter=args.n_epochs,
        scale=args.scale,
    )

    save_run_artifacts(
        out_path=out_path,
        method_type=method_type,
        all_traj=all_traj,
        scheduler_histories=scheduler_histories,
        checks_summary=checks_summary,
    )
    try:
        ax, fig, legend = plot_2d_pareto(trajectories=all_traj, scale=args.scale)

        title_map = {
            "nashmtl": "Nash-MTL",
            "replicator_nashmtl": "Replicator-NashMTL",
            "cagrad": "CAGrad",
            "mgda": "MGDA",
            "pcgrad": "PCGrad",
            "ls": "LS",
        }
        ax.set_title(title_map[method_type], fontsize=25)
        plt.savefig(
            out_path / f"{method_type}.png",
            bbox_extra_artists=(legend,),
            bbox_inches="tight",
            facecolor="white",
        )
        plt.close()
    except Exception as exc:
        logging.exception("Failed to save Pareto plot: %s", exc)

    return all_traj, scheduler_histories, checks_summary


if __name__ == "__main__":
    parser = ArgumentParser(
        "Toy example (modification of the one in CAGrad)", parents=[common_parser]
    )
    parser.set_defaults(n_epochs=35000, method="nashmtl", data_path=None)
    parser.add_argument(
        "--scale", default=1e-1, type=float, help="scale for first loss"
    )
    parser.add_argument(
        "--toy-payoff-temperature",
        default=0.05,
        type=float,
        help="temperature for building the toy payoff_matrix from recent loss improvement",
    )
    parser.add_argument(
        "--toy-payoff-gain",
        default=10.0,
        type=float,
        help="gain applied to under-improvement before the toy payoff softmax",
    )
    parser.add_argument(
        "--toy-ema-decay",
        default=0.9,
        type=float,
        help="EMA decay used by the trainer-side toy scheduler signal",
    )
    parser.add_argument(
        "--toy-improvement-clip",
        default=5.0,
        type=float,
        help="absolute clamp used on the toy relative-improvement signal",
    )
    parser.add_argument(
        "--toy-normalization-eps",
        default=1e-3,
        type=float,
        help="minimum absolute denominator used to normalize toy EMA improvements",
    )
    parser.add_argument(
        "--init-indices",
        default="0,1",
        type=str,
        help="comma-separated subset of toy initialization indices to run",
    )
    parser.add_argument(
        "--scheduler-signal",
        default="improvement",
        choices=["none", "loss_ratio", "loss_gap", "improvement", "qm9_proxy"],
        help="toy scheduler signal used to construct the replicator payoff_matrix",
    )
    parser.add_argument(
        "--debug-init-preset",
        default="none",
        choices=["none", "representative", "origin"],
        help="named toy initialization preset for debugging when init-indices is not explicitly set",
    )
    parser.add_argument(
        "--scheduler-movement-threshold",
        default=0.02,
        type=float,
        help="minimum share deviation treated as meaningful scheduler movement",
    )
    parser.add_argument(
        "--final-nash-diff-threshold",
        default=0.02,
        type=float,
        help="minimum absolute difference between final and Nash weights treated as meaningful",
    )
    parser.add_argument(
        "--share-collapse-threshold",
        default=0.98,
        type=float,
        help="maximum allowed share value before flagging one-hot collapse",
    )
    parser.add_argument(
        "--compare-baseline",
        default=False,
        type=str2bool,
        help="run a matched baseline comparison that saves baseline and target outputs side by side",
    )
    parser.add_argument(
        "--compare-baseline-method",
        default="nashmtl",
        choices=["nashmtl"],
        type=str,
        help="baseline method used when compare-baseline is enabled",
    )
    parser.add_argument("--out-path", default="outputs", type=Path, help="output path")
    parser.add_argument("--wandb_project", type=str, default=None, help="Name of Weights & Biases Project.")
    parser.add_argument("--wandb_entity", type=str, default=None, help="Name of Weights & Biases Entity.")
    args = parser.parse_args()

    if args.wandb_project is not None:
        wandb.init(project=args.wandb_project, entity=args.wandb_entity, config=args)

    device = torch.device("cpu")
    out_path = args.out_path
    if args.compare_baseline:
        method_names = [args.compare_baseline_method, args.method]
        for method_name in method_names:
            run_method_and_save(
                method_type=method_name,
                out_path=out_path / method_name,
                device=device,
            )
        save_comparison_summary(out_path, method_names)
    else:
        run_method_and_save(
            method_type=args.method,
            out_path=out_path,
            device=device,
        )

    if wandb.run is not None:
        wandb_root = out_path / args.method if args.compare_baseline else out_path
        pareto_plot = wandb_root / f"{args.method}.png"
        if pareto_plot.exists():
            wandb.log({"Pareto Front": wandb.Image(pareto_plot.as_posix())})
        for scheduler_plot in wandb_root.glob(f"{args.method}_init_*_scheduler.png"):
            wandb.log({f"Scheduler History {scheduler_plot.stem}": wandb.Image(scheduler_plot.as_posix())})

        wandb.finish()
