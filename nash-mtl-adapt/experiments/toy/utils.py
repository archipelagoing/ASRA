import matplotlib
matplotlib.use("Agg")
import numpy as np
import seaborn as sns
import torch
from matplotlib import pyplot as plt

from experiments.toy.problem import Toy


# plotting utils
def plot_2d_pareto(trajectories: dict, scale):
    """Adaptation of code from: https://github.com/Cranial-XIX/CAGrad"""
    fig, ax = plt.subplots(figsize=(6, 5))

    F = Toy(scale=scale)

    losses = []
    for res in trajectories.values():
        losses.append(F.batch_forward(torch.from_numpy(res["traj"])))

    yy = -8.3552
    x = np.linspace(-7, 7, 1000)

    inpt = np.stack((x, [yy] * len(x))).T
    Xs = torch.from_numpy(inpt).double()

    Ys = F.batch_forward(Xs)
    ax.plot(
        Ys.numpy()[:, 0],
        Ys.numpy()[:, 1],
        "-",
        linewidth=8,
        color="#72727A",
        label="Pareto Front",
    )  # Pareto front

    for i, tt in enumerate(losses):
        ax.scatter(
            tt[0, 0],
            tt[0, 1],
            color="k",
            s=150,
            zorder=10,
            label="Initial Point" if i == 0 else None,
        )
        colors = matplotlib.cm.magma_r(np.linspace(0.1, 0.6, tt.shape[0]))
        ax.scatter(tt[:, 0], tt[:, 1], color=colors, s=5, zorder=9)

    sns.despine()
    ax.set_xlabel(r"$\ell_1$", size=30)
    ax.set_ylabel(r"$\ell_2$", size=30)
    ax.xaxis.set_label_coords(1.015, -0.03)
    ax.yaxis.set_label_coords(-0.01, 1.01)

    for tick in ax.xaxis.get_major_ticks():
        tick.label1.set_fontsize(20)
    for tick in ax.yaxis.get_major_ticks():
        tick.label1.set_fontsize(20)

    plt.tight_layout()

    legend = ax.legend(
        loc=2, bbox_to_anchor=(-0.15, 1.3), frameon=False, fontsize=20, ncol=2
    )

    return ax, fig, legend


def plot_scheduler_history(history: dict, out_file):
    fig, axes = plt.subplots(3, 1, figsize=(9, 10), sharex=True)
    steps = history["steps"]

    replicator_shares = history.get("replicator_shares")
    nash_weights = history.get("nash_weights")
    final_weights = history.get("final_weights")

    if replicator_shares is not None:
        for task_idx in range(replicator_shares.shape[1]):
            axes[0].plot(
                steps,
                replicator_shares[:, task_idx],
                label=f"task_{task_idx}",
                linewidth=2,
            )
    axes[0].set_ylabel("Replicator")
    axes[0].set_title("Replicator Shares")
    axes[0].legend(frameon=False)

    if nash_weights is not None:
        for task_idx in range(nash_weights.shape[1]):
            axes[1].plot(
                steps,
                nash_weights[:, task_idx],
                label=f"task_{task_idx}",
                linewidth=2,
            )
    axes[1].set_ylabel("Nash")
    axes[1].set_title("Nash Weights")

    if final_weights is not None:
        for task_idx in range(final_weights.shape[1]):
            axes[2].plot(
                steps,
                final_weights[:, task_idx],
                label=f"task_{task_idx}",
                linewidth=2,
            )
    axes[2].set_ylabel("Final")
    axes[2].set_xlabel("Step")
    axes[2].set_title("Final Weights")

    for ax in axes:
        sns.despine(ax=ax)

    plt.tight_layout()
    plt.savefig(out_file, bbox_inches="tight", facecolor="white")
    plt.close(fig)
