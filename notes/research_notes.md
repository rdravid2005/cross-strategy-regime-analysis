# Research Notes - Cross-Strategy Regime Analysis

## Current Stage

Project initialized.

The first version should focus on a clean daily-data regime framework before adding intraday ORB logic.

## Initial Direction

Start with:

- QQQ buy-and-hold.
- Simple QQQ daily momentum.
- Volatility regimes.
- Trend regimes.
- Combined volatility/trend regimes.

## Important Caution

This project must clearly separate descriptive regime analysis from tradable backtest logic.

Descriptive analysis can explain how returns behaved across regimes.

Tradable strategy logic must use only information available at the time of decision.

## EXP-001 - QQQ Buy-and-Hold Regime Baseline

Experiment ID: `EXP-001_QQQ_BUY_AND_HOLD_REGIME_BASELINE`

QuantConnect project: `04 - Cross-Strategy Regime Analysis`

Purpose: establish a QQQ buy-and-hold benchmark and summarize QQQ daily returns across volatility and trend regimes.

Backtest period: 2020-01-01 to 2026-07-01.

### QuantConnect Performance Statistics

The buy-and-hold benchmark produced:

- CAGR: 19.757%
- Sharpe: 0.605
- Sortino: 0.663
- Max drawdown: 34.800%
- Net profit: 211.712%
- End equity: $311,711.69
- Total orders: 1
- Fees: $2.40

### Regime Summary

The algorithm recorded 1,581 daily return observations. Of those, 1,310 were fully classified into both volatility and trend regimes.

Overall, the close-to-close QQQ return summary showed:

- Cumulative return: 210.98%
- Annualized return: 19.82%
- Annualized volatility: 24.98%
- Sharpe-like ratio: 0.794
- Win rate: 56.04%

The trend regime split was the clearest finding:

- Uptrend days: 20.51% annualized return, 17.66% annualized volatility, 1.161 Sharpe-like ratio.
- Downtrend days: 0.91% annualized return, 33.44% annualized volatility, 0.027 Sharpe-like ratio.

This suggests QQQ buy-and-hold was highly sensitive to the trend regime. Most of the attractive return profile came from uptrend periods, while downtrend periods delivered almost no annualized return with much higher volatility.

The volatility regime split was less decisive:

- High-volatility days had a 19.51% annualized return and 27.34% annualized volatility.
- Low-volatility days had a 12.59% annualized return and 17.63% annualized volatility.
- Both had the same Sharpe-like ratio of 0.714.

This means high-volatility days were not simply bad for buy-and-hold in this test. They produced higher annualized return, but also higher risk.

The combined regime split showed the strongest and weakest environments:

- Best combined regime by Sharpe-like ratio: high-volatility uptrend, with 26.27% annualized return and 1.329 Sharpe-like ratio.
- Second strongest: low-volatility uptrend, with 17.84% annualized return and 1.077 Sharpe-like ratio.
- Weakest: low-volatility downtrend, with -31.99% annualized return and -1.195 Sharpe-like ratio, but only 61 days of data.

### Interpretation

This first benchmark supports the broad Project 4 hypothesis that strategy behavior can vary meaningfully by regime. Even before testing momentum, QQQ buy-and-hold behaved very differently in uptrends versus downtrends.

The result does not prove that regime switching improves performance. It only establishes that the benchmark itself has regime-sensitive return behavior.

This analysis is best described as a tradable-safe descriptive benchmark analysis. The strategy is still buy-and-hold, but daily returns are assigned to regime labels that were known from prior data rather than future data.

### Limitations

- This is only one asset: QQQ.
- The test period begins in 2020, so results may be influenced by the post-2020 market environment.
- The low-volatility downtrend bucket has only 61 days, so that result should not be overstated.
- The Sharpe-like values in the debug summary are calculated from grouped daily returns and are not identical to QuantConnect's built-in portfolio Sharpe.
- This experiment does not yet compare against a momentum strategy.

### Next Experiment

The next logical experiment is:

`EXP-002_QQQ_DAILY_MOMENTUM_REGIME_BASELINE`

That experiment should use the same regime framework but trade a simple daily momentum strategy. Then we can compare whether momentum improves the weak downtrend behavior or gives up too much upside during uptrends.

## EXP-002 - QQQ Daily Momentum Regime Baseline

Experiment ID: `EXP-002_QQQ_DAILY_MOMENTUM_REGIME_BASELINE`

QuantConnect project: `04 - Cross-Strategy Regime Analysis`

Purpose: test a simple QQQ daily momentum strategy and summarize its returns across the same volatility and trend regimes used in EXP-001.

Strategy rule: hold QQQ when trailing 60-day momentum is positive. Otherwise hold cash.

Backtest period: 2020-01-01 to 2026-07-01.

### QuantConnect Performance Statistics

The daily momentum strategy produced:

- CAGR: 15.833%
- Sharpe: 0.657
- Sortino: 0.606
- Max drawdown: 19.600%
- Net profit: 152.649%
- End equity: $252,649.13
- Total orders: 79
- Fees: $150.72
- Momentum exposure: 68.37%

Compared with EXP-001 buy-and-hold:

- CAGR fell from 19.757% to 15.833%.
- Net profit fell from 211.712% to 152.649%.
- Max drawdown improved from 34.800% to 19.600%.
- Sharpe improved from 0.605 to 0.657.
- Sortino fell from 0.663 to 0.606.
- Orders increased from 1 to 79.
- Fees increased from $2.40 to $150.72.

### Regime Summary

The algorithm recorded 1,581 daily return observations. Of those, 1,310 were fully classified into both volatility and trend regimes.

Overall, the daily momentum return summary showed:

- Cumulative return: 132.94%
- Annualized return: 14.43%
- Annualized volatility: 15.53%
- Sharpe-like ratio: 0.929
- Win rate: 39.03%

The lower win rate is not automatically bad here because the strategy spends many days in cash. Cash days count as zero-return days and do not count as wins.

### Volatility Regimes

Momentum performed better in low-volatility regimes than in high-volatility regimes:

