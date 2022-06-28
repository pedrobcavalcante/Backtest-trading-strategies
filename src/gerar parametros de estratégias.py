# %%
from services.crypto_get_data import getData as gd
from services.condicao import funcaoDeCondicao
from services.generateWeightedAverageTrade import generateWeightedAverageTrade
from strategys.HiLo import HiLoStrategy
from strategys.SmaCross import SmaCrossStrategy
import datetime as dt
from tinydb import TinyDB, Query
from backtesting import Backtest
import backtesting
import os
import sys
import json
dir2 = os.path.abspath("")
dir1 = os.path.dirname(dir2)
if not dir1 in sys.path:
    sys.path.append(dir1)


backtesting.set_bokeh_output(notebook=False)


# %%


# %%
def gerarListaDeParametros(listaDeListas):
    listaDeParametros = []

    def executarFuncaoRecursiva(listaDeListas, newlist=[], modificadorInicial=0):
        if not newlist:
            newlist.extend(listaDeListas)
        tamanhoLista = len(listaDeListas)
        for i in listaDeListas[modificadorInicial]:
            if modificadorInicial < tamanhoLista - 1:
                newlist[modificadorInicial] = i
                executarFuncaoRecursiva(
                    listaDeListas, newlist, modificadorInicial + 1)
            else:
                newlist[modificadorInicial] = i
                listaDeParametros.append(newlist[:])

    executarFuncaoRecursiva(listaDeListas)
    return listaDeParametros


# %%
def gerarListadeBackTest(listaDeParametros, Strategy, dataframe):
    listaDeBackTest = []
    for parametros in listaDeParametros:
        try:
            Strategy.setInitialParams(Strategy, parametros)
            bt = Backtest(
                dataframe, Strategy, cash=100000000, exclusive_orders=False, commission=0.00
            )
            output = bt.run()
            listaDeBackTest.append(
                {"parametros": parametros, "results": output})
        except Exception as e:
            print("erro na geração de backetest para os parametros: ", parametros)
            print(e)
    return listaDeBackTest


# %%
def pegarOsMelhoresResutadosDaListaDeBackTest(listaDeBackTest):
    def adicionarAListaDeResultado(lista, resultado):
        if resultado not in lista and resultado != None:
            lista.append(resultado)
        return lista

    maxReturn = None
    maxSharpeRatio = None
    maxSortinoRatio = None
    maxCalmarRatio = None
    WinRate = None
    maxProfitFactor = None
    maxExpectancy = None
    maxSQN = None
    finalList = []
    for backTest in listaDeBackTest:
        results = backTest["results"]
        if funcaoDeCondicao(results):
            if (
                maxReturn == None
                or results["Return [%]"] > maxReturn["results"]["Return [%]"]
            ):
                maxReturn = backTest
            if (
                maxSharpeRatio == None
                or results["Sharpe Ratio"] > maxSharpeRatio["results"]["Sharpe Ratio"]
            ):
                maxSharpeRatio = backTest
            if (
                maxSortinoRatio == None
                or results["Sortino Ratio"]
                > maxSortinoRatio["results"]["Sortino Ratio"]
            ):
                maxSortinoRatio = backTest
            if (
                maxCalmarRatio == None
                or results["Calmar Ratio"] > maxCalmarRatio["results"]["Calmar Ratio"]
            ):
                maxCalmarRatio = backTest
            if (
                WinRate == None
                or results["Win Rate [%]"] > WinRate["results"]["Win Rate [%]"]
            ):
                WinRate = backTest
            if (
                maxProfitFactor == None
                or results["Profit Factor"]
                > maxProfitFactor["results"]["Profit Factor"]
            ):
                maxProfitFactor = backTest
            if (
                maxExpectancy == None
                or results["Expectancy [%]"]
                > maxExpectancy["results"]["Expectancy [%]"]
            ):
                maxExpectancy = backTest
            if maxSQN == None or results["SQN"] > maxSQN["results"]["SQN"]:
                maxSQN = backTest
    finalList = adicionarAListaDeResultado(finalList, maxReturn)
    finalList = adicionarAListaDeResultado(finalList, maxSharpeRatio)
    finalList = adicionarAListaDeResultado(finalList, maxSortinoRatio)
    finalList = adicionarAListaDeResultado(finalList, maxCalmarRatio)
    finalList = adicionarAListaDeResultado(finalList, WinRate)
    finalList = adicionarAListaDeResultado(finalList, maxProfitFactor)
    finalList = adicionarAListaDeResultado(finalList, maxExpectancy)
    finalList = adicionarAListaDeResultado(finalList, maxSQN)
    if len(finalList) == 0:
        print("Nenhum resultado encontrado")
    else:
        print("Lista de melhores resultados final gerada. Total: ", len(finalList))
    return finalList


# %%
def gerarDicionario(ativo, output, strategyName, strategyTimeFrame, params):
    results = json.loads(output["results"].to_json())
    results.pop("Equity Final [$]")
    results.pop("Equity Peak [$]")
    results.pop("Return (Ann.) [%]")
    results.pop("_strategy")
    results.pop("_equity_curve")
    results["Weighted Average Trade"] = generateWeightedAverageTrade(results)
    dicionario = {
        "ticket": ativo,
        "strategy": {
            "name": strategyName,
            "timeFrame": strategyTimeFrame,
            "params": params,
        },
        "results": results,
        "updateDate": dt.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    }
    return dicionario


# %%
def gerarListaReduzida(tamanho):
    lista = []
    if tamanho <= 11:
        for i in range(tamanho):
            lista.append(i)
    else:
        lista = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
        while lista[-1] < tamanho:
            lista.append(int(lista[-1] * 1.1))
    list.remove(lista, 0)
    return lista


