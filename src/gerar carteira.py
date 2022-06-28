# %%
from strategys.HiLo import HiLoSignal
from strategys.SmaCross import SmaCrossSignal
from services.crypto_get_data import getData
import datetime as dt
from tinydb import TinyDB
import os
import sys
dir2 = os.path.abspath('')
dir1 = os.path.dirname(dir2)
if not dir1 in sys.path:
    sys.path.append(dir1)


# %%


# %%
cwd = os.getcwd()
path = os.path.join("..", 'DB', 'estrategys.json')
db = TinyDB(path)
table = db.table('estrategys')


# %%
def funcaoLimitadoraGerarCarteira(estrategia):
    result = estrategia['results']
    try:
        return result['Avg. Trade [%]'] > 10.0 and result['Return [%]'] > 0 and result['Max. Drawdown [%]'] > -90.0 and result['Avg. Drawdown [%]'] > -60.0 and result['# Trades'] > 10 and result['Profit Factor'] > 2.0 and result['SQN'] > 1.0 and result['Worst Trade [%]'] > -60.0
    except KeyError:
        return result['Avg. Trade [%]'] > 10.0 and result['Return [%]'] > 0 and result['Max. Drawdown [%]'] > -90.0 and result['Avg. Drawdown [%]'] > -60.0 and result['Trades'] > 10 and result['Profit Factor'] > 2.0 and result['SQN'] > 1.0 and result['Worst Trade [%]'] > -60.0


# %%
# estrategias = table.search(
#     where('results')['Avg. Trade [%]'] > 50)
estrategias = table.search(funcaoLimitadoraGerarCarteira)
estrategias.sort(key=lambda x: x['results']['Profit Factor'], reverse=True)
print(len(estrategias))


# %%
def verifyStrategy(strategy):
    try:
        ticket = strategy['ticket']
        history = getData(ticket, period="10y",
                          interval=strategy["strategy"]["timeFrame"])
        if strategy['strategy']['name'] == 'SmaCrossStrategy':
            smaCurta = int(strategy['strategy']['params'][0])
            smaLonga = int(strategy['strategy']['params'][1])
            result = SmaCrossSignal(
                history, smaCurta=smaCurta, smaLonga=smaLonga)
            return result
        elif strategy['strategy']['name'] == 'HiLoStrategy':
            smaHigh = int(strategy['strategy']['params'][0])
            smaLow = int(strategy['strategy']['params'][1])
            result = HiLoSignal(
                history, smaHigh=smaHigh, smaLow=smaLow)
            return result
    except AttributeError:
        return None
    except Exception as e:
        print(e)
        print("Erro na verificação da estratégia")
        print(strategy)
        return None


# %%
dbcompras = TinyDB(os.path.join('..', 'DB', 'compras.json'))
tabelaOrdens = dbcompras.table('ordens')
ListaOrdens = tabelaOrdens.all()
tabelaDeComprados = dbcompras.table('comprados')
listaDeComprados = tabelaDeComprados.all()


# %% [markdown]
#

# %%
listaDeAtivos = []
listaDeVendas = []
novaListaDeComprados = []
for comprado in listaDeComprados:
    if comprado['ticket'] not in listaDeAtivos:
        listaDeAtivos.append(comprado['ticket'])
for vendido in listaDeVendas:
    if vendido['ticket'] not in listaDeAtivos:
        listaDeAtivos.append(vendido['ticket'])
for estrategia in estrategias:
    result = verifyStrategy(estrategia)
    if result is not None:
        if result['signal'] == 'Buy' and estrategia['ticket'] not in listaDeAtivos:
            if 'signal' in estrategia.keys():
                estrategia['signal']['buy'] = result['close']
            else:
                result.pop('df')
                estrategia['signal'] = result
                resultado = estrategia['results']
                resultado.pop('Start')
                resultado.pop('End')
                resultado.pop('Volatility (Ann.) [%]')
                resultado.pop('_trades')
                estrategia.pop('updateDate')
                estrategia['OrderDate'] = dt.datetime.now().strftime(
                    "%Y-%m-%d %H:%M:%S")
                print("Adicionado: ", estrategia['ticket'])
            listaDeAtivos.append(estrategia['ticket'])
            novaListaDeComprados.append(dict(estrategia))

    if len(listaDeComprados) >= 10:
        break


# %%
res = tabelaDeComprados.insert_multiple(novaListaDeComprados)
res = tabelaOrdens.insert_multiple(novaListaDeComprados)


# %%
barra = "    "
resultados = listaDeVendas + novaListaDeComprados
for resultado in resultados:
    if resultado['signal']['signal'].lower() == 'sell':
        print('Venda: ', resultado['ticket'].replace('USDT', ''))
    if resultado['signal']['signal'].lower() == 'buy':
        print('Compra: ', resultado['ticket'].replace('USDT', ''))
    print(barra, 'valor: ',  '$', resultado['signal']['close'])
    print(barra, 'chance de acerto: ',  int(
        resultado['results']['Win Rate [%]']), '%')
    print(barra, 'Total de Trades: ',  int(resultado['results']['# Trades']))
    print(barra, 'Média de perda quando erra: ',  int(
        resultado['results']['Avg. Drawdown [%]']), '%')
    print(barra, 'Média de lucro quando acerta: ',  int(
        resultado['results']['Win Rate [%]']*resultado['results']['Profit Factor']), '%')
    print(barra, 'Fator de Lucro: ',  int(
        resultado['results']['Profit Factor']))
    print(barra, 'Média de Lucro de Todos os Trades: ',
          int(resultado['results']['Avg. Trade [%]']), '%')


# %%