- High-volatility days: 6.55% annualized return, 12.73% annualized volatility, 0.515 Sharpe-like ratio.
- Low-volatility days: 15.21% annualized return, 16.06% annualized volatility, 0.947 Sharpe-like ratio.

This is directionally consistent with Project 1: QQQ momentum looked better when avoiding or reducing exposure to higher-volatility periods.

### Trend Regimes

Momentum reduced the damage from downtrend periods compared with buy-and-hold:

- Momentum in downtrends: 3.80% annualized return, 9.46% annualized volatility, 0.402 Sharpe-like ratio.
- Buy-and-hold in downtrends from EXP-001: 0.91% annualized return, 33.44% annualized volatility, 0.027 Sharpe-like ratio.

Momentum also gave up upside in uptrends:

- Momentum in uptrends: 13.77% annualized return, 15.96% annualized volatility, 0.863 Sharpe-like ratio.
- Buy-and-hold in uptrends from EXP-001: 20.51% annualized return, 17.66% annualized volatility, 1.161 Sharpe-like ratio.

This is the core tradeoff so far: momentum improved downside/risk control but reduced participation in strong uptrend returns.

### Combined Regimes

The strongest combined momentum regime was low-volatility uptrend:

- Low-volatility uptrend: 15.89% annualized return, 15.72% annualized volatility, 1.011 Sharpe-like ratio.

The weakest high-level area was high-volatility exposure:

- High-volatility uptrend: 9.49% annualized return, 16.48% annualized volatility, 0.576 Sharpe-like ratio.
- High-volatility downtrend: 2.82% annualized return, 4.32% annualized volatility, 0.653 Sharpe-like ratio.

The high-volatility downtrend Sharpe-like ratio looks decent because volatility was very low for strategy returns, likely because the momentum strategy was often in cash. This should be interpreted as risk reduction, not necessarily strong return generation.

Low-volatility downtrend was positive for momentum, with 7.86% annualized return, but this bucket had only 61 days, so it should not be overstated.

### Interpretation

EXP-002 supports the idea that different strategy types behave differently across regimes.

Buy-and-hold produced higher raw return and higher end equity, but suffered much larger drawdown. Momentum produced lower raw return, but improved drawdown and Sharpe. The regime summaries suggest momentum was most useful as a risk-management rule, especially around downtrends and low-volatility environments.

The result does not prove that the 60-day lookback is optimal. It only shows that this simple preselected momentum rule changed the return/risk profile versus buy-and-hold.

### Descriptive vs Tradable

This is a tradable strategy backtest with descriptive regime summaries.

The strategy itself uses a prior-data momentum signal to decide whether to hold QQQ. The regime summaries assign each strategy return to a regime label known from prior data. This keeps the experiment aligned with the no-lookahead standard.

### Limitations

- This is only one momentum lookback: 60 trading days.
- The strategy was tested only on QQQ.
- The sample starts in 2020, so results may be period-dependent.
- The regime summaries are grouped return diagnostics, not separate live strategies.
- The low-volatility downtrend bucket has only 61 days.
- Momentum improved risk control but did not beat buy-and-hold on raw return.

### Next Experiment

The next logical experiment is:

`EXP-003_QQQ_DAILY_MOMENTUM_LOW_MED_VOL_FILTER`

That experiment would combine the 60-day momentum rule with a volatility regime filter, holding QQQ only when momentum is positive and volatility is not high. This directly connects Project 4 back to Project 1.

## EXP-003 - QQQ Daily Momentum Low-Volatility Filter

Experiment ID: `EXP-003_QQQ_DAILY_MOMENTUM_LOW_MED_VOL_FILTER`

QuantConnect project: `04 - Cross-Strategy Regime Analysis`

Purpose: test whether adding a volatility filter improves the simple QQQ daily momentum strategy from EXP-002.

Strategy rule: hold QQQ when trailing 60-day momentum is positive and the prior volatility regime is low volatility. Otherwise hold cash.

Backtest period: 2020-01-01 to 2026-07-01.

### QuantConnect Performance Statistics

The low-volatility-filtered momentum strategy produced:

- CAGR: 6.331%
- Sharpe: 0.166
- Sortino: 0.120
- Max drawdown: 15.400%
- Net profit: 47.270%
- End equity: $147,270.20
- Total orders: 85
- Fees: $112.62
- Momentum low-volatility exposure: 40.86%

Compared with EXP-002 daily momentum:

- CAGR fell from 15.833% to 6.331%.
- Net profit fell from 152.649% to 47.270%.
- Max drawdown improved from 19.600% to 15.400%.
- Sharpe fell from 0.657 to 0.166.
- Sortino fell from 0.606 to 0.120.
- Exposure fell from 68.37% to 40.86%.

### Regime Summary

The strategy had zero high-volatility return exposure by design:

- High-volatility days: 0.00% cumulative return.
- Low-volatility days: 51.29% cumulative return, 15.21% annualized return, 0.947 Sharpe-like ratio.

This confirms that the volatility filter worked mechanically. It fully avoided high-volatility regimes.

However, the overall strategy result became much weaker because avoiding high volatility removed too many return-producing periods. The strategy lowered volatility and drawdown, but the reduction in return was too large.

### Interpretation

EXP-003 weakens the idea that a strict low-volatility-only filter improves this Project 4 daily momentum strategy.

The result is still useful. It shows that the high-volatility exposure in EXP-002 was not purely harmful. Even though EXP-002's high-volatility regime summary was weaker than its low-volatility summary, removing high-volatility exposure entirely caused the total strategy to underperform badly.

The honest interpretation is:

- The low-volatility filter improved drawdown.
- The low-volatility filter reduced exposure.
- The low-volatility filter materially damaged CAGR, Sharpe, Sortino, and net profit.
- Avoiding all high-volatility periods appears too restrictive in this version.

### Connection To Project 1

This partly differs from Project 1.

Project 1 found that avoiding high-volatility regimes helped some QQQ momentum variants manage risk. In Project 4 EXP-003, the strict binary low-volatility filter was too restrictive and weakened the daily momentum strategy.

That does not invalidate Project 1. It means the exact regime definition and strategy context matter. A volatility filter can help risk control while still being too blunt if it removes too much market participation.

