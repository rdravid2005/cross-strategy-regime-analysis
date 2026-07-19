# Research Charter - Cross-Strategy Regime Analysis

## Project Title

Cross-Strategy Regime Analysis

## Research Question

How do different strategy types perform across different market regimes?

## Plain-English Version

Do buy-and-hold and simple daily momentum behave differently depending on whether QQQ is in a high-volatility, low-volatility, uptrend, or downtrend environment?

## Motivation

The first three projects studied regime-aware momentum, opening range breakout robustness, and the backtest-to-reality gap.

This project ties those lessons together by asking whether different strategy types respond differently to market regimes. The first version should stay simple and focus on daily data before adding intraday ORB behavior.

## Initial Hypothesis

Different strategies should perform differently across regimes.

A strategy that works well in low-volatility uptrends may struggle in high-volatility downtrends. The goal is to identify which strategies are most sensitive to regime changes and whether any strategy appears more stable across environments.

## First Version Scope

The first version will use:

- Asset: QQQ
- Data frequency: Daily
- Benchmark: Buy-and-hold QQQ
- Strategy: Simple daily momentum
- Regimes: Volatility regime, trend regime, and combined volatility/trend regime

Intraday ORB should not be added until the daily regime framework is clear.

## Baseline Strategy Definitions

### Buy-and-Hold

Buy QQQ and hold through the test period.

### Simple Daily Momentum

Use a trailing daily momentum signal to determine whether to hold QQQ or cash.

The exact momentum lookback should be defined before the first experiment is run.

## Initial Regime Definitions

### Volatility Regime

Use realized volatility from prior daily returns.

Potential first version:

- Low volatility: realized volatility below a chosen threshold.
- High volatility: realized volatility above a chosen threshold.

### Trend Regime

Use a trailing trend measure based only on prior information.

Potential first version:

- Uptrend: price above a trailing moving average.
- Downtrend: price below a trailing moving average.

### Combined Regimes

Combine volatility and trend labels:

- Low-volatility uptrend
- Low-volatility downtrend
- High-volatility uptrend
- High-volatility downtrend

## Descriptive vs Tradable Analysis

This project must explicitly separate descriptive regime analysis from tradable backtest logic.

Descriptive regime analysis asks how returns behaved under different regime labels.

Tradable backtest logic asks what a strategy could have known and traded at the time.

## What Would Support the Hypothesis?

The hypothesis would be supported if buy-and-hold and daily momentum show meaningfully different return, drawdown, or risk-adjusted behavior across regimes.

For example, momentum may perform better in low-volatility uptrends and worse in high-volatility downtrends.

## What Would Weaken the Hypothesis?

The hypothesis would be weakened if strategy behavior is similar across regimes or if regime labels do not explain meaningful differences in performance.

It would also be weakened if results are highly sensitive to one arbitrary regime definition.

## Key Risks

- Lookahead bias in regime labels.
- Using full-sample thresholds while claiming tradability.
- Overfitting regime definitions after seeing results.
- Confusing descriptive return analysis with a tradable strategy.
- Adding intraday ORB before the daily framework is clean.
- Overstating results from one asset.

## First Exit Test

Before coding, I should be able to explain:

1. The difference between descriptive regime analysis and tradable backtest logic.
2. How volatility regimes are calculated without future data.
3. How trend regimes are calculated without future data.
4. Why buy-and-hold is the benchmark.
5. Why ORB is delayed until the daily framework works.

## Research Standard

The goal is not to find the best-performing parameter set.

The goal is to build a clean framework for comparing strategy behavior across regimes and to document the evidence honestly.
