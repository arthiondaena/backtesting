from backtesting import Backtest, Strategy
from backtesting.lib import SignalStrategy, TrailingStrategy
from indicators import SMC, EMA
from data_fetcher import fetch
import pandas as pd

class SMC_test(Strategy):
    swing_hl = 10
    def init(self):
        super().init()

        self.smc_b = self.I(self.smc_buy, data=self.data.df, swing_hl=self.swing_hl)
        self.smc_s = self.I(self.smc_sell, data=self.data.df, swing_hl=self.swing_hl)


    def next(self):
        price = self.data.Close[-1]
        current_time = self.data.index[-1]

        if self.smc_b[-1] == 1:
            self.buy(sl=.95 * price, tp=1.05 * price)
        if self.smc_s[-1] == -1:
            self.sell(tp=.95 * price, sl=1.05 * price)

        # Additionally, set aggressive stop-loss on trades that have been open
        # for more than two days
        for trade in self.trades:
            if current_time - trade.entry_time > pd.Timedelta('2 days'):
                if trade.is_long:
                    trade.sl = max(trade.sl, self.data.Low[-1])
                else:
                    trade.sl = min(trade.sl, self.data.High[-1])


    def smc_buy(self, data, swing_hl):
        return SMC(data, swing_hl).backtest_buy_signal()

    def smc_sell(self, data, swing_hl):
        return SMC(data, swing_hl).backtest_sell_signal()

class SMC_ema(SignalStrategy, TrailingStrategy):
    ema1 = 9
    ema2 = 21
    close_on_crossover = False

    def init(self):
        super().init()

        self.smc_b = self.I(self.smc_buy, self.data.df)
        self.smc_s = self.I(self.smc_sell, self.data.df)


        close = self.data.Close

        self.ma1 = self.I(EMA, close, self.ema1)
        self.ma2 = self.I(EMA, close, self.ema2)


    def next(self):
        price = self.data.Close[-1]
        current_time = self.data.index[-1]

        if self.smc_b[-1] == 1 and self.ma1 > self.ma2:
            self.buy(sl=.95 * price, tp=1.05 * price)
        if self.smc_s[-1] == -1 and self.ma1 < self.ma2:
            self.sell(tp=.95 * price, sl=1.05 * price)

        # Additionally, set aggressive stop-loss on trades that have been open
        # for more than two days
        for trade in self.trades:
            if current_time - trade.entry_time > pd.Timedelta('2 days'):
                if trade.is_long:
                    trade.sl = max(trade.sl, self.data.Low[-1])
                else:
                    trade.sl = min(trade.sl, self.data.High[-1])

        # Close the trade if there is a moving average crossover in opposite direction
        if self.close_on_crossover:
            for trade in self.trades:
                if trade.is_long and self.ma1 < self.ma2:
                    trade.close()
                if trade.is_short and self.ma1 > self.ma2:
                    trade.close()

    def smc_buy(self, data):
        return SMC(data).backtest_buy_signal()

    def smc_sell(self, data):
        return SMC(data).backtest_sell_signal()

def smc_plot_backtest(data, filename, swing_hl, **kwargs):
    bt = Backtest(data, SMC_test, **kwargs)
    bt.run(swing_hl=swing_hl)
    print('runned')
    return bt.plot(filename=filename, open_browser=False)

def smc_ema_plot_backtest(data, filename, ema1, ema2, closecross, **kwargs):
    bt = Backtest(data, SMC_ema, **kwargs)
    bt.run(ema1=ema1, ema2=ema2, close_on_crossover=closecross)
    return bt.plot(filename=filename, open_browser=False)


if __name__ == "__main__":
    data = fetch('ICICIBANK.NS', period='1mo', interval='15m')
    bt = Backtest(data, SMC_ema, commission=.002)

    bt.run(ema1 = 9, ema2 = 21, close_on_crossover=True)
    bt.plot()