### Descriptive vs Tradable

This is a tradable strategy backtest with descriptive regime summaries.

The position uses prior-day momentum and prior-day volatility regime information. The grouped regime summaries are diagnostic; they describe where the strategy returns occurred.

### Limitations

- This test uses a binary low/high volatility split based on a rolling median.
- The experiment name says low/medium volatility, but the current Project 4 regime framework has only low and high volatility. In this implementation, "low/medium" effectively means "not high," which equals low under the binary regime setup.
- The strategy may be too restrictive because it excludes all high-volatility periods.
- This test does not prove volatility filters are bad; it only shows this specific strict filter weakened performance.

### Next Experiment

The next logical experiment is:

`EXP-004_QQQ_DAILY_MOMENTUM_UPTREND_FILTER`

That experiment would hold QQQ only when 60-day momentum is positive and the prior trend regime is uptrend. This tests whether the trend dimension, which was very important for buy-and-hold in EXP-001, improves the momentum strategy more effectively than the volatility filter.

## EXP-004 - QQQ Daily Momentum Uptrend Filter

Experiment ID: `EXP-004_QQQ_DAILY_MOMENTUM_UPTREND_FILTER`

QuantConnect project: `04 - Cross-Strategy Regime Analysis`

Purpose: test whether adding a trend filter improves the simple QQQ daily momentum strategy from EXP-002.

Strategy rule: hold QQQ when trailing 60-day momentum is positive and the prior trend regime is uptrend. Otherwise hold cash.

Backtest period: 2020-01-01 to 2026-07-01.

### QuantConnect Performance Statistics

The uptrend-filtered momentum strategy produced:

- CAGR: 11.612%
- Sharpe: 0.484
- Sortino: 0.428
- Max drawdown: 15.200%
- Net profit: 99.925%
- End equity: $199,925.33
- Total orders: 77
- Fees: $119.66
- Momentum uptrend exposure: 59.01%

Compared with EXP-002 daily momentum:

- CAGR fell from 15.833% to 11.612%.
- Net profit fell from 152.649% to 99.925%.
- Max drawdown improved from 19.600% to 15.200%.
- Sharpe fell from 0.657 to 0.484.
- Sortino fell from 0.606 to 0.428.
- Exposure fell from 68.37% to 59.01%.

Compared with EXP-003 low-volatility-filtered momentum:

- CAGR improved from 6.331% to 11.612%.
- Net profit improved from 47.270% to 99.925%.
- Max drawdown was similar, improving slightly from 15.400% to 15.200%.
- Sharpe improved from 0.166 to 0.484.
- Sortino improved from 0.120 to 0.428.

### Regime Summary

The strategy had zero downtrend exposure by design:

- Downtrend days: 0.00% cumulative return.
- Uptrend days: 66.96% cumulative return, 13.77% annualized return, 0.863 Sharpe-like ratio.

The volatility split showed that returns still came mainly from low-volatility regimes:

- High-volatility days: 5.28% annualized return, 12.41% annualized volatility, 0.425 Sharpe-like ratio.
- Low-volatility days: 14.49% annualized return, 15.06% annualized volatility, 0.962 Sharpe-like ratio.

The strongest combined regime remained low-volatility uptrend:

- Low-volatility uptrend: 15.89% annualized return, 15.72% annualized volatility, 1.011 Sharpe-like ratio.

### Interpretation

EXP-004 shows that the trend filter was more useful than the strict volatility filter, but it still did not improve the overall strategy versus plain daily momentum.

The trend filter reduced drawdown and avoided downtrend exposure, which is intuitively attractive. However, it also reduced return and risk-adjusted performance compared with EXP-002. This suggests that the plain 60-day momentum rule may already capture some trend information, so adding a 200-day trend filter may be partly redundant or too restrictive.

The result supports the broader Project 4 hypothesis that strategy behavior differs across regimes. But it weakens the idea that simply adding a regime filter automatically improves a strategy.

### Current Four-Experiment Takeaway

So far:

- EXP-001 buy-and-hold had the highest raw return and end equity, but the largest drawdown.
- EXP-002 plain daily momentum had lower return than buy-and-hold, but improved drawdown and Sharpe.
- EXP-003 low-volatility-filtered momentum was too restrictive and performed worst overall.
- EXP-004 uptrend-filtered momentum was better than EXP-003, but still worse than EXP-002 on return and Sharpe.

The best strategy so far depends on the objective:

- Best raw return: EXP-001 buy-and-hold.
- Best drawdown control: EXP-004 uptrend-filtered momentum, slightly better than EXP-003.
- Best Sharpe: EXP-002 plain daily momentum.

The honest current conclusion is that simple daily momentum improved risk-adjusted performance versus buy-and-hold, but adding strict volatility or trend filters reduced too much exposure.

### Descriptive vs Tradable

This is a tradable strategy backtest with descriptive regime summaries.

The position uses prior-day momentum and prior-day trend regime information. The grouped regime summaries describe where strategy returns occurred; they are diagnostics, not separate strategy claims.

### Limitations

- This test uses only one trend definition: close above the 200-day moving average.
- The strategy may be redundant with the 60-day momentum rule because both are trend-following concepts.
- The result is only for QQQ from 2020-01-01 to 2026-07-01.
- This does not yet test robustness across momentum lookbacks, assets, or subperiods.

### Next Step

This is a good first Git checkpoint.

Before adding more experiments, the repo should be committed with EXP-001 through EXP-004 preserved and documented.

## EXP-005 - QQQ Daily Momentum Low-Volatility Uptrend Filter

Experiment ID: `EXP-005_QQQ_DAILY_MOMENTUM_LOW_VOL_UPTREND_FILTER`

QuantConnect project: `04 - Cross-Strategy Regime Analysis`

Purpose: test whether the strongest observed combined regime, low-volatility uptrend, improves the simple QQQ daily momentum strategy when used as a trading filter.

Strategy rule: hold QQQ when trailing 60-day momentum is positive, the prior volatility regime is low volatility, and the prior trend regime is uptrend. Otherwise hold cash.

