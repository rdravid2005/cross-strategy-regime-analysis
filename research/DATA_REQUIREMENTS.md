# Optional Local Data Requirements

This file is optional and is not part of the main Project 4 workflow right now.

Project 4 is currently QuantConnect-first:

- Codex writes QuantConnect-compatible Python code.
- The user runs the backtest in QuantConnect.
- Results are recorded in the local repository.

Local CSV-based analysis may be added later if deliberately approved.

## Optional Input File

If a later local helper script is created, it may expect real QQQ daily price data at:

```text
research/qqq_daily.csv
```

Do not use fake data for research conclusions.

## Required Columns

The CSV must contain at least:

```text
Date,Close
```

Extra columns such as `Open`, `High`, `Low`, `Volume`, or `Adjusted Close` are okay, but the first script only uses `Date` and `Close`.

## Example Format

```csv
Date,Close
2020-01-02,216.16
2020-01-03,214.18
```

## Suggested Source

For now, export daily QQQ price data manually from QuantConnect or another trusted source and place it at `research/qqq_daily.csv`.

Later, this project may connect directly to QuantConnect Lean or an API, but the first version is intentionally file-based so the research logic is easy to inspect.
