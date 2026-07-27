"""
Project 4: Cross-Strategy Regime Analysis

Experiment:
EXP-014_QQQ_ORB_5M_REGIME_BASELINE

Purpose:
Measure the corrected QQQ five-minute ORB across prior-day volatility and
trend regimes using actual QuantConnect portfolio returns.

Regime timing:
Each day's ORB return is assigned to the regime calculated after the previous
session close. No current-day intraday information is used to classify the day.

Strategy:
- QQQ minute data
- Long-only
- Five-bar opening range
- Enter when a later minute closes above the opening range high
- Block new entries beginning five minutes before the close
- Exit five minutes before the market close
- No stop or profit target
"""

from AlgorithmImports import *
from datetime import timedelta
from math import sqrt
from statistics import mean, median, stdev


class CrossStrategyRegimeAnalysis(QCAlgorithm):

    def initialize(self):
        self.set_start_date(2020, 1, 1)
        self.set_end_date(2026, 7, 1)
        self.set_cash(100000)

        self.symbol = self.add_equity("QQQ", Resolution.MINUTE).symbol
        self.opening_range_minutes = 5
        self.volatility_lookback = 20
        self.volatility_threshold_lookback = 252
        self.trend_lookback = 200
        self.trading_days_per_year = 252

        self.current_day = None
        self.opening_range_high = None
        self.opening_range_low = None
        self.opening_range_bar_count = 0
        self.opening_range_complete = False
        self.range_count_recorded = False
        self.traded_today = False
        self.entry_window_closed = False
        self.late_breakout_recorded = False

        self.trading_days = 0
        self.trade_days = 0
        self.legacy_late_breakout_days = 0
        self.overnight_holding_days = 0
        self.completed_range_counts = []

        self.previous_daily_close = None
        self.previous_portfolio_value = self.portfolio.total_portfolio_value
        self.active_regime = self.create_unclassified_regime()
        self.daily_close_history = []
        self.daily_return_history = []
        self.realized_volatility_history = []
        self.daily_records = []
        self.last_processed_date = None

        self.schedule.on(
            self.date_rules.every_day(self.symbol),
            self.time_rules.before_market_close(self.symbol, 5),
            self.close_entry_window_and_exit,
        )
        self.schedule.on(
            self.date_rules.every_day(self.symbol),
            self.time_rules.after_market_close(self.symbol, 1),
            self.process_daily_close,
        )

    def on_data(self, data: Slice):
        if self.symbol not in data.bars:
            return

        bar = data.bars[self.symbol]
        current_time = self.time
        current_day = current_time.date()

        if self.current_day != current_day:
            self.reset_daily_state(current_day)

        market_open = current_time.replace(
            hour=9,
            minute=30,
            second=0,
            microsecond=0,
        )
        opening_range_end = (
            market_open + timedelta(minutes=self.opening_range_minutes)
        )

        # Minute bars are available at their end time. The five opening-range
        # bars therefore arrive at 9:31, 9:32, 9:33, 9:34, and 9:35.
        if market_open < current_time <= opening_range_end:
            self.update_opening_range(bar)
            self.opening_range_bar_count += 1
            return

        # No breakout can be evaluated until the full range is available.
        if current_time <= opening_range_end:
            return

        if not self.opening_range_complete:
            self.opening_range_complete = True
            self.record_opening_range_count()

        if self.traded_today:
            return

        if self.opening_range_high is None:
            return

        if bar.close > self.opening_range_high:
            if self.entry_window_closed:
                if not self.late_breakout_recorded:
                    self.legacy_late_breakout_days += 1
                    self.late_breakout_recorded = True
                return

            self.set_holdings(self.symbol, 1)
            self.traded_today = True
            self.trade_days += 1

    def reset_daily_state(self, current_day):
        if (
            self.current_day is not None
            and self.portfolio[self.symbol].invested
        ):
            self.overnight_holding_days += 1

        self.current_day = current_day
        self.opening_range_high = None
        self.opening_range_low = None
        self.opening_range_bar_count = 0
        self.opening_range_complete = False
        self.range_count_recorded = False
        self.traded_today = False
        self.entry_window_closed = False
        self.late_breakout_recorded = False
        self.trading_days += 1

    def update_opening_range(self, bar):
        if self.opening_range_high is None:
            self.opening_range_high = bar.high
            self.opening_range_low = bar.low
            return

        self.opening_range_high = max(self.opening_range_high, bar.high)
        self.opening_range_low = min(self.opening_range_low, bar.low)

    def record_opening_range_count(self):
        if self.range_count_recorded:
            return

        self.completed_range_counts.append(self.opening_range_bar_count)
        self.range_count_recorded = True

    def close_entry_window_and_exit(self):
        self.entry_window_closed = True

        if self.portfolio[self.symbol].invested:
            self.liquidate(self.symbol)

    def process_daily_close(self):
        current_date = self.time.date()

        if self.last_processed_date == current_date:
            return

        daily_close = float(self.securities[self.symbol].price)
        current_portfolio_value = self.portfolio.total_portfolio_value

        if daily_close <= 0:
            return

        orb_return = (
            current_portfolio_value / self.previous_portfolio_value - 1
        )
        qqq_return = None

        if self.previous_daily_close is not None:
            qqq_return = daily_close / self.previous_daily_close - 1
            self.daily_return_history.append(qqq_return)

        self.daily_records.append({
            "date": current_date,
            "orb_return": orb_return,
            "qqq_return": qqq_return,
            "orb_signal": self.traded_today,
            "volatility_regime": self.active_regime["volatility_regime"],
            "trend_regime": self.active_regime["trend_regime"],
            "combined_regime": self.active_regime["combined_regime"],
            "realized_volatility": self.active_regime["realized_volatility"],
            "volatility_threshold": self.active_regime["volatility_threshold"],
            "moving_average": self.active_regime["moving_average"],
        })

        self.daily_close_history.append(daily_close)

        # Today's close can only determine the next trading day's regime.
        self.active_regime = self.calculate_regime_for_next_day()
        self.previous_daily_close = daily_close
        self.previous_portfolio_value = current_portfolio_value
        self.last_processed_date = current_date

    def create_unclassified_regime(self):
        return {
            "volatility_regime": "unclassified",
            "trend_regime": "unclassified",
            "combined_regime": "unclassified_unclassified",
            "realized_volatility": None,
            "volatility_threshold": None,
            "moving_average": None,
        }

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

        if len(self.daily_close_history) >= self.trend_lookback:
            recent_closes = self.daily_close_history[-self.trend_lookback:]
            moving_average = mean(recent_closes)

            if self.daily_close_history[-1] > moving_average:
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
        exact_five_bar_days = sum(
            1 for count in self.completed_range_counts
            if count == self.opening_range_minutes
        )
        incorrect_range_days = sum(
            1 for count in self.completed_range_counts
            if count != self.opening_range_minutes
        )

        if self.completed_range_counts:
            minimum_count = min(self.completed_range_counts)
            maximum_count = max(self.completed_range_counts)
            average_count = (
                sum(self.completed_range_counts)
                / len(self.completed_range_counts)
            )
        else:
            minimum_count = 0
            maximum_count = 0
            average_count = 0

        trade_day_rate = (
            self.trade_days / self.trading_days
            if self.trading_days else 0
        )

        if self.portfolio[self.symbol].invested:
            self.overnight_holding_days += 1

        classified_records = [
            record for record in self.daily_records
            if record["volatility_regime"] != "unclassified"
            and record["trend_regime"] != "unclassified"
        ]

        self.debug("EXP-014_QQQ_ORB_5M_REGIME_BASELINE")
        self.debug("Strategy: corrected QQQ five-bar long-only ORB")
        self.debug("Regime timing: today's ORB return uses yesterday's label")
        self.debug("ORB returns: daily changes in QuantConnect portfolio value")
        self.debug("Opening range bars: end times 9:31 through 9:35")
        self.debug("First eligible breakout bar: end time 9:36")
        self.debug("Entry window closes five minutes before each session close")
        self.debug(f"Trading days observed: {self.trading_days}")
        self.debug(
            f"Completed opening ranges: {len(self.completed_range_counts)}"
        )
        self.debug(f"Exact five-bar range days: {exact_five_bar_days}")
        self.debug(f"Incorrect range-count days: {incorrect_range_days}")
        self.debug(
            "Opening range bar counts: "
            f"min={minimum_count}, "
            f"max={maximum_count}, "
            f"average={average_count:.2f}"
        )
        self.debug(f"ORB trade days: {self.trade_days}")
        self.debug(f"ORB trade-day rate: {trade_day_rate:.2%}")
        self.debug(
            "Late breakout days blocked by cutoff: "
            f"{self.legacy_late_breakout_days}"
        )
        self.debug(
            "Days with unintended overnight holdings: "
            f"{self.overnight_holding_days}"
        )
        self.debug(f"Daily ORB records: {len(self.daily_records)}")
        self.debug(
            f"Fully classified daily records: {len(classified_records)}"
        )

        self.debug("ORB OVERALL SUMMARY")
        self.log_summary("orb_all_days", self.daily_records, "orb_return")

        self.debug("ORB VOLATILITY REGIME SUMMARY")
        self.log_group_summary(
            classified_records,
            "volatility_regime",
            "orb_return",
        )

        self.debug("ORB TREND REGIME SUMMARY")
        self.log_group_summary(
            classified_records,
            "trend_regime",
            "orb_return",
        )

        self.debug("ORB COMBINED REGIME SUMMARY")
        self.log_group_summary(
            classified_records,
            "combined_regime",
            "orb_return",
        )

        self.debug("ORB SIGNAL ACTIVITY BY VOLATILITY REGIME")
        self.log_signal_activity(classified_records, "volatility_regime")

        self.debug("ORB SIGNAL ACTIVITY BY TREND REGIME")
        self.log_signal_activity(classified_records, "trend_regime")

        self.debug("QQQ UNDERLYING OVERALL SUMMARY")
        qqq_records = [
            record for record in self.daily_records
            if record["qqq_return"] is not None
        ]
        self.log_summary("qqq_all_days", qqq_records, "qqq_return")

        custom_cumulative = self.calculate_cumulative_return(
            self.daily_records,
            "orb_return",
        )
        quantconnect_net_profit = (
            self.portfolio.total_portfolio_value / 100000 - 1
        )
        alignment_difference = custom_cumulative - quantconnect_net_profit

        self.debug(
            "RETURN ALIGNMENT CHECK: "
            f"custom_cum_return={custom_cumulative:.2%}, "
            f"quantconnect_net_profit={quantconnect_net_profit:.2%}, "
            f"difference={alignment_difference:.4%}"
        )

    def log_group_summary(self, records, group_key, return_key):
        group_names = sorted(set(record[group_key] for record in records))

        for group_name in group_names:
            group_records = [
                record for record in records
                if record[group_key] == group_name
            ]
            self.log_summary(group_name, group_records, return_key)

    def log_signal_activity(self, records, group_key):
        group_names = sorted(set(record[group_key] for record in records))

        for group_name in group_names:
            group_records = [
                record for record in records
                if record[group_key] == group_name
            ]
            signal_days = sum(
                1 for record in group_records
                if record["orb_signal"]
            )
            signal_rate = (
                signal_days / len(group_records)
                if group_records else 0
            )
            self.debug(
                f"{group_name}: "
                f"days={len(group_records)}, "
                f"signal_days={signal_days}, "
                f"signal_rate={signal_rate:.2%}"
            )

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