Backtest period shown in QuantConnect output: 2020-01-01 to 2026-04-22.

### QuantConnect Performance Statistics

The low-volatility uptrend filtered momentum strategy produced:

- CAGR: 6.257%
- Sharpe: 0.166
- Sortino: 0.122
- Max drawdown: 15.400%
- Net profit: 46.676%
- End equity: $146,676.26
- Total orders: 81
- Fees: $106.21
- Momentum low-volatility uptrend exposure: 39.04%

QuantConnect also showed two execution warnings:

- One rebalance recommendation was ignored because it would have resulted in a single-share trade.
- A market order submitted while the market was closed was converted to a MarketOnOpen order.

These warnings should be noted, but they do not change the main interpretation. This is a daily-resolution strategy and QuantConnect handled the order timing.

### Regime Summary

The algorithm recorded 1,583 daily return observations. Of those, 1,312 were fully classified into both volatility and trend regimes.

The strategy only produced returns in the low-volatility uptrend bucket by design:

- Low-volatility uptrend: 48.54% cumulative return, 15.89% annualized return, 15.72% annualized volatility, 1.011 Sharpe-like ratio.
- All other combined regimes: 0.00% cumulative return because the strategy was in cash.

Overall, however, the full strategy result was weak:

- Cumulative return: 48.54%
- Annualized return: 6.50%
- Annualized volatility: 10.28%
- Sharpe-like ratio: 0.632
- Win rate: 22.05%

The low overall win rate is mainly because the strategy spends many days in cash. Cash days count as zero-return days and do not count as wins.

### Interpretation

EXP-005 confirms that the combined low-volatility uptrend filter was too restrictive.

The selected regime looked strong when isolated, but using it as a trading filter produced weak overall performance because exposure fell to only 39.04%. The filter avoided higher-risk periods, but it also removed too much return opportunity.

Compared with EXP-002 plain daily momentum:

- CAGR fell from 15.833% to 6.257%.
- Net profit fell from 152.649% to 46.676%.
- Sharpe fell from 0.657 to 0.166.
- Drawdown improved from 19.600% to 15.400%.

Compared with EXP-004 uptrend-filtered momentum, EXP-005 was worse on CAGR, Sharpe, Sortino, net profit, and end equity, while having similar drawdown.

The lesson is important: a regime bucket can look attractive descriptively, but a strict trading filter based on that bucket can still be unattractive if it removes too much exposure.

### Current Five-Experiment Takeaway

So far:

- EXP-001 buy-and-hold had the highest raw return and end equity.
- EXP-002 plain daily momentum had the best Sharpe among the tested strategies and materially reduced drawdown versus buy-and-hold.
- EXP-003 low-volatility-filtered momentum was too restrictive.
- EXP-004 uptrend-filtered momentum was better than EXP-003 but still worse than EXP-002.
- EXP-005 low-volatility uptrend momentum was also too restrictive and did not improve on EXP-002 or EXP-004.

The strongest current result is not a heavily filtered regime strategy. It is the simpler 60-day daily momentum strategy from EXP-002.

### Descriptive vs Tradable

This is a tradable strategy backtest with descriptive regime summaries.

The strategy uses prior-day momentum, volatility, and trend information. The grouped regime summaries describe where the strategy returns occurred, but should not be treated as separate robustness tests.

### Limitations

- This test combines filters after observing that low-volatility uptrend was a strong bucket, so it should be treated cautiously as a follow-up experiment rather than proof.
- The combined filter is very restrictive and may underperform because of low exposure rather than bad trade selection.
- Results remain limited to QQQ and the 2020-2026 test period.
- This does not yet test robustness across momentum lookbacks or alternative regime thresholds.

### Next Step

This is a good second Git checkpoint after EXP-005.

The next research step should be a small robustness test rather than another stricter filter. A reasonable candidate is testing the plain daily momentum strategy with a different momentum lookback, such as 120 days, to see whether EXP-002 depends heavily on the 60-day parameter.

## EXP-006 - QQQ Daily Momentum 120-Day Baseline

Experiment ID: `EXP-006_QQQ_DAILY_MOMENTUM_120D_BASELINE`

QuantConnect project: `04 - Cross-Strategy Regime Analysis`

Purpose: test whether the plain QQQ daily momentum result from EXP-002 is sensitive to the momentum lookback window.

Strategy rule: hold QQQ when trailing 120-day momentum is positive. Otherwise hold cash.

Backtest period shown in QuantConnect output: 2020-01-01 to 2026-04-22.

### QuantConnect Performance Statistics

The 120-day daily momentum strategy produced:

- CAGR: 14.867%
- Sharpe: 0.588
- Sortino: 0.572
- Max drawdown: 25.500%
- Net profit: 139.831%
- End equity: $239,830.61
- Total orders: 46
- Fees: $87.04
- Momentum exposure: 72.52%

QuantConnect also showed two execution warnings:

- One rebalance recommendation was ignored because it would have resulted in a single-share trade.
- A market order submitted while the market was closed was converted to a MarketOnOpen order.

These are worth noting, but they do not change the main interpretation.

### Regime Summary

The algorithm recorded 1,583 daily return observations. Of those, 1,312 were fully classified into both volatility and trend regimes.

Overall, the 120-day momentum return summary showed:

- Cumulative return: 141.98%
- Annualized return: 15.10%
- Annualized volatility: 15.88%
- Sharpe-like ratio: 0.951
- Win rate: 41.44%

The volatility regime split remained similar to the prior momentum experiments:

- High-volatility days: 8.72% annualized return, 15.70% annualized volatility, 0.556 Sharpe-like ratio.
- Low-volatility days: 16.01% annualized return, 15.23% annualized volatility, 1.051 Sharpe-like ratio.

This again suggests that QQQ momentum behaved better in low-volatility regimes than high-volatility regimes.

The trend regime split was more mixed:

- Uptrend days: 20.09% annualized return, 17.21% annualized volatility, 1.167 Sharpe-like ratio.
- Downtrend days: -8.08% annualized return, 6.95% annualized volatility, -1.162 Sharpe-like ratio.

