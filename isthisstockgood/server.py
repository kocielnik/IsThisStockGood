import logging
import re
from datetime import date
from flask import Flask, request, render_template, json


def get_logger():
    logger = logging.getLogger("IsThisStockGood")

    handler = logging.StreamHandler()
    handler.setLevel(logging.WARNING)

    h_format = logging.Formatter('%(name)s - %(levelname)s : %(message)s')
    handler.setFormatter(h_format)

    logger.addHandler(handler)

    return logger

def create_app(fetchDataForTickerSymbol):
    app = Flask(__name__)

    @app.route(
        '/api/ticker/<unsanitized_ticker>/<unsanitized_growth_estimate>'
    )
    def api_ticker(
        unsanitized_ticker,
        unsanitized_growth_estimate
    ):
      ticker = re.sub(r'\W+', '', unsanitized_ticker)
      growth_estimate = int(re.sub(r'\W+', '', unsanitized_growth_estimate))

      template_values = fetchDataForTickerSymbol(ticker, growth_estimate=growth_estimate)

      if not template_values:
        data = render_template('json/error.json', **{'error' : 'Invalid ticker symbol'})
      else:
        data = render_template('json/stock_data.json', **template_values)

      return app.response_class(
        response=data,
        status=200,
        mimetype='application/json'
    )

    @app.route('/api')
    def api():
      data = {}
      return app.response_class(
        response=json.dumps(data),
        status=200,
        mimetype='application/json'
    )

    @app.route('/')
    def homepage():
      if request.environ['HTTP_HOST'].endswith('.appspot.com'):  #Redirect the appspot url to the custom url
        return '<meta http-equiv="refresh" content="0; url=https://isthisstockgood.com" />'

      template_values = {
        'page_title' : "Is This Stock Good?",
        'current_year' : date.today().year,
      }
      return render_template('home.html', **template_values)

    @app.route('/search', methods=['POST'])
    def search():
      if request.environ['HTTP_HOST'].endswith('.appspot.com'):  #Redirect the appspot url to the custom url
        return '<meta http-equiv="refresh" content="0; url=http://isthisstockgood.com" />'

      ticker = request.values.get('ticker')
      custom_growth_rate = request.values.get('custom_growth_rate')
      template_values = fetchDataForTickerSymbol(ticker, growth_estimate=int(custom_growth_rate))
      if not template_values:
        return render_template('json/error.json', **{'error' : 'Invalid ticker symbol'})
      return render_template('json/stock_data.json', **template_values)

    return app
