from poloniex import Poloniex
import pandas as pd


def get_poloniex_data(cryptocurrency, period, start_time):
    polo = Poloniex()
    data = polo.returnChartData(cryptocurrency, period=period, start=start_time)
    dataframe = pd.DataFrame(data)
    return dataframe


def priceStableTest():
    early_time = 1540392912
    btc_chart_data = get_poloniex_data('USDT_BTC', 300, early_time)


if __name__ == "__main__":
    priceStableTest()
    # early_time = 1540392912
    # btc_chart_data = get_poloniex_data('USDT_BTC', 300, early_time)
    # print(btc_chart_data)
