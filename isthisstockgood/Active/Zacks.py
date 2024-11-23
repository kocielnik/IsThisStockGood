import re

class Zacks:
    def __init__(self, ticker_symbol):
        base_url = "https://www.zacks.com/stock/quote"

        self.url = f"{base_url}/{ticker_symbol}/detailed-earning-estimates"
        self.ticker_symbol = ticker_symbol
        self.five_year_growth_rate = None
        self.maintenance_capital_expenditures = None
        self.errors = []

    def parse(self, response, **kwargs):
        if response.status_code != 200:
          self.errors.append(response.text)
          return
        if not response.text:
          self.errors.append("No data arrived.")
          return

        try:
          self.five_year_growth_rate = self.get_growth_rate(response.text)
        except:
          self.five_year_growth_rate = None

    def get_growth_rate(self, text):
      lines = text.split("\n")

      for i, line in enumerate(lines):
          if "Next 5 Years" in line:
              result = lines[i+1]

      estimate = re.sub(r"[^\d\.]", "", result)

      try:
        result = float(estimate)
      except TypeError:
        self.errors.append(
          "Unable to parse growth estimate from: {text}"
        )

      return float(estimate)
