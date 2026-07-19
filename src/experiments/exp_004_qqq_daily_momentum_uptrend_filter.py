"""
Project 4: Cross-Strategy Regime Analysis

Experiment:
EXP-004_QQQ_DAILY_MOMENTUM_UPTREND_FILTER

QuantConnect project:
04 - Cross-Strategy Regime Analysis

Purpose:
Test whether adding a trend filter improves the simple QQQ daily momentum
strategy from EXP-002.

Strategy rule:
Hold QQQ when trailing 60-day momentum is positive and the prior trend regime
is uptrend. Otherwise hold cash.

Important timing rule:
Today's portfolio position is based on signals calculated from prior data.
Today's return is also assigned to the regime label known from prior data.
This avoids using today's close to decide today's exposure.
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

        # Baseline parameters chosen before seeing EXP-004 results.
        self.momentum_lookback = 60
        self.volatility_lookback = 20
        self.volatility_threshold_lookback = 252
        self.trend_lookback = 200
        self.trading_days_per_year = 252

        self.previous_close = None
        self.previous_regime = None
        self.previous_momentum_signal = None
        self.current_position = 0

        self.close_history = []
        self.daily_return_history = []
        self.realized_volatility_history = []
        self.daily_records = []

    def on_data(self, data: Slice):
        if self.symbol not in data.bars:
            return

        close = data.bars[self.symbol].close
        current_date = self.time.date()

        # Trade using signals that were already known before this bar.
        self.apply_previous_signal_and_filter()

        if self.previous_close is not None:
            qqq_return = close / self.previous_close - 1
            strategy_return = self.current_position * qqq_return

            # Today's return is assigned to the regime known before today.
            if self.previous_regime is not None:
                self.daily_records.append({
                    "date": current_date,
                    "qqq_return": qqq_return,
                    "strategy_return": strategy_return,
                    "momentum_position": self.current_position,
                    "volatility_regime": self.previous_regime["volatility_regime"],
                    "trend_regime": self.previous_regime["trend_regime"],
                    "combined_regime": self.previous_regime["combined_regime"],
                    "realized_volatility": self.previous_regime["realized_volatility"],
                    "volatility_threshold": self.previous_regime["volatility_threshold"],
                    "moving_average": self.previous_regime["moving_average"],
                    "momentum": self.previous_regime["momentum"],
                })

            self.daily_return_history.append(qqq_return)

        self.close_history.append(close)

        # After today's close is known, calculate signals for the next bar.
        self.previous_regime = self.calculate_regime_for_next_day()
        self.previous_momentum_signal = self.calculate_momentum_signal_for_next_day()
        self.previous_close = close

    def apply_previous_signal_and_filter(self):
        if self.previous_momentum_signal is None or self.previous_regime is None:
            return

        is_uptrend = self.previous_regime["trend_regime"] == "uptrend"
        should_hold_qqq = self.previous_momentum_signal and is_uptrend

        if should_hold_qqq:
            self.set_holdings(self.symbol, 1)
            self.current_position = 1
        else:
            self.liquidate(self.symbol)
            self.current_position = 0

    def calculate_momentum_signal_for_next_day(self):
        if len(self.close_history) < self.momentum_lookback + 1:
            return None

        current_close = self.close_history[-1]
        past_close = self.close_history[-1 - self.momentum_lookback]
        momentum = current_close / past_close - 1

        return momentum > 0

    def calculate_regime_for_next_day(self):
        realized_volatility = None
        volatility_threshold = None
        moving_average = None
        momentum = None

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

        if len(self.close_history) >= self.momentum_lookback + 1:
            current_close = self.close_history[-1]
            past_close = self.close_history[-1 - self.momentum_lookback]
            momentum = current_close / past_close - 1

        combined_regime = f"{volatility_regime}_{trend_regime}"

        return {
            "volatility_regime": volatility_regime,
            "trend_regime": trend_regime,
            "combined_regime": combined_regime,
            "realized_volatility": realized_volatility,
            "volatility_threshold": volatility_threshold,
            "moving_average": moving_average,
            "momentum": momentum,
        }

    def on_end_of_algorithm(self):
        self.debug("EXP-004_QQQ_DAILY_MOMENTUM_UPTREND_FILTER")
        self.debug("Strategy: Hold QQQ when 60-day momentum is positive and trend is up")
        self.debug("Regime timing: today's return uses yesterday's regime label")
        self.debug("Signal timing: today's position uses yesterday's momentum and trend signals")
        self.debug(f"Total daily records: {len(self.daily_records)}")

        classified_records = [
            record for record in self.daily_records
            if record["volatility_regime"] != "unclassified"
            and record["trend_regime"] != "unclassified"
        ]

        invested_records = [
            record for record in self.daily_records
            if record["momentum_position"] == 1
        ]

        exposure = len(invested_records) / len(self.daily_records)
        self.debug(f"Fully classified daily records: {len(classified_records)}")
        self.debug(f"Momentum uptrend exposure: {exposure:.2%}")

        self.debug("MOMENTUM UPTREND FILTER STRATEGY OVERALL SUMMARY")
        self.log_summary("all_days", self.daily_records, "strategy_return")

        self.debug("MOMENTUM UPTREND FILTER STRATEGY VOLATILITY REGIME SUMMARY")
        self.log_group_summary(classified_records, "volatility_regime", "strategy_return")

        self.debug("MOMENTUM UPTREND FILTER STRATEGY TREND REGIME SUMMARY")
        self.log_group_summary(classified_records, "trend_regime", "strategy_return")

        self.debug("MOMENTUM UPTREND FILTER STRATEGY COMBINED REGIME SUMMARY")
        self.log_group_summary(classified_records, "combined_regime", "strategy_return")

        self.debug("QQQ UNDERLYING RETURN SUMMARY FOR COMPARISON")
        self.log_summary("qqq_all_days", self.daily_records, "qqq_return")

    def log_group_summary(self, records, group_key, return_key):
        group_names = sorted(set(record[group_key] for record in records))

        for group_name in group_names:
            group_records = [
                record for record in records
                if record[group_key] == group_name
            ]
            self.log_summary(group_name, group_records, return_key)

    def log_summary(self, label, records, return_key):
        returns = [record[return_key] for record in records]

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