Unlike the 60-day momentum strategy, the 120-day momentum strategy performed poorly in downtrends. This suggests the longer lookback may react more slowly when the market regime deteriorates.

### Interpretation

EXP-006 gives partial support to the plain momentum idea.

The 120-day momentum strategy remained positive, had a strong cumulative return, and traded less frequently than the 60-day version. This weakens the concern that EXP-002 only worked because of one narrow 60-day parameter.

However, 120-day momentum was not clearly better than 60-day momentum. Compared with EXP-002, it had:

- Slightly lower CAGR.
- Lower QuantConnect Sharpe.
- Lower Sortino.
- Much larger max drawdown.
- Lower turnover and fees.

The biggest concern is drawdown. EXP-006 had a 25.500% drawdown versus 19.600% for EXP-002, which suggests the longer momentum window may reduce responsiveness.

### Current Six-Experiment Takeaway

So far, the strongest overall strategy remains EXP-002, the simple 60-day daily momentum baseline.

The filtered strategies reduced exposure and drawdown, but generally hurt return and Sharpe. The 120-day robustness test supports the general momentum concept, but it did not improve on the 60-day version.

The current evidence suggests:

- QQQ buy-and-hold maximized raw return.
- Simple momentum improved drawdown and risk-adjusted performance versus buy-and-hold.
- Strict regime filters were too restrictive.
- Momentum lookback matters, but the result is not completely isolated to 60 days.

### Descriptive vs Tradable

This is a tradable strategy backtest with descriptive regime summaries.

The strategy uses a prior-data 120-day momentum signal. Regime summaries classify strategy returns using prior-data volatility and trend labels.

### Limitations

- EXP-006 used the latest QuantConnect output ending 2026-04-22, while earlier EXP-001 through EXP-004 were originally logged through 2026-07-01 based on prior outputs. Comparisons should account for that date mismatch.
- Only one alternate momentum lookback was tested.
- Results remain limited to QQQ and the 2020-2026 period.
- This does not yet test shorter momentum, such as 20 days, or subperiod robustness.

### Next Step

The next logical robustness test is:

`EXP-007_QQQ_DAILY_MOMENTUM_20D_BASELINE`

That would test a shorter, faster momentum lookback. If 20-day momentum is much worse, then the strategy may prefer medium/longer trend signals. If it is similar or better, then the momentum effect may be more robust across lookbacks.

## EXP-007 - QQQ Daily Momentum 20-Day Baseline

Experiment ID: `EXP-007_QQQ_DAILY_MOMENTUM_20D_BASELINE`

QuantConnect project: `04 - Cross-Strategy Regime Analysis`

Purpose: test whether the plain QQQ daily momentum result is sensitive to a shorter, faster momentum lookback.

Strategy rule: hold QQQ when trailing 20-day momentum is positive. Otherwise hold cash.

Backtest period shown in QuantConnect output: 2020-01-01 to 2026-04-24.

### QuantConnect Performance Statistics

The 20-day daily momentum strategy produced:

- CAGR: 18.113%
- Sharpe: 0.761
- Sortino: 0.717
- Max drawdown: 27.100%
- Net profit: 186.213%
- End equity: $286,212.74
- Total orders: 143
- Fees: $280.18
- Momentum exposure: 64.67%

QuantConnect warned that a market order submitted while the market was closed was converted to a MarketOnOpen order. This warning exposes an execution-timing distinction discussed below.

### Regime Summary

The algorithm recorded 1,585 daily return observations, including 1,314 observations fully classified into both volatility and trend regimes.

The synthetic 20-day momentum return series showed:

- Cumulative return: 181.09%
- Annualized return: 17.86%
- Annualized volatility: 15.36%
- Sharpe-like ratio: 1.163
- Win rate: 36.59%

Performance by volatility regime was positive in both buckets:

- High volatility: 15.30% annualized return and 1.060 Sharpe-like ratio.
- Low volatility: 12.90% annualized return and 0.912 Sharpe-like ratio.

Performance was also positive across the broad trend labels:

- Downtrend: 15.39% annualized return and 0.946 Sharpe-like ratio.
- Uptrend: 13.51% annualized return and 0.993 Sharpe-like ratio.

The strongest combined result was high-volatility downtrend, with a 23.85% annualized return and 1.437 Sharpe-like ratio. Low-volatility downtrend was negative, but it contained only 61 observations, so that estimate is less reliable.

### Momentum Lookback Comparison

Among the tested momentum lookbacks, the 20-day version produced the strongest QuantConnect CAGR and Sharpe:

- 20-day: 18.113% CAGR, 0.761 Sharpe, 27.100% drawdown, 143 orders, and $280.18 in fees.
- 60-day: 15.833% CAGR, 0.657 Sharpe, 19.600% drawdown, 79 orders, and $150.72 in fees.
- 120-day: 14.867% CAGR, 0.588 Sharpe, 25.500% drawdown, 46 orders, and $87.04 in fees.

The shorter signal improved return and Sharpe in this sample, but it also increased trading, fees, and drawdown. This is evidence that momentum remained effective across the three predefined lookbacks, not proof that 20 days is an optimal parameter.

### Execution and Measurement Audit

The QuantConnect portfolio produced a 186.213% net profit, while the algorithm's synthetic close-to-close regime series produced a 181.09% cumulative return.

The code calculates a momentum signal after a daily close, applies that signal to the next close-to-close return in its synthetic records, and submits the associated portfolio order when the next daily bar arrives. QuantConnect reports that such orders are submitted after the market close and converted to MarketOnOpen orders. Therefore, the synthetic regime series and the actual portfolio fills do not have perfectly aligned exposure timing.

This does not erase the experiment, because all three lookback tests used the same framework and remain useful as controlled comparisons. It does mean the custom regime statistics should not yet be treated as exact decompositions of the QuantConnect portfolio return.

### Current Interpretation

EXP-007 strengthens the evidence that the general QQQ momentum result is not isolated to one lookback. All three plain momentum versions were profitable.

The 20-day signal was more responsive and captured more return in this sample, particularly during high-volatility downtrends. Its higher drawdown and trading activity prevent us from simply declaring it superior. The 60-day baseline remains a reasonable representative specification because it was selected before these robustness tests and offers the lowest drawdown of the three.

