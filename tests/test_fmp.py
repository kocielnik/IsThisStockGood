import keyring as kr
from os import environ


def get_api_key(email):
  return kr.get_password("financialmodelingprep.com", email)

def test_get_email():
  assert 'DEV_EMAIL' in environ

def test_get_password():
  password = get_api_key(environ['DEV_EMAIL'])
  assert isinstance(password, str)
