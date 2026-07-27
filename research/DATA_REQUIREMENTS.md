# Data and Result Inputs

Project 4 is QuantConnect-first. No local QQQ price file is required.

QuantConnect supplies:

- Daily and minute QQQ market data.
- The backtest engine.
- Order execution and fill modeling.
- Fees and portfolio statistics.

The exact QuantConnect algorithms are preserved under `src/experiments/`.
Reported backtest outputs are stored as structured summaries under `results/`.

## Local Synthesis Inputs

The final local comparison script reads:

```text
results/exp_010_regime_summary.csv
results/exp_014_regime_summary.csv
```

It does not download prices or rerun a backtest. It combines the saved
canonical QuantConnect summaries and produces:

```text
results/three_strategy_regime_comparison.csv
figures/combined_regime_annualized_return.png
figures/overall_return_vs_volatility.png
```

Run it from the project root:

```bash
python -m pip install -r requirements.txt
python research/build_final_comparison.py
```

Raw local price analysis may be added in a future, separately approved research
stage. It is not part of the current project workflow.
