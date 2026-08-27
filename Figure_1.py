"""
Render compliance_rate_by_criterion as a 600 dpi JPEG.

Plotting logic is identical to scripts/compute_compliance.py::make_figure;
the compliance rates are read from figures/compliance_rate_by_criterion.csv
(the output of the compute step).
"""

from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.patches import Patch

RATES_CSV = Path("/home/claude/compliance_rate_by_criterion.csv")
OUT_FILE = Path("/home/claude/compliance_rate_by_criterion.jpeg")

CRITERION_ORDER = [f"C{i}" for i in range(1, 21)]


def color_for_rate(rate: float) -> str:
    if rate >= 75:
        return "#5FAD56"
    if rate >= 50:
        return "#F2C14E"
    return "#F26B5E"


def make_figure(wide: pd.DataFrame, out_path: Path, dpi: int = 600) -> None:
    aerr_vals = wide["AERR"].values
    ijae_vals = wide["IJAE"].values
    criteria = wide.index.tolist()

    overall = (aerr_vals + ijae_vals) / 2.0
    order = np.argsort(-overall)
    criteria_sorted = [criteria[i] for i in order]
    aerr_sorted = aerr_vals[order]
    ijae_sorted = ijae_vals[order]

    y = np.arange(len(criteria_sorted))
    bar_h = 0.38

    aerr_colors = [color_for_rate(v) for v in aerr_sorted]
    ijae_colors = [color_for_rate(v) for v in ijae_sorted]

    fig, ax = plt.subplots(figsize=(11, 11))

    bars_aerr = ax.barh(
        y + bar_h / 2, aerr_sorted, height=bar_h,
        color=aerr_colors, edgecolor="#2E2E2E", linewidth=0.5,
        hatch="", label="AERR",
    )
    bars_ijae = ax.barh(
        y - bar_h / 2, ijae_sorted, height=bar_h,
        color=ijae_colors, edgecolor="#2E2E2E", linewidth=0.5,
        hatch="///", label="IJAE",
    )

    for bar, val in zip(bars_aerr, aerr_sorted):
        ax.text(val + 1.0, bar.get_y() + bar.get_height() / 2,
                f"{val:.1f}%", va="center", ha="left",
                fontsize=8.5, color="#2E2E2E")
    for bar, val in zip(bars_ijae, ijae_sorted):
        ax.text(val + 1.0, bar.get_y() + bar.get_height() / 2,
                f"{val:.1f}%", va="center", ha="left",
                fontsize=8.5, color="#2E2E2E")

    ax.set_yticks(y)
    ax.set_yticklabels(criteria_sorted, fontsize=10)

    ax.set_xlabel("Compliance Rate (%)", fontsize=12, fontweight="bold")
    ax.set_ylabel("Criterion", fontsize=12, fontweight="bold")
    ax.set_title(
        "Compliance Rate by Transparency-in-Reporting Criterion\n"
        "AERR (n=27) vs IJAE (n=17)",
        fontsize=13, fontweight="bold", pad=15,
    )
    ax.set_xlim(0, 110)
    ax.xaxis.grid(True, linestyle="--", alpha=0.4)
    ax.set_axisbelow(True)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)

    journal_handles = [
        Patch(facecolor="lightgrey", edgecolor="#2E2E2E", hatch="",    label="AERR"),
        Patch(facecolor="lightgrey", edgecolor="#2E2E2E", hatch="///", label="IJAE"),
    ]
    level_handles = [
        Patch(facecolor="#5FAD56", edgecolor="#2E2E2E", label="Excellent (>=75%)"),
        Patch(facecolor="#F2C14E", edgecolor="#2E2E2E", label="Moderate (50-74%)"),
        Patch(facecolor="#F26B5E", edgecolor="#2E2E2E", label="Poor (<50%)"),
    ]
    leg1 = ax.legend(
        handles=journal_handles, title="Journal",
        loc="lower right", bbox_to_anchor=(1.0, 0.05),
        fontsize=9, title_fontsize=10,
    )
    ax.add_artist(leg1)
    ax.legend(
        handles=level_handles, title="Compliance Level",
        loc="lower right", bbox_to_anchor=(1.0, 0.20),
        fontsize=9, title_fontsize=10,
    )

    plt.tight_layout()
    out_path.parent.mkdir(parents=True, exist_ok=True)
    # JPEG has no alpha channel: force a white canvas.
    fig.patch.set_facecolor("white")
    plt.savefig(out_path, dpi=dpi, bbox_inches="tight",
                format="jpeg", pil_kwargs={"quality": 95})
    plt.close(fig)


def main() -> None:
    wide = pd.read_csv(RATES_CSV, index_col="criterion").reindex(CRITERION_ORDER)
    make_figure(wide, OUT_FILE, dpi=600)
    print(f"Saved: {OUT_FILE}")


if __name__ == "__main__":
    main()