### Descriptive vs Tradable

The QuantConnect portfolio is a tradable backtest under QuantConnect's MarketOnOpen conversion behavior. The custom regime summaries are descriptive synthetic return calculations using prior-data labels and signals. Their timing needs to be aligned with actual fills before they can be described as exact portfolio regime attribution.

### Limitations

- The test period ends on 2026-04-24, while prior experiments have slightly different endpoints.
- Only QQQ was tested.
- Three lookbacks provide useful neighboring checks but do not establish universal parameter robustness.
- The 20-day signal incurred substantially more orders and fees.
- The custom regime return series is not perfectly aligned with QuantConnect's actual MarketOnOpen fills.
- Low-volatility downtrend contains only 61 classified days.

### Next Step

Before building the direct buy-and-hold versus momentum comparison, the next experiment should audit and correct signal, fill, and return-attribution timing. After that correction, both strategy return streams can be compared under identical regime labels without mixing synthetic close-to-close exposure with a differently timed QuantConnect portfolio.

## EXP-008 - QQQ Daily Momentum Execution Alignment Audit

Experiment ID: `EXP-008_QQQ_DAILY_MOMENTUM_EXECUTION_ALIGNMENT_AUDIT`

QuantConnect project: `04 - Cross-Strategy Regime Analysis`

Purpose: determine whether custom regime returns can be calculated from actual QuantConnect portfolio values and reconciled to QuantConnect's reported performance.

Intended execution rule: calculate the 60-day momentum signal after the daily close and rebalance shortly after the next market open.

Observed execution rule: QuantConnect automatically converted the scheduled market orders to MarketOnClose orders because the algorithm subscribed only to daily-resolution data and the available price was stale during market hours.

Backtest period shown in QuantConnect output: 2020-01-01 to 2026-04-24.

### QuantConnect Performance Statistics

- CAGR: 15.974%
- Sharpe: 0.657
- Sortino: 0.605
- Max drawdown: 20.400%
- Net profit: 155.007%
- End equity: $255,007.43
- Total orders: 63
- Fees: $136.66
- Momentum target exposure: 68.45%

### Alignment Result

The custom actual portfolio series produced a cumulative return of 155.01%. QuantConnect reported net profit of 155.007% and end equity of $255,007.43.

The near-exact reconciliation confirms that daily changes in `total_portfolio_value` can be used to attribute the actual backtested strategy return to custom regimes. This is a material improvement over multiplying a target-position flag by QQQ's close-to-close return.

The legacy synthetic series produced only 139.09% cumulative return, creating a 15.91 percentage-point gap versus the actual portfolio series. The gap demonstrates that execution timing, overnight exposure, fees, and QuantConnect fill behavior materially affect the return path.

### Actual Portfolio Regime Results

The actual portfolio series produced:

- Overall: 16.05% annualized return, 15.46% annualized volatility, and 1.038 Sharpe-like ratio.
- High volatility: 11.18% annualized return and 0.873 Sharpe-like ratio.
- Low volatility: 17.59% annualized return and 1.098 Sharpe-like ratio.
- Downtrend: -2.32% annualized return and -0.247 Sharpe-like ratio.
- Uptrend: 20.55% annualized return and 1.288 Sharpe-like ratio.

The combined regimes reinforced the same pattern. High-volatility uptrend and low-volatility uptrend were strong, while both downtrend combinations were negative or nearly flat. The low-volatility downtrend bucket remained particularly weak, although it contained only 61 observations.

### Interpretation

EXP-008 successfully validates the portfolio-value return-attribution method, but it does not validate the intended next-open execution rule.

This distinction matters. The algorithm's log described next-open rebalancing, while QuantConnect actually used MarketOnClose orders. The resulting backtest remains useful as an execution audit, but it should not be represented as a next-open strategy.

The result also changes the earlier downtrend interpretation. Once regime performance is measured from actual portfolio value, the 60-day momentum strategy was slightly negative in downtrends rather than clearly positive. Momentum still reduced downside materially relative to continuously holding QQQ, but it did not generate a strong positive downtrend return.

### Descriptive vs Tradable

The regime attribution is now tied to the actual backtested portfolio and is therefore a valid description of this QuantConnect backtest. The automatic order conversion is specific to backtesting with stale daily-resolution prices and would not be applied the same way in live trading, according to QuantConnect's warning. The observed strategy therefore needs an explicit order type before its execution rule can be considered reproducible across environments.

### Limitations

- Scheduled market orders did not execute at the intended next-open time.
- QuantConnect automatically changed the order type because only daily-resolution data was available.
- The backtest and live behavior would differ if the same market-order instruction were used unchanged.
- Earlier regime summaries used synthetic close-to-close returns and should be treated as controlled descriptive comparisons rather than exact portfolio attribution.
- The experiment remains limited to QQQ and one sample period.

### Next Step

The next experiment should specify the execution order explicitly. The cleanest daily-data design is to calculate the signal after the close and submit an explicit MarketOnOpen order for the next session. The resulting daily portfolio-value returns can then be attributed to prior-data regimes using the method validated here.

## EXP-009 - QQQ Daily Momentum Explicit MarketOnOpen Baseline

Experiment ID: `EXP-009_QQQ_DAILY_MOMENTUM_EXPLICIT_MOO_BASELINE`

QuantConnect project: `04 - Cross-Strategy Regime Analysis`

Purpose: establish a reproducible 60-day momentum baseline with an explicit next-session MarketOnOpen execution rule and actual portfolio-value regime attribution.

Strategy rule: after each daily close, calculate trailing 60-day QQQ momentum. Submit an explicit MarketOnOpen order for the next session, holding QQQ when momentum is positive and cash otherwise.

Backtest period shown in QuantConnect output: 2020-01-01 to 2026-04-24.

### QuantConnect Performance Statistics

- CAGR: 13.729%
- Sharpe: 0.538
- Sortino: 0.502
- Max drawdown: 14.300%
- Net profit: 125.381%
- End equity: $225,380.60
- Total orders: 63
- Fees: $132.43
- Momentum target exposure: 68.45%

