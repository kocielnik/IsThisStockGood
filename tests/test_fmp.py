import keyring as kr
from os import environ
import requests


def get_statement(symbol):
  email = environ['DEV_EMAIL']
  api_key = get_api_key(email)

  return requests.get(
    "https://financialmodelingprep.com/api/v3/balance-sheet-statement"
    f"/{symbol}"
    f"?period=annual&apikey={api_key}"
  ).json()[0]

def get_api_key(email):
  return kr.get_password("financialmodelingprep.com", email)

def test_get_email():
  assert 'DEV_EMAIL' in environ

def test_get_password():
  password = get_api_key(environ['DEV_EMAIL'])
  assert isinstance(password, str)

def test_get_fmp_data():
  data = get_statement("AAPL")

  assert isinstance(data['longTermDebt'], int)
