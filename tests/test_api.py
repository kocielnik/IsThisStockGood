import json
from dataclasses import dataclass
from isthisstockgood.server import create_app
from isthisstockgood.DataFetcher import Collector


class RPC:
    def result(self):
        return {
          'companyMetrics' : [self.get_bvps(year) for year in range(10)]
        }

    def get_bvps(self, year):
        return {
          'fiscalPeriodType' : 'Annual',
          'bookValuePerShare' : year
        }


class MockSession:
    headers: dict = {}

    def get(self, *args, **kwargs):
        return RPC()


def test_import_app():
    app = create_app(Collector())

    with app.test_client() as test_client:
        test_client = app.test_client()
        res = test_client.get('/api')
        data = res.text
        assert json.loads(data) == {}
        assert res.status_code == 200

def test_get_data():
    app = create_app(Collector())

    with app.test_client() as test_client:
        test_client = app.test_client()

        res = test_client.get('/api/ticker/nvda')
        assert res.status_code == 200

        assert res.json['debt_payoff_time'] >= 0

def test_get_ten_cap_price():
    app = create_app(Collector())

    with app.test_client() as test_client:
        test_client = app.test_client()
        res = test_client.get('/api/ticker/nvda')
        assert res.json['ten_cap_price'] > 0

def test_ten_cap_price_has_two_places_precision():
    app = create_app(Collector())

    with app.test_client() as test_client:
        test_client = app.test_client()
        res = test_client.get('/api/ticker/nvda')

        price = res.json['ten_cap_price']

        assert round(price, 2) == price
