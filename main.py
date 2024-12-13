from isthisstockgood.DataFetcher import Collector
from isthisstockgood.server import create_app


if __name__ == '__main__':
  data_collector = Collector()
  app = create_app(data_collector)
  app.run(host='127.0.0.1', port=8080, debug=True)
