from datetime import timedelta

import pandas_ta as ta
from pyalgotrader_protocols.strategy import Strategy_Protocol


class Strategy(Strategy_Protocol):
    async def initialize(self) -> None:
        await self.set_account_type(self.AccountType.DERIVATIVE_INTRADAY)

        self.instrument = await self.add_equity(
            self.symbols.NIFTY_BANK, timedelta(minutes=5)
        )

        await self.instrument.set_filter(self.set_instrument_option_filter)

    async def set_instrument_option_filter(self) -> None:
        self.instrument_ce = await self.instrument.add_option(("weekly", 1), -2, "CE")
        self.instrument_pe = await self.instrument.add_option(("weekly", 1), +2, "PE")

    @property
    def sma_20(self):
        return self.instrument.add_indicator(
            "sma_20",
            lambda data: ta.sma(data.close, 20),
        )

    @property
    def sma_50(self):
        return self.instrument.add_indicator(
            "sma_50",
            lambda data: ta.sma(data.close, 50),
        )

    @property
    def adx_14(self):
        return self.instrument.add_indicator(
            "adx_14",
            lambda data: ta.adx(data.high, data.low, data.close, 14),
        )

    async def next(self) -> None:
        sma_signal = None
        adx_signal = None

        if self.sma_20.data["SMA_20"][-1] > self.sma_50.data["SMA_50"][-1]:
            sma_signal = "long"

        if self.sma_20.data["SMA_20"][-1] < self.sma_50.data["SMA_50"][-1]:
            sma_signal = "short"

        if self.adx_14.data["ADX_14"][-2] > 20 and self.adx_14.data["ADX_14"][-1] > 20:
            adx_signal = True

        if not self.positions:
            should_long = sma_signal == "long" and adx_signal
            should_short = sma_signal == "short" and adx_signal

            if should_long:
                await self.buy(
                    self.instrument_ce, quantities=200, sl=40, tgt=80, tsl=10
                )

            if should_short:
                await self.buy(
                    self.instrument_pe, quantities=200, sl=40, tgt=80, tsl=10
                )
