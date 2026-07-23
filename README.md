# Cross-Strategy Regime Analysis

## Overview

This project studies how different strategy types behave across market regimes.

The project is QuantConnect-first. Strategy code is written locally, copied into the QuantConnect cloud project, run in QuantConnect, and then preserved in this repository with experiment logs and research notes.

The first version focuses on daily QQQ behavior. It starts with a buy-and-hold benchmark regime map, then will compare that benchmark against a simple daily momentum strategy. Intraday opening range breakout logic will be added later only after the daily regime framework is clean.

## Research Question

How do different strategy types perform across different market regimes?

## Current Status

EXP-001 through EXP-007 have been run in QuantConnect.

Completed initial experiments:

`EXP-001_QQQ_BUY_AND_HOLD_REGIME_BASELINE`

`EXP-002_QQQ_DAILY_MOMENTUM_REGIME_BASELINE`

`EXP-003_QQQ_DAILY_MOMENTUM_LOW_MED_VOL_FILTER`

`EXP-004_QQQ_DAILY_MOMENTUM_UPTREND_FILTER`

`EXP-005_QQQ_DAILY_MOMENTUM_LOW_VOL_UPTREND_FILTER`

`EXP-006_QQQ_DAILY_MOMENTUM_120D_BASELINE`

`EXP-007_QQQ_DAILY_MOMENTUM_20D_BASELINE`

## Planned First Outputs

- `results/experiment_log.csv`
- `results/exp_001_regime_summary.csv`
- `results/exp_002_regime_summary.csv`
- `results/exp_003_regime_summary.csv`
- `results/exp_004_regime_summary.csv`
- `results/exp_005_regime_summary.csv`
- `results/exp_006_regime_summary.csv`
- `results/exp_007_regime_summary.csv`
- `notes/research_notes.md`

## QuantConnect Workflow

1. Codex writes QuantConnect-compatible Python code.
2. The code is copied into the QuantConnect cloud project.
3. The backtest is run in QuantConnect.
4. Results are recorded locally in `results/` and `notes/`.
5. Exact experiment code is preserved in `src/experiments/`.

## QuantConnect Project

`04 - Cross-Strategy Regime Analysis`

## Repo Structure

```text
cross-strategy-regime-analysis/
├── README.md
├── RESEARCH_CHARTER.md
├── src/
│   ├── main.py
│   └── experiments/
├── results/
│   └── experiment_log.csv
├── figures/
├── notes/
│   └── research_notes.md
└── research/
```
