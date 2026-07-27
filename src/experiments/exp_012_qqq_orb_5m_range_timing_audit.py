"""
Project 4: Cross-Strategy Regime Analysis

Experiment:
EXP-012_QQQ_ORB_5M_RANGE_TIMING_AUDIT

Purpose:
Rebuild the QQQ 5-minute ORB baseline with an opening range that contains
exactly five completed one-minute bars.

Legacy timing issue:
LEAN emits minute bars at their end time. The prior condition included bars
ending at 9:31, 9:32, 9:33, and 9:34, then allowed the 9:35 bar to trigger a
breakout. This experiment includes the 9:35 bar in the opening range and makes
the 9:36 bar the first eligible breakout bar.

Strategy:
- QQQ minute data
- Long-only
- Five-bar opening range
- Enter when a later minute closes above the opening range high
- Exit five minutes before the market close
- No stop or profit target
"""

from AlgorithmImports import *
from datetime import timedelta


class CrossStrategyRegimeAnalysis(QCAlgorithm):

    def initialize(self):
        self.set_start_date(2020, 1, 1)
        self.set_end_date(2026, 7, 1)
        self.set_cash(100000)

        self.symbol = self.add_equity("QQQ", Resolution.MINUTE).symbol
        self.opening_range_minutes = 5

        self.current_day = None
        self.opening_range_high = None
        self.opening_range_low = None
        self.opening_range_bar_count = 0
        self.opening_range_complete = False
        self.range_count_recorded = False
        self.traded_today = False

        self.trading_days = 0
        self.trade_days = 0
        self.completed_range_counts = []

        self.schedule.on(
            self.date_rules.every_day(self.symbol),
            self.time_rules.before_market_close(self.symbol, 5),
            self.exit_position,
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
            self.set_holdings(self.symbol, 1)
            self.traded_today = True
            self.trade_days += 1

    def reset_daily_state(self, current_day):
        self.current_day = current_day
        self.opening_range_high = None
        self.opening_range_low = None
        self.opening_range_bar_count = 0
        self.opening_range_complete = False
        self.range_count_recorded = False
        self.traded_today = False
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

    def exit_position(self):
        if self.portfolio[self.symbol].invested:
            self.liquidate(self.symbol)

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

        self.debug("EXP-012_QQQ_ORB_5M_RANGE_TIMING_AUDIT")
        self.debug("Strategy: QQQ five-bar long-only ORB")
        self.debug("Opening range bars: end times 9:31 through 9:35")
        self.debug("First eligible breakout bar: end time 9:36")
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
