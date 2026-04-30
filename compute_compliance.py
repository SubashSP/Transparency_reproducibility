"""
Compliance rate by transparency-in-reporting criterion.

Side-by-side comparison: AERR vs IJAE.

Reads raw per-scorer scores from data/scoring_data.xlsx, averages across the
four scorers (Human_1, Human_2, AI, Claude) per paper-criterion cell using
nanmean (so blank cells are treated as missing, not zero), then averages
across all papers in each journal to produce the per-criterion compliance
rate. The figure is saved to figures/compliance_rate_by_criterion.png.

Companion paper: "Advancing Transparency and Reproducibility of Agricultural
Economics Research in India".

Run from the repository root:
    python scripts/compute_compliance.py
"""

from __future__ import annotations

import sys
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.patches import Patch


# ============================================================
# Paths
# ============================================================
REPO_ROOT = Path(__file__).resolve().parent.parent
DATA_FILE = REPO_ROOT / "data" / "scoring_data.xlsx"
FIG_DIR = REPO_ROOT / "figures"
FIG_FILE = FIG_DIR / "compliance_rate_by_criterion.png"
RATES_CSV = FIG_DIR / "compliance_rate_by_criterion.csv"


# ============================================================
# Constants
# ============================================================
JOURNAL_LABELS = {"AERA": "AERR", "IJAE": "IJAE"}
CRITERION_ORDER = [f"C{i}" for i in range(1, 21)]


# ============================================================
# Compliance computation
# ============================================================
def load_scores(path: Path) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Return (long-format scores, criterion codebook)."""
    if not path.exists():
        sys.exit(f"ERROR: data file not found at {path}")
    long = pd.read_excel(path, sheet_name="scores_long")
    codebook = pd.read_excel(path, sheet_name="criterion_labels")
    return long, codebook


def compute_compliance(long: pd.DataFrame) -> pd.DataFrame:
    """
    Compute per-journal, per-criterion compliance rate (percent).

    Step 1: For each (paper, criterion) average across scorers using nanmean
            so missing scorer entries are skipped rather than counted as zero.
    Step 2: For each (journal, criterion) average across all papers in the
            journal.
    Step 3: Multiply by 100 to express as percent.
    """
    # paper x criterion x scorer -> paper x criterion (mean over scorers)
    paper_crit = (
        long.groupby(["paper_id", "journal", "criterion"], dropna=False)["value"]
        .mean()  # nanmean by default in pandas groupby
        .reset_index()
    )

    journal_crit = (
        paper_crit.groupby(["journal", "criterion"])["value"]
        .mean()
        .reset_index()
    )
    journal_crit["compliance_rate_pct"] = journal_crit["value"] * 100.0
    return journal_crit


def to_wide(journal_crit: pd.DataFrame) -> pd.DataFrame:
    """Wide table: rows = criteria (C1..C20), columns = AERR, IJAE."""
    wide = journal_crit.pivot(
        index="criterion", columns="journal", values="compliance_rate_pct"
    )
    wide = wide.rename(columns=JOURNAL_LABELS)
    wide = wide.reindex(CRITERION_ORDER)
    return wide


# ============================================================
# Plotting
# ============================================================
def color_for_rate(rate: float) -> str:
    """Traffic-light colour by compliance rate band."""
    if rate >= 75:
        return "#5FAD56"
    if rate >= 50:
        return "#F2C14E"
    return "#F26B5E"


def make_figure(wide: pd.DataFrame, codebook: pd.DataFrame, out_path: Path,
                use_long_labels: bool = False) -> None:
    """Render the side-by-side compliance chart."""
    aerr_vals = wide["AERR"].values
    ijae_vals = wide["IJAE"].values
    criteria = wide.index.tolist()

    # Sort by overall mean (descending) so worst criteria sit at the bottom.
    overall = (aerr_vals + ijae_vals) / 2.0
    order = np.argsort(-overall)
    criteria_sorted = [criteria[i] for i in order]
    aerr_sorted = aerr_vals[order]
    ijae_sorted = ijae_vals[order]

    label_lookup = dict(zip(codebook["code"], codebook["short_label"]))

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
    if use_long_labels:
        ax.set_yticklabels(
            [f"{c}: {label_lookup[c]}" for c in criteria_sorted], fontsize=9
        )
    else:
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
    plt.savefig(out_path, dpi=200, bbox_inches="tight")
    plt.close(fig)


# ============================================================
# Main
# ============================================================
def main() -> None:
    long, codebook = load_scores(DATA_FILE)
    journal_crit = compute_compliance(long)
    wide = to_wide(journal_crit)

    # Save the rates as CSV alongside the figure for downstream use.
    FIG_DIR.mkdir(parents=True, exist_ok=True)
    wide.round(2).to_csv(RATES_CSV)

    # Write the figure.
    make_figure(wide, codebook, FIG_FILE, use_long_labels=False)

    # Console summary.
    n_aerr = long.loc[long["journal"] == "AERA", "paper_id"].nunique()
    n_ijae = long.loc[long["journal"] == "IJAE", "paper_id"].nunique()
    print(f"Saved figure: {FIG_FILE.relative_to(REPO_ROOT)}")
    print(f"Saved rates : {RATES_CSV.relative_to(REPO_ROOT)}")
    print(f"\nN papers: AERR = {n_aerr}, IJAE = {n_ijae}, Total = {n_aerr + n_ijae}")
    print("\nCompliance rates (%):")
    print(wide.round(2).to_string())
    print(
        "\nNote: C19 (data and code shared) and C20 (README/metadata) are 0 "
        "for both journals as neither has an open data policy."
    )


if __name__ == "__main__":
    main()
