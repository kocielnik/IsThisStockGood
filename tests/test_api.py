import json
from isthisstockgood.server import create_app
from isthisstockgood.DataFetcher import fetchDataForTickerSymbol


def test_import_app():
    app = create_app(fetchDataForTickerSymbol)

    with app.test_client() as test_client:
        test_client = app.test_client()
        res = test_client.get('/api')
        data = res.text
        assert json.loads(data) == {}
        assert res.status_code == 200

def test_get_data():
    app = create_app(fetchDataForTickerSymbol)

    with app.test_client() as test_client:
        test_client = app.test_client()
        res = test_client.get('/api/ticker/nvda')
        assert res.status_code == 200

        data = json.loads(res.text)
        assert data['debt_payoff_time'] == 0
        assert data['sticker_price'] > 0.0
        assert data['payback_time'] > 1
