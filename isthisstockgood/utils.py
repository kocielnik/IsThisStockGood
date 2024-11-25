from isthisstockgood.CompanyInfo import CompanyInfo
from isthisstockgood.DataFetcher import DataFetcher


def get_growth_rate(ticker):
    data_fetcher = DataFetcher()
    data_fetcher.ticker_symbol = ticker

    # Make all network request asynchronously to build their portion of
    # the json results.
    data_fetcher.fetch_growth_rate()

    # Wait for each RPC result before proceeding.
    for rpc in data_fetcher.rpcs:
      rpc.result()

    return data_fetcher.future_growth_rate

def get_msn_money_data(ticker):
    data_fetcher = DataFetcher()
    data_fetcher.ticker_symbol = ticker

    # Make all network request asynchronously to build their portion of
    # the json results.
    data_fetcher.fetch_msn_money_data()

    # Wait for each RPC result before proceeding.
    for rpc in data_fetcher.rpcs:
      rpc.result()

    return CompanyInfo(**vars(data_fetcher.msn_money))

def get_yahoo_growth_estimate(ticker):
    data_fetcher = DataFetcher()
    data_fetcher.ticker_symbol = ticker

    # Make all network request asynchronously to build their portion of
    # the json results.
    data_fetcher.fetch_growth_rate_estimate()

    # Wait for each RPC result before proceeding.
    for rpc in data_fetcher.rpcs:
      rpc.result()

    return data_fetcher.future_growth_rate
