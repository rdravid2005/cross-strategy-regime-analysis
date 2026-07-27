"""Build the final three-strategy comparison table and figures.

Run this script from the project root:

    python research/build_final_comparison.py

The script uses saved QuantConnect summaries. It does not download data or
rerun any strategy.
"""

from pathlib import Path

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[1]
RESULTS_DIR = PROJECT_ROOT / "results"
FIGURES_DIR = PROJECT_ROOT / "figures"

DAILY_SOURCE = RESULTS_DIR / "exp_010_regime_summary.csv"
ORB_SOURCE = RESULTS_DIR / "exp_014_regime_summary.csv"
COMPARISON_OUTPUT = RESULTS_DIR / "three_strategy_regime_comparison.csv"

STRATEGY_ORDER = [
    "Buy and Hold",
    "Momentum 60D",
    "Corrected Five-Bar ORB",
]
STRATEGY_COLORS = {
    "Buy and Hold": "#2F6B4F",
    "Momentum 60D": "#D39B2A",
    "Corrected Five-Bar ORB": "#3E6FA3",
}
COMBINED_REGIME_ORDER = [
    "high_volatility_downtrend",
    "high_volatility_uptrend",
    "low_volatility_downtrend",
    "low_volatility_uptrend",
]
COMBINED_REGIME_LABELS = {
    "high_volatility_downtrend": "High vol\nDowntrend",
    "high_volatility_uptrend": "High vol\nUptrend",
    "low_volatility_downtrend": "Low vol\nDowntrend",
    "low_volatility_uptrend": "Low vol\nUptrend",
}


def percentage_to_number(value):
    """Convert a CSV percentage such as '13.79%' to numeric percent units."""
    if pd.isna(value) or value == "":
        return None
    return float(str(value).replace("%", ""))


def load_strategy_summaries():
    """Load canonical daily and ORB summaries and standardize their columns."""
    daily = pd.read_csv(DAILY_SOURCE)
    orb = pd.read_csv(ORB_SOURCE)
    orb = orb[orb["Strategy"] == "Corrected Five-Bar ORB"].copy()

    daily["Source End Date"] = "2026-04-24"
    orb["Source End Date"] = "2026-04-28"

    comparison = pd.concat([daily, orb], ignore_index=True, sort=False)
    comparison = comparison[
        comparison["Strategy"].isin(STRATEGY_ORDER)
    ].copy()

    percentage_columns = [
        "Cumulative Return",
        "Annualized Return",
        "Annualized Volatility",
        "Average Daily Return",
        "Win Rate",
    ]
    for column in percentage_columns:
        comparison[column] = comparison[column].map(percentage_to_number)

    comparison = comparison.rename(columns={
        "Experiment ID": "source_experiment",
        "Source End Date": "source_end_date",
        "Strategy": "strategy",
        "Regime Type": "regime_type",
        "Regime": "regime",
        "Days": "days",
        "Cumulative Return": "cumulative_return_pct",
        "Annualized Return": "annualized_return_pct",
        "Annualized Volatility": "annualized_volatility_pct",
        "Sharpe Like": "sharpe_like",
        "Average Daily Return": "average_daily_return_pct",
        "Win Rate": "win_rate_pct",
    })

    output_columns = [
        "source_experiment",
        "source_end_date",
        "strategy",
        "regime_type",
        "regime",
        "days",
        "cumulative_return_pct",
        "annualized_return_pct",
        "annualized_volatility_pct",
        "sharpe_like",
        "average_daily_return_pct",
        "win_rate_pct",
    ]
    comparison = comparison[output_columns]

    duplicate_rows = comparison.duplicated(
        subset=["strategy", "regime_type", "regime"]
    )
    if duplicate_rows.any():
        raise ValueError("Duplicate strategy/regime rows found.")

    expected_rows = len(STRATEGY_ORDER) * 9
    if len(comparison) != expected_rows:
        raise ValueError(
            f"Expected {expected_rows} comparison rows, found "
            f"{len(comparison)}."
        )

    return comparison


def save_combined_regime_figure(comparison):
    """Plot conditional annualized returns across combined regimes."""
    combined = comparison[
        comparison["regime_type"] == "combined_regime"
    ].copy()

    pivot = combined.pivot(
        index="regime",
        columns="strategy",
        values="annualized_return_pct",
    ).reindex(COMBINED_REGIME_ORDER)

    figure, axis = plt.subplots(figsize=(11, 6.5))
    x_positions = range(len(COMBINED_REGIME_ORDER))
    bar_width = 0.24
    offsets = [-bar_width, 0, bar_width]

    for strategy, offset in zip(STRATEGY_ORDER, offsets):
        positions = [position + offset for position in x_positions]
        values = pivot[strategy].tolist()
        bars = axis.bar(
            positions,
            values,
            width=bar_width,
            label=strategy,
            color=STRATEGY_COLORS[strategy],
        )
        axis.bar_label(
            bars,
            labels=[f"{value:.1f}%" for value in values],
            padding=3,
            fontsize=8,
        )

    axis.axhline(0, color="#333333", linewidth=0.8)
    axis.set_title("Strategy Returns Differ Sharply Across Combined Regimes")
    axis.set_ylabel("Conditional annualized return (%)")
    axis.set_xticks(
        list(x_positions),
        [
            COMBINED_REGIME_LABELS[regime]
            for regime in COMBINED_REGIME_ORDER
        ],
    )
    axis.legend(frameon=False, ncols=3, loc="upper right")
    axis.grid(axis="y", color="#D9D9D9", linewidth=0.7, alpha=0.8)
    axis.set_axisbelow(True)
    figure.tight_layout()
    figure.savefig(
        FIGURES_DIR / "combined_regime_annualized_return.png",
        dpi=180,
        bbox_inches="tight",
    )
    plt.close(figure)


def save_overall_risk_return_figure(comparison):
    """Plot each strategy's full-sample return against volatility."""
    overall = comparison[
        comparison["regime_type"] == "overall"
    ].set_index("strategy")

    figure, axis = plt.subplots(figsize=(8.5, 6.5))

    for strategy in STRATEGY_ORDER:
        row = overall.loc[strategy]
        axis.scatter(
            row["annualized_volatility_pct"],
            row["annualized_return_pct"],
            s=130,
            color=STRATEGY_COLORS[strategy],
            edgecolor="white",
            linewidth=1.2,
            zorder=3,
        )
        axis.annotate(
            strategy,
            (
                row["annualized_volatility_pct"],
                row["annualized_return_pct"],
            ),
            xytext=(8, 7),
            textcoords="offset points",
            fontsize=10,
        )

    axis.set_title("Overall Return and Risk Profile")
    axis.set_xlabel("Annualized volatility (%)")
    axis.set_ylabel("Annualized return (%)")
    axis.grid(color="#D9D9D9", linewidth=0.7, alpha=0.8)
    axis.set_axisbelow(True)
    figure.tight_layout()
    figure.savefig(
        FIGURES_DIR / "overall_return_vs_volatility.png",
        dpi=180,
        bbox_inches="tight",
    )
    plt.close(figure)


def main():
    FIGURES_DIR.mkdir(exist_ok=True)
    comparison = load_strategy_summaries()
    comparison.to_csv(COMPARISON_OUTPUT, index=False)
    save_combined_regime_figure(comparison)
    save_overall_risk_return_figure(comparison)

    print(f"Saved {COMPARISON_OUTPUT.relative_to(PROJECT_ROOT)}")
    print("Saved figures/combined_regime_annualized_return.png")
    print("Saved figures/overall_return_vs_volatility.png")


if __name__ == "__main__":
    main()
