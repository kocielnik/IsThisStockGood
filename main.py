from isthisstockgood.DataFetcher import fetchDataForTickerSymbol
from isthisstockgood.server import create_app

app = create_app(fetchDataForTickerSymbol)
