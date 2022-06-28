import pandas as pd
import yfinance as yf
import datetime as dt
from pandas import Timestamp
import os
import ccxt


def getData(baseAsset, quoteAsset="USDT", period=1000, interval='1w'):
    def convertInterval(interval):
        if interval == '1wk' or interval == '1w':
            return '1w'
        elif interval == '1d':
            return '1d'
        else:
            raise ValueError('Interval not supported')

    interval = convertInterval(interval)

    def verifyData(lastDataIndexSaved, interval):
        now = dt.datetime.now()
        if interval == '1w':
            interval = 7
        if interval == '1d':
            interval = 1
        return now - lastDataIndexSaved > dt.timedelta(days=interval)

    def yahooFinance(baseAsset, end: str, quoteAsset: str = "USDT",  interval='1w'):
        try:
            if quoteAsset.upper().__contains__("USDT"):
                quoteAsset = "USD"
            ticket = baseAsset+"-"+quoteAsset
            if interval == '1w':
                interval = '1wk'
            res = yf.download(ticket, period='max',
                              interval=interval, end=end)
            return res
        except Exception as e:
            print(e)
            return None

    def binance(ticket, period: int = 1000, interval='1w', params: any = {}):
        binance = ccxt.binance()
        binance.fetch_ticker(ticket)
        data = binance.fetch_ohlcv(
            ticket, interval, limit=period, params=params)
        data = pd.DataFrame(
            data, columns=['Date', 'Open', 'High', 'Low', 'Close', 'Volume'])
        data['Date'] = pd.to_datetime(data['Date'], unit='ms')
        data = data.set_index('Date')
        data = data.sort_index()
        return data[-period:]

    def indexConverter(data):
        data['index'] = data.index
        data['index'] = data['index'].apply(lambda x: Timestamp(x))
        data['index'] = data['index'].apply(
            lambda x: x.strftime('%Y-%m-%d %H:%M:%S'))
        data['index'] = pd.to_datetime(data['index'])
        data = data.set_index('index')
        data = data.sort_index()
        return data

    baseAsset = baseAsset.upper()
    pathName = os.path.join("assets", "data", baseAsset.lower(
    )+"-"+quoteAsset.lower()+"_"+interval+".csv")
    path = os.path.abspath(os.getcwd())
    pathName = os.path.abspath(os.path.join(path, os.pardir, pathName))
    if not os.path.exists(os.path.dirname(pathName)):
        # print("Creating directory: " + os.path.dirname(pathName))
        os.makedirs(os.path.dirname(pathName))

    if not os.path.exists(pathName):
        # print("Baixando dados da Binance")
        data = binance(baseAsset+"/"+quoteAsset, period, interval)
        data = indexConverter(data)
        if period > len(data):
            # print("Baixando dados do Yahoo Finance")
            res = yahooFinance(
                baseAsset, data.index[-1], quoteAsset, interval)
            res = indexConverter(res)
            data = data.append(res)
            data = data.reset_index().drop_duplicates(
                subset='index', keep='first').set_index('index')
            data = data.sort_index()
    else:
        # print("Carregando dados do arquivo: "+pathName)
        data = pd.read_csv(pathName, index_col=0)
        data = indexConverter(data)
        if True:  # verifyData(data.index[-1], interval):
            dataUpdate = binance(baseAsset+"/"+quoteAsset, period, interval)
            dataUpdate = indexConverter(dataUpdate)
            data = data.append(dataUpdate)
            data = data.reset_index().drop_duplicates(
                subset='index', keep='last').set_index('index')
            data = data.sort_index()
    data.to_csv(pathName)
    return data[-period:]