No order-conversion or stale-price warnings were reported.

### Execution Alignment Result

The custom actual portfolio series produced a 125.38% cumulative return. QuantConnect reported 125.381% net profit and ending equity of $225,380.60.

This near-exact match confirms that the explicit MarketOnOpen implementation and daily portfolio-value attribution are aligned. EXP-009 is therefore the cleanest reproducible momentum implementation in the project so far.

The synthetic close-to-close series produced 139.09%, overstating the actual next-open result by 13.71 percentage points. The difference reflects the fact that a signal calculated at today's close cannot earn the overnight return that occurs before its next-open fill. Existing positions also remain exposed through the overnight period before an exit order fills.

### Actual Portfolio Regime Results

- Overall: 13.79% annualized return, 15.54% annualized volatility, and 0.888 Sharpe-like ratio.
- High volatility: 5.53% annualized return and 0.424 Sharpe-like ratio.
- Low volatility: 16.04% annualized return and 0.999 Sharpe-like ratio.
- Downtrend: 2.56% annualized return and 0.269 Sharpe-like ratio.
- Uptrend: 14.14% annualized return and 0.879 Sharpe-like ratio.

Low-volatility uptrend remained the strongest well-populated combined regime, with a 16.37% annualized return and 1.042 Sharpe-like ratio. High-volatility downtrend was nearly flat. Low-volatility downtrend was positive, but it contained only 61 observations and should not receive much weight.

### Comparison With EXP-008

EXP-008's automatically converted MarketOnClose implementation produced a 15.974% CAGR, 0.657 Sharpe, and 20.400% drawdown. EXP-009's explicit next-open implementation produced a 13.729% CAGR, 0.538 Sharpe, and 14.300% drawdown.

MarketOnOpen execution reduced both return and drawdown. This is not evidence that one fill convention is universally better. It demonstrates that a daily momentum strategy's measured performance depends materially on whether a signal is filled at the close or at the next open.

### Interpretation

EXP-009 resolves the execution ambiguity uncovered in EXP-008. The result is weaker than the earlier synthetic and automatically converted versions, but it is more defensible because the code, order type, fill timing, and custom return attribution agree.

The strategy continued to behave best in low-volatility and uptrend regimes. It provided limited positive performance in downtrends rather than a strong independent return source. Its main benefit versus buy-and-hold remains lower exposure and drawdown, not superior raw return.

### Descriptive vs Tradable

This is a tradable QuantConnect backtest with an explicit next-session MarketOnOpen execution rule. Its regime summaries use actual portfolio returns and regime labels known before the attributed trading day.

### Limitations

- Opening auction fills may differ from ordinary market-order fills after the open.
- MarketOnOpen orders can be rejected if an overnight price gap makes the submitted quantity unaffordable.
- The test remains limited to QQQ and one historical period.
- Regime buckets are uneven, especially low-volatility downtrend.
- Earlier lookback comparisons used the older execution framework and should not be treated as exact comparisons to this corrected baseline.

### Next Step

EXP-008 and EXP-009 should be committed together as an execution-alignment checkpoint. After that, the next experiment should compare the explicit-MOO 60-day momentum portfolio against QQQ buy-and-hold under the same prior-data regime labels.

## EXP-010 - QQQ Buy-and-Hold vs Momentum Regime Comparison

Experiment ID: `EXP-010_QQQ_BH_VS_MOMENTUM_REGIME_COMPARISON`

QuantConnect project: `04 - Cross-Strategy Regime Analysis`

Purpose: directly compare QQQ buy-and-hold with the execution-aligned 60-day momentum strategy under identical prior-data volatility and trend regime labels.

Momentum execution: calculate the 60-day momentum signal after the daily close and submit an explicit MarketOnOpen order for the next session.

Backtest period shown in QuantConnect output: 2020-01-01 to 2026-04-24.

### Overall Comparison

Buy-and-hold produced a 219.19% cumulative return, 20.27% annualized return, 24.97% annualized volatility, and 0.812 Sharpe-like ratio.

Momentum produced a 125.38% cumulative return, 13.79% annualized return, 15.54% annualized volatility, and 0.888 Sharpe-like ratio while targeting QQQ exposure on 68.45% of days.

Momentum trailed buy-and-hold by 93.81 percentage points of cumulative return. Its purpose was therefore not return maximization. It exchanged substantial upside for lower exposure and volatility. QuantConnect reported a 14.300% momentum drawdown, compared with approximately 34.800% in the earlier buy-and-hold benchmark, although those drawdowns came from separate backtests with slightly different endpoints.

The custom Sharpe-like statistic is annualized return divided by annualized volatility without the same adjustments used by QuantConnect. It should not be described as QuantConnect Sharpe. QuantConnect reported a 0.538 Sharpe for momentum, while the earlier buy-and-hold backtest reported 0.605.

### Volatility Regime Comparison

In low volatility, momentum returned 16.04% annualized with 16.06% volatility and a 0.999 Sharpe-like ratio. Buy-and-hold returned 12.59% annualized with 17.63% volatility and a 0.714 Sharpe-like ratio. This was the clearest environment in which momentum outperformed buy-and-hold on both conditional return and volatility.

In high volatility, momentum returned only 5.53% annualized versus 20.73% for buy-and-hold. Momentum cut volatility from 27.29% to 13.04%, but its 0.424 Sharpe-like ratio remained below buy-and-hold's 0.759. The 60-day signal appears to miss substantial upside during fast, volatile recoveries.

### Trend Regime Comparison

During uptrends, buy-and-hold returned 21.21% annualized versus 14.14% for momentum. Buy-and-hold also had the stronger Sharpe-like ratio. Continuous exposure was more effective when the broad trend was already favorable.

During downtrends, momentum returned 2.56% annualized with 9.53% volatility. Buy-and-hold returned 0.91% annualized with 33.44% volatility. Momentum's advantage was primarily capital preservation rather than a strong independent downtrend return.

### Combined Regime Comparison

