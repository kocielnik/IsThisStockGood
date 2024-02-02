import keyring as kr
from os import environ
import requests
from requests_toolbelt.sessions import BaseUrlSession


def get_api_key(email=environ['DEV_EMAIL']):
  return kr.get_password("financialmodelingprep.com", email)

def get_session():
  return BaseUrlSession(
    base_url="https://financialmodelingprep.com/api/v3/"
  )

def get_statement(symbol, api_key=get_api_key()):
  return requests.get(
    "https://financialmodelingprep.com/api/v3/balance-sheet-statement"
    f"/{symbol}"
    f"?period=annual&apikey={api_key}"
  ).json()[0]

def get_key_metrics(symbol, api_key=get_api_key()):
  return requests.get(
    "https://financialmodelingprep.com/api/v3/key-metrics"
    f"/{symbol}"
    f"?apikey={api_key}"
  ).json()[0]

def get_key_metrics_session(
    symbol, session=get_session(), api_key=get_api_key()
  ):
  return session.get(f"key-metrics/{symbol}?apikey={api_key}").json()[0]


class FinancialModelingPrep:
  def __init__(self, roic):
    self.roic = roic


def test_get_email():
  assert 'DEV_EMAIL' in environ

def test_get_password():
  password = get_api_key()
  assert isinstance(password, str)

def test_get_fmp_data():
  data = get_statement("AAPL")

  assert isinstance(data['longTermDebt'], int)

def test_get_roic():
  key_metrics = get_key_metrics("AAPL")

  assert isinstance(key_metrics['roic'], float)

def test_session():
  metrics = get_key_metrics_session("AAPL")
  assert isinstance(metrics['roic'], float)

def test_fmp():
  fmp = FinancialModelingPrep(roic=0.1)
  assert fmp.roic == 0.1
