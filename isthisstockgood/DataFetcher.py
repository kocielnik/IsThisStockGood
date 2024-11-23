import random
import logging
import isthisstockgood.RuleOneInvestingCalculations as RuleOne
from requests_futures.sessions import FuturesSession
from isthisstockgood.Active.MSNMoney import MSNMoney
from isthisstockgood.Active.YahooFinance import YahooFinanceAnalysis
from isthisstockgood.Active.Zacks import Zacks
from threading import Lock

logger = logging.getLogger("IsThisStockGood")


def fetchDataForTickerSymbol(ticker):
  """Fetches and parses all of the financial data for the `ticker`.

    Args:
      ticker: The ticker symbol string.

    Returns:
      Returns a dictionary of all the processed financial data. If
      there's an error, return None.

      Keys include:
        'roic',
        'eps',
        'sales',
        'equity',
        'cash',
        'long_term_debt',
        'free_cash_flow',
        'debt_payoff_time',
        'debt_equity_ratio',
        'margin_of_safety_price',
        'current_price'
  """
  if not ticker:
    return None

  data_fetcher = DataFetcher()
  data_fetcher.ticker_symbol = ticker

  # Make all network request asynchronously to build their portion of
  # the json results.
  data_fetcher.fetch_msn_money_data()
  data_fetcher.fetch_growth_rate()


  # Wait for each RPC result before proceeding.
  for rpc in data_fetcher.rpcs:
    rpc.result()

  msn_money = data_fetcher.msn_money
  future_growth_rate = data_fetcher.future_growth_rate
  # NOTE: Some stocks won't have analyst growth rates, such as newly listed stocks or some foreign stocks.
  five_year_growth_rate = future_growth_rate.five_year_growth_rate if future_growth_rate else 0
  # TODO: Use TTM EPS instead of most recent year
  margin_of_safety_price, sticker_price = \
      _calculateMarginOfSafetyPrice(msn_money.equity_growth_rates[-1], msn_money.pe_low, msn_money.pe_high, msn_money.eps[-1], five_year_growth_rate)
  payback_time = _calculatePaybackTime(msn_money.equity_growth_rates[-1], msn_money.last_year_net_income, msn_money.market_cap, five_year_growth_rate)
  computed_free_cash_flow = round(float(msn_money.free_cash_flow[-1]) * msn_money.shares_outstanding)
  template_values = {
    'ticker' : ticker,
    'name' : msn_money.name if msn_money and msn_money.name else 'null',
    'description': msn_money.description if msn_money and msn_money.description else 'null',
    'roic': msn_money.roic_averages if msn_money and msn_money.roic_averages else [],
    'eps': msn_money.eps_growth_rates if msn_money and msn_money.eps_growth_rates else [],
    'sales': msn_money.revenue_growth_rates if msn_money and msn_money.revenue_growth_rates else [],
    'equity': msn_money.equity_growth_rates if msn_money and msn_money.equity_growth_rates else [],
    'cash': msn_money.free_cash_flow_growth_rates if msn_money and msn_money.free_cash_flow_growth_rates else [],
    'total_debt' : msn_money.total_debt,
    'free_cash_flow' : computed_free_cash_flow,
    'debt_payoff_time' : round(float(msn_money.total_debt) / computed_free_cash_flow),
    'debt_equity_ratio' : msn_money.debt_equity_ratio if msn_money and msn_money.debt_equity_ratio >= 0 else -1,
    'margin_of_safety_price' : margin_of_safety_price if margin_of_safety_price else 'null',
    'current_price' : msn_money.current_price if msn_money and msn_money.current_price else 'null',
    'sticker_price' : sticker_price if sticker_price else 'null',
    'payback_time' : payback_time if payback_time else 'null',
    'average_volume' : msn_money.average_volume if msn_money and msn_money.average_volume else 'null'
  }
  return template_values


def _calculate_growth_rate_decimal(analyst_growth_rate, current_growth_rate):
  growth_rate = min(float(analyst_growth_rate), float(current_growth_rate))
  # Divide the growth rate by 100 to convert from percent to decimal.
  return growth_rate / 100.0


def _calculateMarginOfSafetyPrice(one_year_equity_growth_rate, pe_low, pe_high, ttm_eps, analyst_five_year_growth_rate):
  if not one_year_equity_growth_rate or not pe_low or not pe_high or not ttm_eps or not analyst_five_year_growth_rate:
    return None, None

  growth_rate = _calculate_growth_rate_decimal(analyst_five_year_growth_rate, one_year_equity_growth_rate)
  margin_of_safety_price, sticker_price = \
      RuleOne.margin_of_safety_price(float(ttm_eps), growth_rate, float(pe_low), float(pe_high))
  return margin_of_safety_price, sticker_price


# TODO: Figure out how to get TTM net income instead of previous year net income.
def _calculatePaybackTime(one_year_equity_growth_rate, last_year_net_income, market_cap, analyst_five_year_growth_rate):
  if not one_year_equity_growth_rate or not last_year_net_income or not market_cap or not analyst_five_year_growth_rate:
    return None

  growth_rate = _calculate_growth_rate_decimal(analyst_five_year_growth_rate, one_year_equity_growth_rate)
  payback_time = RuleOne.payback_time(market_cap, last_year_net_income, growth_rate)
  return payback_time