- High-volatility uptrend strongly favored buy-and-hold: 28.45% annualized versus 9.68% for momentum.
- Low-volatility uptrend was close: 17.84% for buy-and-hold versus 16.37% for momentum, with momentum carrying slightly less volatility.
- High-volatility downtrend left momentum nearly flat with very low volatility, while buy-and-hold earned more return but with 34.90% volatility.
- Low-volatility downtrend favored momentum, but the bucket contained only 61 observations and is not strong enough for a robust conclusion.

### Interpretation

EXP-010 supports the initial hypothesis that different strategies behave differently across regimes.

Buy-and-hold remained the stronger return-maximizing strategy. Momentum behaved as a defensive exposure filter: it helped most in low-volatility and downtrend environments, reduced risk materially, and missed substantial upside during high-volatility uptrends.

A proportional conclusion is that the 60-day momentum rule can improve the shape of exposure, especially for drawdown-sensitive investors, but it did not replace buy-and-hold as the best way to maximize long-run QQQ return.

### Descriptive vs Tradable

The momentum series is a tradable QuantConnect portfolio using explicit next-session MarketOnOpen orders. Buy-and-hold is represented descriptively by QQQ close-to-close returns rather than a second separately funded portfolio. This is a reasonable benchmark approximation, but it excludes the negligible one-time benchmark trade fee.

### Statistical Cautions

- Regime days are non-contiguous. Conditional cumulative and annualized returns describe the collection of days assigned to each regime, not a standalone calendar-period strategy CAGR.
- Regime cumulative returns are not additive across buckets.
- Momentum cash days have zero returns and are counted as non-winning days, so its daily win rate is not a trade win rate.
- The first 271 daily observations were part of indicator warm-up and were excluded from fully classified regime summaries but included in overall results.
- Low-volatility downtrend contains only 61 observations.

### Next Step

The next experiment should test temporal robustness by comparing buy-and-hold and momentum over two predefined subperiods: 2020-2022 and 2023-2026. Strategy parameters and regime definitions should remain unchanged.

## EXP-011 - Buy-and-Hold vs Momentum Subperiod Robustness

Experiment ID: `EXP-011_QQQ_BH_VS_MOMENTUM_SUBPERIOD_ROBUSTNESS`

QuantConnect project: `04 - Cross-Strategy Regime Analysis`

Purpose: test whether the conclusions from EXP-010 persist across two predefined periods without changing the strategy, execution, or regime parameters.

Subperiods:

- 2020-01-01 through 2022-12-31.
- 2023-01-01 through the available backtest end on 2026-04-24.

### Full-Period Portfolio Check

The QuantConnect statistics remained identical to the execution-aligned baseline: 13.729% CAGR, 0.538 Sharpe, 0.502 Sortino, 14.300% drawdown, 125.381% net profit, 63 orders, $132.43 in fees, and $225,380.60 end equity.

This confirms that EXP-011 changed only the reporting split and did not change the traded strategy.

### 2020-2022 Results

Momentum was exposed on 56.42% of days. It returned 33.90% cumulatively, compared with 25.60% for buy-and-hold. Momentum therefore outperformed by 8.30 percentage points.

Momentum also had much lower annualized volatility: 15.92% versus 29.59% for buy-and-hold. Its Sharpe-like ratio was 0.643 versus 0.267 for buy-and-hold.

Within the classified observations, momentum lost less than buy-and-hold in both volatility regimes and during downtrends. In downtrends, momentum returned -6.90% cumulatively versus -18.88% for buy-and-hold. This supports the interpretation that momentum provided defensive value during the more difficult 2020-2022 environment.

### 2023-2026 Results

Momentum exposure rose to 79.40%. Momentum returned 68.32% cumulatively, while buy-and-hold returned 154.13%. Momentum underperformed by 85.81 percentage points.

Buy-and-hold also had the stronger return-to-volatility result: a 1.649 Sharpe-like ratio versus 1.128 for momentum. Momentum still reduced annualized volatility from 19.85% to 15.19%, but the reduction was not enough to compensate for the missed return.

The largest difference appeared in high volatility. Buy-and-hold returned 63.83% cumulatively during high-volatility observations versus 11.57% for momentum. In low volatility, results were much closer: 55.12% for buy-and-hold versus 50.86% for momentum.

### Temporal Robustness Interpretation

The evidence supports regime sensitivity but weakens any claim that momentum is a consistently superior strategy.

Momentum was valuable in the stressful 2020-2022 period, when reducing exposure limited damage. It was much less effective during the strong 2023-2026 market, when continuous exposure captured powerful advances and volatile rebounds.

The result is consistent with momentum acting as a defensive allocation rule. It can improve outcomes when avoiding losses matters, but it creates opportunity cost during sustained or rapidly recovering bull markets.

### Classification Asymmetry

Only 484 of the 755 observations in 2020-2022 were fully classified, because the 20-day volatility estimate and especially the rolling 252-observation volatility threshold required a long warm-up. All 830 observations in 2023-2026 were classified.

Therefore, the overall subperiod comparison is valid across both full periods, but the first period's regime summaries do not represent all of 2020-2022. They primarily describe the post-warm-up portion of that period. This prevents a perfectly symmetric regime comparison between the two subperiods.

### Statistical Cautions

- The 2023-2026 downtrend bucket contains only 76 non-contiguous days.
- Its annualized figures, including the 107.60% buy-and-hold annualized return, are mechanical conditional annualizations and should not be interpreted as calendar CAGRs.
- Regime cumulative returns are not additive.
- Momentum win rates include zero-return cash days and are not trade win rates.
- The two periods contain different market environments and are not independent statistical samples.

### Conclusion

EXP-011 supports the project's main hypothesis: strategy performance depends strongly on market environment.

Buy-and-hold was superior during the strong later-period market. Momentum was more competitive and more defensive during the earlier stressed period. Momentum should therefore be described as a regime-sensitive risk-control strategy rather than a universally better alternative to passive exposure.

### Next Step

The daily buy-and-hold and momentum framework is now sufficiently developed. The next phase should inspect the exact QQQ 5-minute ORB code preserved in Projects 2 and 3 before designing the first ORB-by-regime experiment.