# %%
def insertIntTableOfUpdates(updateTable, ticket, strategyName, strategyTimeFrame):
    lambdaContains = (
        lambda x: x["ticket"] == ticket["quota"]
        and x["strategy"] == strategyName
        and x["timeFrame"] == strategyTimeFrame
    )
    if updateTable.contains(lambdaContains):
        updateTable.update(
            {"updateDate": dt.datetime.now().strftime("%Y-%m-%d %H:%M:%S")},
            lambdaContains,
        )
    else:
        updateTable.insert(
            {
                "ticket": ticket["quota"],
                "updateDate": dt.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "strategy": strategyName,
                "timeFrame": strategyTimeFrame,
            }
        )


# %%
def gerarUnicaEstrategiaESalvar(
    updateTable,
    ticket,
    strategyName,
    strategy,
    strategysedb,
    timeFrame,
    listaDeParametros,
    dataframe,
    removeStrategysFirst=False
):
    if removeStrategysFirst:
        removefunc = (
            lambda x: x["ticket"] == ticket["quota"]
            and x["strategy"]["name"] == strategyName
            and x["strategy"]["timeFrame"] == timeFrame
        )
        strategysedb.table("estrategys").remove(removefunc)
    listaDeBackTest = gerarListadeBackTest(
        listaDeParametros, strategy, dataframe)
    print("estratégia: ", strategyName, "-", timeFrame, end='-> ')
    melhoresBackTest = pegarOsMelhoresResutadosDaListaDeBackTest(
        listaDeBackTest)
    finalList = []
    if len(melhoresBackTest) > 0:
        for backTest in melhoresBackTest:
            resultado = gerarDicionario(
                ticket["quota"],
                backTest,
                strategyName,
                timeFrame,
                backTest["parametros"],
            )
            finalList.append(resultado)
        if finalList != [None]:
            strategysedb.table("estrategys").insert_multiple(finalList)
        else:
            strategysedb.table("estrategys").insert(
                {
                    "ticket": ticket["quota"],
                    "strategy": {
                        "name": strategyName,
                        "timeFrame": timeFrame,
                        "params": None,
                    },
                    "results": None,
                    "updateDate": dt.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                }
            )
    insertIntTableOfUpdates(updateTable, ticket, strategyName, timeFrame)


# %%
def GerarEstrategiasPorTimeFrame(
    removeStrategysFirst,
    timeFrame,
    updateTable,
    ticket,
    strategysedb,
    listaDeParametros,
    dataframe,
):
    strategys = [
        {"strategyName": "HiLoStrategy", "strategy": HiLoStrategy},
        {"strategyName": "SmaCrossStrategy", "strategy": SmaCrossStrategy},
    ]
    for strategy in strategys:
        gerarUnicaEstrategiaESalvar(
            updateTable,
            ticket,
            strategy["strategyName"],
            strategy["strategy"],
            strategysedb,
            timeFrame,
            listaDeParametros,
            dataframe,
            removeStrategysFirst)


# %%
def ordenarListaDeEstrategias(lista):
    def lambdaFunction(x):
        divisor = 1
        if x["timeFrame"] == "1wk":
            divisor = 7
        updateDate = dt.datetime.strptime(x["updateDate"], "%Y-%m-%d %H:%M:%S")

        return (dt.datetime.now() - updateDate) / divisor

    lista.sort(key=lambda x: lambdaFunction(x), reverse=True)
    return lista


# %%
def getStrategysFunction(strategyName):
    if strategyName == "HiLoStrategy":
        return HiLoStrategy
    elif strategyName == "SmaCrossStrategy":
        return SmaCrossStrategy
    else:
        return None


# %%
def condition(mode, updateTable, ticket):
    if mode == "OnlyUpdate":
        return updateTable.contains(Query().ticket == ticket["quota"])
    elif mode == "OnlyInsertNew":
        return not updateTable.contains(Query().ticket == ticket["quota"])
    elif mode == "OverwriteAll":
        return True
    else:
        print("Modo de operacao invalido")
        return "break"


def gerarTodasEstrategiasESalvar(mode):
    binancedb = TinyDB(os.path.join("..", "DB", "binance.json"))
    binanceTickets = binancedb.table("pares").all()
    strategysedb = TinyDB(os.path.join("..", "DB", "estrategys.json"))
    updateTable = strategysedb.table("update")
    listaDeParametros = gerarListaDeParametros(
        [gerarListaReduzida(100), gerarListaReduzida(100)]
    )
    if mode == "OnlyUpdate":
        listaDeUpdate = ordenarListaDeEstrategias(updateTable.all())
        for update in listaDeUpdate:
            print("Atualizando: ", update["ticket"], "-", update["strategy"])
            try:
                ticket = {"quota": update["ticket"]}
                dataframe = gd(ticket["quota"])
                gerarUnicaEstrategiaESalvar(
                    updateTable,
                    ticket,
                    update["strategy"],
                    getStrategysFunction(update["strategy"]),
                    strategysedb,
                    update['timeFrame'],
                    listaDeParametros,
                    dataframe,
                    True)
            except Exception as e:
                print(e)
    else:
        for ticket in binanceTickets:
            try:
                if condition(mode, updateTable, ticket):
                    print(ticket["quota"])
                    dataframe = gd(ticket["quota"])
                    GerarEstrategiasPorTimeFrame(
                        mode != "OnlyInsertNew",
                        "1wk",
                        updateTable,
                        ticket,
                        strategysedb,
                        listaDeParametros,
                        dataframe,
                    )
                elif condition(mode, updateTable, ticket) == "break":
                    break
            except Exception as e:
                print(e)


# %%
# gerarTodasEstrategiasESalvar("OnlyInsertNew")
gerarTodasEstrategiasESalvar("OnlyUpdate")