class DataFetcher():
  """A helper class that syncronizes all of the async data fetches."""

  USER_AGENT_LIST = [
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_5) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/13.1.1 Safari/605.1.15',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:77.0) Gecko/20100101 Firefox/77.0',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.97 Safari/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:77.0) Gecko/20100101 Firefox/77.0',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.97 Safari/537.36',
  ]

  def __init__(self,):
    self.lock = Lock()
    self.rpcs = []
    self.ticker_symbol = ''
    self.msn_money = None
    self.future_growth_rate = None
    self.yahoo_finance_chart = None
    self.error = False

  def _create_session(self):
    session = FuturesSession()
    session.headers.update({
      'User-Agent' : random.choice(DataFetcher.USER_AGENT_LIST)
    })
    return session

  def fetch_msn_money_data(self):
    """
    Fetching PE Ratios to calculate Sticker Price and Safety Margin Price. As well as
    the "Big 5" growth rate numbers.
    First we need to get an internal MSN stock id for a ticker and then fetch the data.
    """
    self.msn_money = MSNMoney(self.ticker_symbol)
    session = self._create_session()
    rpc = session.get(self.msn_money.get_ticker_autocomplete_url(), allow_redirects=True, hooks={
       'response': self.continue_fetching_msn_money_data,
    })
    self.rpcs.append(rpc)

  def continue_fetching_msn_money_data(self, response, *args, **kwargs):
    """
    After msn_stock_id was fetched in fetch_msn_money_data method
    we can now get the financials.
    """
    msn_stock_id = self.msn_money.extract_stock_id(response.text)
    session = self._create_session()
    rpc = session.get(self.msn_money.get_key_ratios_url(msn_stock_id), allow_redirects=True, hooks={
       'response': self.parse_msn_money_ratios_data,
    })
    self.rpcs.append(rpc)
    rpc = session.get(self.msn_money.get_quotes_url(msn_stock_id), allow_redirects=True, hooks={
       'response': self.parse_msn_money_quotes_data,
    })
    self.rpcs.append(rpc)
    rpc = session.get(self.msn_money.get_annual_statements_url(msn_stock_id), allow_redirects=True, hooks={
       'response': self.parse_msn_money_annual_statement_data,
    })
    self.rpcs.append(rpc)

  # Called asynchronously upon completion of the URL fetch from
  # `fetch_msn_money_data` and `continue_fetching_msn_money_data`.
  def parse_msn_money_ratios_data(self, response, *args, **kwargs):
    if response.status_code != 200:
      return
    if not self.msn_money:
      return
    result = response.text
    self.msn_money.parse_ratios_data(result)


  # Called asynchronously upon completion of the URL fetch from
  # `fetch_msn_money_data` and `continue_fetching_msn_money_data`.
  def parse_msn_money_quotes_data(self, response, *args, **kwargs):
    if response.status_code != 200:
      return
    if not self.msn_money:
      return
    result = response.text
    self.msn_money.parse_quotes_data(result)

  # Called asynchronously upon completion of the URL fetch from
  # `fetch_msn_money_data` and `continue_fetching_msn_money_data`.
  def parse_msn_money_annual_statement_data(self, response, *args, **kwargs):
    if response.status_code != 200:
      return
    if not self.msn_money:
      return
    result = response.text
    self.msn_money.parse_annual_report_data(result)

  def fetch_growth_rate_estimate(self):
    self.future_growth_rate = YahooFinanceAnalysis(self.ticker_symbol)
    session = self._create_session()
    rpc = session.get(self.future_growth_rate.url, allow_redirects=True, hooks={
       'response': self.parse_growth_rate_estimate,
    })
    self.rpcs.append(rpc)

  def fetch_growth_rate(self):
    session = self._create_session()
    self.future_growth_rate = Zacks(self.ticker_symbol)

    rpc = session.get(
      self.future_growth_rate.url,
      allow_redirects=True,
      hooks={
       'response': self.future_growth_rate.parse,
      }
    )
    self.rpcs.append(rpc)

  # Called asynchronously upon completion of the URL fetch from
  # `fetch_growth_rate_estimate`.
  def parse_growth_rate_estimate(self, response, *args, **kwargs):
    if response.status_code != 200:
      return
    if not self.future_growth_rate:
      return
    result = response.text
    success = self.future_growth_rate.parse_analyst_five_year_growth_rate(result)
    if not success:
      self.future_growth_rate = None

  def fetch_yahoo_finance_chart(self):
    self.yahoo_finance_chart = YahooFinanceChart(self.ticker_symbol)
    session = self._create_session()
    rpc = session.get(self.yahoo_finance_chart.url, allow_redirects=True, hooks={
       'response': self.parse_yahoo_finance_chart,
    })
    self.rpcs.append(rpc)

  # Called asynchronously upon completion of the URL fetch from
  # `fetch_growth_rate_estimate`.
  def parse_yahoo_finance_chart(self, response, *args, **kwargs):
    if response.status_code != 200:
      return
    if not self.yahoo_finance_chart:
      return
    result = response.text
    success = self.yahoo_finance_chart.parse_chart(result)
    if not success:
      self.yahoo_finance_chart = None
