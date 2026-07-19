"""
Project 4: Cross-Strategy Regime Analysis

Experiment:
EXP-001_QQQ_BUY_AND_HOLD_REGIME_BASELINE

QuantConnect project:
04 - Cross-Strategy Regime Analysis

Purpose:
Establish a QQQ buy-and-hold benchmark and summarize QQQ daily returns
across volatility and trend regimes.

Important timing rule:
The regime label for today's close-to-close return is based on information
available as of yesterday's close. This avoids using today's close to explain
or classify today's return.
"""

from AlgorithmImports import *
from math import sqrt
from statistics import mean, median, stdev


class CrossStrategyRegimeAnalysis(QCAlgorithm):

    def initialize(self):
        self.set_start_date(2020, 1, 1)
        self.set_end_date(2026, 7, 1)
        self.set_cash(100000)

        self.symbol = self.add_equity("QQQ", Resolution.DAILY).symbol

        # Baseline regime parameters chosen before seeing Project 4 results.
        self.volatility_lookback = 20
        self.volatility_threshold_lookback = 252
        self.trend_lookback = 200
        self.trading_days_per_year = 252

        self.previous_close = None
        self.previous_regime = None
        self.invested = False

        self.close_history = []
        self.daily_return_history = []
        self.realized_volatility_history = []
        self.daily_records = []

    def on_data(self, data: Slice):
        if self.symbol not in data.bars:
            return

        close = data.bars[self.symbol].close
        current_date = self.time.date()

        # This is the actual benchmark strategy: buy QQQ and hold it.
        if not self.invested:
            self.set_holdings(self.symbol, 1)
            self.invested = True

        if self.previous_close is not None:
            daily_return = close / self.previous_close - 1

            # Today's return is assigned to the regime known yesterday.
            if self.previous_regime is not None:
                self.daily_records.append({
                    "date": current_date,
                    "daily_return": daily_return,
                    "volatility_regime": self.previous_regime["volatility_regime"],
                    "trend_regime": self.previous_regime["trend_regime"],
                    "combined_regime": self.previous_regime["combined_regime"],
                    "realized_volatility": self.previous_regime["realized_volatility"],
                    "volatility_threshold": self.previous_regime["volatility_threshold"],
                    "moving_average": self.previous_regime["moving_average"],
                })

            self.daily_return_history.append(daily_return)

        self.close_history.append(close)

        # After today's close is known, calculate the regime to use tomorrow.
        self.previous_regime = self.calculate_regime_for_next_day()
        self.previous_close = close

    def calculate_regime_for_next_day(self):
        realized_volatility = None
        volatility_threshold = None
        moving_average = None

        volatility_regime = "unclassified"
        trend_regime = "unclassified"

        if len(self.daily_return_history) >= self.volatility_lookback:
            recent_returns = self.daily_return_history[-self.volatility_lookback:]
            realized_volatility = (
                stdev(recent_returns) * sqrt(self.trading_days_per_year)
            )
            self.realized_volatility_history.append(realized_volatility)

        if len(self.realized_volatility_history) >= self.volatility_threshold_lookback:
            recent_volatility = self.realized_volatility_history[
                -self.volatility_threshold_lookback:
            ]
            volatility_threshold = median(recent_volatility)

            if realized_volatility <= volatility_threshold:
                volatility_regime = "low_volatility"
            else:
                volatility_regime = "high_volatility"

        if len(self.close_history) >= self.trend_lookback:
            recent_closes = self.close_history[-self.trend_lookback:]
            moving_average = mean(recent_closes)

            if self.close_history[-1] > moving_average:
                trend_regime = "uptrend"
            else:
                trend_regime = "downtrend"

        combined_regime = f"{volatility_regime}_{trend_regime}"

        return {
            "volatility_regime": volatility_regime,
            "trend_regime": trend_regime,
            "combined_regime": combined_regime,
            "realized_volatility": realized_volatility,
            "volatility_threshold": volatility_threshold,
            "moving_average": moving_average,
        }

    def on_end_of_algorithm(self):
        self.debug("EXP-001_QQQ_BUY_AND_HOLD_REGIME_BASELINE")
        self.debug("Strategy: Buy and hold QQQ")
        self.debug("Regime timing: today's return uses yesterday's regime label")
        self.debug(f"Total daily records: {len(self.daily_records)}")

        classified_records = [
            record for record in self.daily_records
            if record["volatility_regime"] != "unclassified"
            and record["trend_regime"] != "unclassified"
        ]

        self.debug(f"Fully classified daily records: {len(classified_records)}")

        self.debug("OVERALL RETURN SUMMARY")
        self.log_summary("all_days", self.daily_records)

        self.debug("VOLATILITY REGIME SUMMARY")
        self.log_group_summary(classified_records, "volatility_regime")

        self.debug("TREND REGIME SUMMARY")
        self.log_group_summary(classified_records, "trend_regime")

        self.debug("COMBINED REGIME SUMMARY")
        self.log_group_summary(classified_records, "combined_regime")

    def log_group_summary(self, records, group_key):
        group_names = sorted(set(record[group_key] for record in records))

        for group_name in group_names:
            group_records = [
                record for record in records
                if record[group_key] == group_name
            ]
            self.log_summary(group_name, group_records)

    def log_summary(self, label, records):
        returns = [record["daily_return"] for record in records]

        if len(returns) == 0:
            self.debug(f"{label}: no records")
            return

        cumulative_return = 1
        wins = 0

        for daily_return in returns:
            cumulative_return *= 1 + daily_return
            if daily_return > 0:
                wins += 1

        cumulative_return -= 1
        average_daily_return = mean(returns)
        win_rate = wins / len(returns)

        if len(returns) > 1:
            annualized_volatility = stdev(returns) * sqrt(self.trading_days_per_year)
        else:
            annualized_volatility = 0

        years = len(returns) / self.trading_days_per_year
        annualized_return = (1 + cumulative_return) ** (1 / years) - 1

        if annualized_volatility == 0:
            sharpe_like_ratio = 0
        else:
            sharpe_like_ratio = annualized_return / annualized_volatility

        self.debug(
            f"{label}: "
            f"days={len(returns)}, "
            f"cum_return={cumulative_return:.2%}, "
            f"ann_return={annualized_return:.2%}, "
            f"ann_vol={annualized_volatility:.2%}, "
            f"sharpe_like={sharpe_like_ratio:.3f}, "
            f"avg_daily={average_daily_return:.4%}, "
            f"win_rate={win_rate:.2%}"
        )
