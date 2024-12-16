from isthisstockgood.DataFetcher import fetchDataForTickerSymbol
from isthisstockgood.server import create_app

app = create_app(fetchDataForTickerSymbol)
app.run(host='127.0.0.1', port=8080, debug=True)
