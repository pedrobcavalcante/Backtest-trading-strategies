def generateWeightedAverageTrade(result):
    # return result['# Trades'] * result['Avg. Trade [%]'] * result['Exposure Time [%]']
    return result['# Trades'] * result['Avg. Trade [%]'] / 100
