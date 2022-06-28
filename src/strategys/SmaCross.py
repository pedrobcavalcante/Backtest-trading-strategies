import pandas_ta as ta
import pandas as pd
from backtesting import Strategy
from backtesting.lib import crossover
from backtesting.test import SMA


def SmaCrossSignal(df, smaCurta=5, smaLonga=20):
    if(smaCurta >= smaLonga):
        print("SmaCurta deve ser menor que SmaLonga")
        return None
    smaCurta = int(smaCurta)
    smaLonga = int(smaLonga)

    def lambdaFunction(df):
        if df['smaCurta'] > df['smaLonga']:
            return 'Buy'
        if df['smaCurta'] < df['smaLonga']:
            return 'Sell'
        else:
            return ''
    iLocSearch = (smaCurta+smaLonga)*(-5)
    df = df.iloc[iLocSearch:]
    if smaCurta > 1:
        dfsmaCurta = ta.sma(df['Close'], length=smaCurta)
    else:
        dfsmaCurta = df['Close']
    dfsmaCurta.name = 'smaCurta'
    if smaLonga > 1:
        dfsmaLonga = ta.sma(df['Close'], length=smaLonga)
    else:
        dfsmaLonga = df['Close']
    dfsmaLonga.name = 'smaLonga'
    df = pd.concat([df, dfsmaCurta, dfsmaLonga], axis=1)

    df['Signal'] = df.apply(lambda row: lambdaFunction(row), axis=1)
    # return df
    if(df['Signal'][-2] != df['Signal'][-3]):
        return {'signal': df['Signal'][-2], 'close': df['Close'][-2], 'df': df}
    else:
        return None


class SmaCrossStrategy(Strategy):
    n1 = 0
    n2 = 0

    def init(self):
        self.sma1 = self.I(SMA, self.data.Close, self.n1)
        self.sma2 = self.I(SMA, self.data.Close, self.n2)

    def next(self):
        if(self.sma1 < self.sma2):
            if crossover(self.sma1, self.sma2):
                self.buy(size=self._FULL_EQUITY/10)
            elif crossover(self.sma2, self.sma1):
                self.position.close()

    def setInitialParams(self, listDeValores):
        self.n1 = listDeValores[0]
        self.n2 = listDeValores[1]
