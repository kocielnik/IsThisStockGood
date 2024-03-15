#!/usr/bin/env python3

import logging
import os
import sys
from isthisstockgood.Database import SQLite
from isthisstockgood.DataFetcher import fetchDataForTickerSymbol

def populate_database():
    print("Connecting to database...")
    db = SQLite()
    print("Adding stocks...")
    table_name = "stocks"
    if len(sys.argv) == 2:
        ticker = sys.argv[1]
        db.insertDataIntoTableForTicker(table_name, ticker, fetchDataForTickerSymbol(ticker,None))
    else:
        stock_list = db.get_stocks_to_be_fetched()
        for ticker_exchange in stock_list:
          db.insertDataIntoTableForTicker(table_name, ticker_exchange[0], fetchDataForTickerSymbol(ticker_exchange[0], ticker_exchange[1]))

def test_ticker():
    logging.basicConfig(level=logging.DEBUG)

    ticker = sys.argv[1]
    exchange = None
    if len(sys.argv) == 3:
        exchange = sys.argv[2]

    r = fetchDataForTickerSymbol(ticker, exchange)
    print(r)