"""
Project 4: Cross-Strategy Regime Analysis

Experiment:
EXP-009_QQQ_DAILY_MOMENTUM_EXPLICIT_MOO_BASELINE

QuantConnect project:
04 - Cross-Strategy Regime Analysis

Purpose:
Create a reproducible 60-day momentum baseline with an explicit next-session
MarketOnOpen execution rule and actual portfolio-value regime attribution.

Strategy rule:
After each daily close, calculate trailing 60-day momentum and submit an
explicit MarketOnOpen order for the next session. Hold cash when momentum is
not positive.

Timing rule:
The next day's signal and regime label are calculated only after the current
daily close. The order cannot fill before the next session opens. Actual
strategy returns come from changes in QuantConnect's total portfolio value.
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

        # Use the original 60-day momentum specification.
        self.momentum_lookback = 60
        self.volatility_lookback = 20
        self.volatility_threshold_lookback = 252
        self.trend_lookback = 200
        self.trading_days_per_year = 252

        self.previous_close = None
        self.previous_portfolio_value = None

        # These values are calculated after a close and used the next day.
        self.pending_momentum_signal = None
        self.active_regime = None
        self.current_target_position = 0

        self.close_history = []
        self.daily_return_history = []
        self.realized_volatility_history = []
        self.daily_records = []

    def submit_market_on_open_rebalance(self, momentum_signal):
        if momentum_signal is None:
            return

        desired_position = 1 if momentum_signal else 0

        # Avoid submitting a new order when the desired exposure is unchanged.
        if desired_position == self.current_target_position:
            return

        if desired_position == 1:
            order_quantity = self.calculate_order_quantity(self.symbol, 1)
        else:
            order_quantity = -self.portfolio[self.symbol].quantity

        if order_quantity != 0:
            self.market_on_open_order(self.symbol, order_quantity)

        self.current_target_position = desired_position

    def on_data(self, data: Slice):
        if self.symbol not in data.bars:
            return

        close = data.bars[self.symbol].close
        current_date = self.time.date()
        current_portfolio_value = self.portfolio.total_portfolio_value

        if (
            self.previous_close is not None
            and self.previous_portfolio_value is not None
        ):
            qqq_return = close / self.previous_close - 1
            actual_portfolio_return = (
                current_portfolio_value / self.previous_portfolio_value - 1
            )

            # This reproduces the prior experiments' synthetic assumption.
            synthetic_close_return = (
                self.current_target_position * qqq_return
            )

            if self.active_regime is not None:
                self.daily_records.append({
                    "date": current_date,
                    "qqq_return": qqq_return,
                    "actual_portfolio_return": actual_portfolio_return,
                    "synthetic_close_return": synthetic_close_return,
                    "target_position": self.current_target_position,
                    "volatility_regime": (
                        self.active_regime["volatility_regime"]
                    ),
                    "trend_regime": self.active_regime["trend_regime"],
                    "combined_regime": self.active_regime["combined_regime"],
                    "realized_volatility": (
                        self.active_regime["realized_volatility"]
                    ),
                    "volatility_threshold": (
                        self.active_regime["volatility_threshold"]
                    ),
                    "moving_average": self.active_regime["moving_average"],
                    "momentum": self.active_regime["momentum"],
                })

            self.daily_return_history.append(qqq_return)

        self.close_history.append(close)

        # Information calculated here is used no earlier than the next open.
        self.active_regime = self.calculate_regime_for_next_day()
        self.pending_momentum_signal = (
            self.calculate_momentum_signal_for_next_day()
        )

        # Submit after today's close for an explicit fill at the next open.
        self.submit_market_on_open_rebalance(self.pending_momentum_signal)

        self.previous_close = close
        self.previous_portfolio_value = current_portfolio_value

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
        self.debug("EXP-009_QQQ_DAILY_MOMENTUM_EXPLICIT_MOO_BASELINE")
        self.debug("Strategy: 60-day momentum with explicit MarketOnOpen orders")
        self.debug("Regime timing: today's return uses yesterday's regime label")
        self.debug("Actual returns: daily changes in QuantConnect portfolio value")
        self.debug("Synthetic returns: target position times QQQ close return")
        self.debug(f"Total daily records: {len(self.daily_records)}")

        classified_records = [
            record for record in self.daily_records
            if record["volatility_regime"] != "unclassified"
            and record["trend_regime"] != "unclassified"
        ]
        invested_records = [
            record for record in self.daily_records
            if record["target_position"] == 1
        ]

        exposure = (
            len(invested_records) / len(self.daily_records)
            if self.daily_records else 0
        )

        self.debug(f"Fully classified daily records: {len(classified_records)}")
        self.debug(f"Momentum target exposure: {exposure:.2%}")

        self.debug("ACTUAL PORTFOLIO OVERALL SUMMARY")
        self.log_summary(
            "actual_all_days",
            self.daily_records,
            "actual_portfolio_return",
        )

        self.debug("ACTUAL PORTFOLIO VOLATILITY REGIME SUMMARY")
        self.log_group_summary(
            classified_records,
            "volatility_regime",
            "actual_portfolio_return",
        )

        self.debug("ACTUAL PORTFOLIO TREND REGIME SUMMARY")
        self.log_group_summary(
            classified_records,
            "trend_regime",
            "actual_portfolio_return",
        )

        self.debug("ACTUAL PORTFOLIO COMBINED REGIME SUMMARY")
        self.log_group_summary(
            classified_records,
            "combined_regime",
            "actual_portfolio_return",
        )

        self.debug("SYNTHETIC CLOSE-TO-CLOSE COMPARISON SUMMARY")
        self.log_summary(
            "synthetic_all_days",
            self.daily_records,
            "synthetic_close_return",
        )

        self.debug("QQQ UNDERLYING RETURN SUMMARY FOR COMPARISON")
        self.log_summary("qqq_all_days", self.daily_records, "qqq_return")

        actual_cumulative = self.calculate_cumulative_return(
            self.daily_records,
            "actual_portfolio_return",
        )
        synthetic_cumulative = self.calculate_cumulative_return(
            self.daily_records,
            "synthetic_close_return",
        )
        timing_gap = actual_cumulative - synthetic_cumulative

        self.debug(
            "EXECUTION ALIGNMENT CHECK: "
            f"actual_cum_return={actual_cumulative:.2%}, "
            f"synthetic_cum_return={synthetic_cumulative:.2%}, "
            f"difference={timing_gap:.2%}"
        )

    def log_group_summary(self, records, group_key, return_key):
        group_names = sorted(set(record[group_key] for record in records))

        for group_name in group_names:
            group_records = [
                record for record in records
                if record[group_key] == group_name
            ]
            self.log_summary(group_name, group_records, return_key)

    def calculate_cumulative_return(self, records, return_key):
        cumulative_value = 1

        for record in records:
            cumulative_value *= 1 + record[return_key]

        return cumulative_value - 1

    def log_summary(self, label, records, return_key):
        returns = [record[return_key] for record in records]

        if len(returns) == 0:
            self.debug(f"{label}: no records")
            return

        cumulative_return = self.calculate_cumulative_return(records, return_key)
        average_daily_return = mean(returns)
        wins = sum(1 for daily_return in returns if daily_return > 0)
        win_rate = wins / len(returns)

        if len(returns) > 1:
            annualized_volatility = (
                stdev(returns) * sqrt(self.trading_days_per_year)
            )
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
