from unittest import result


def funcaoDeCondicao(results):
    if results["Win Rate [%]"] == None or results["Win Rate [%]"] < 49.0:
        return False
    elif results["# Trades"] == None or results["# Trades"] < 10:
        return False
    elif results["Expectancy [%]"] == None or results["Expectancy [%]"] < 0.0:
        return False
    # elif results["Calmar Ratio"] <= 0.0:
    #     return False
    # elif results["Sharpe Ratio"] <= 0.0:
    #     return False
    # elif results["Sortino Ratio"] <= 0.0:
    #     return False
    elif results["Return [%]"] == None or results["Return [%]"] < 0.0:
        return False
    # elif results['Max. Drawdown [%]'] == None or results['Max. Drawdown [%]'] <= -90.0:
    #     return False
    # elif results['Avg. Drawdown [%]'] == None or results['Avg. Drawdown [%]'] <= -90.0:
    #     return False
    elif results['Avg. Trade [%]'] == None or results['Avg. Trade [%]'] <= 0.0:
        return False
    elif results['Profit Factor'] == None or results['Profit Factor'] <= 3.0:
        return False
    elif results['SQN'] == None or results['SQN'] <= 1.0:
        return False
    elif results['Worst Trade [%]'] == None or results['Worst Trade [%]'] <= -60.0:
        return False
    else:
        return True
