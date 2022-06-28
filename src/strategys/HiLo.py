import pandas_ta as ta
import pandas as pd
from backtesting import Strategy
from backtesting.test import SMA


def HiLoSignal(df, smaHigh=5, smaLow=5):
    def lambdaFunction(df):
        if df['Close'] > df['smaHigh']:
            return 'Buy'
        if df['Close'] < df['smaLow']:
            return 'Sell'
        else:
            return ''
    iLocSearch = (smaHigh+smaLow)*(-5)
    df = df.iloc[iLocSearch:]
    dfsmaHigh = ta.sma(df['High'], length=smaHigh)
    dfsmaHigh.name = 'smaHigh'
    dfsmaLow = ta.sma(df['Low'], length=smaLow)
    dfsmaLow.name = 'smaLow'
    df = pd.concat([df, dfsmaHigh, dfsmaLow], axis=1)

    df['Signal'] = df.apply(lambda row: lambdaFunction(row), axis=1)
    # return df
    if(df['Signal'][-2] != df['Signal'][-3]):
        return {'signal': df['Signal'][-2], 'close': df['Close'][-2], 'df': df}
    else:
        return None


class HiLoStrategy(Strategy):
    n1 = 1
    n2 = 1

    def init(self):
        self.sma1 = self.I(SMA, self.data.High, self.n1)
        self.sma2 = self.I(SMA, self.data.Low, self.n2)

    def next(self):
        if self.data.Close > self.sma1:
            self.buy(size=self._FULL_EQUITY/10)

        if self.sma2 > self.data.Close:
            self.position.close()

    def setInitialParams(self, listDeValores):
        self.n1 = listDeValores[0]
        self.n2 = listDeValores[1]
