import re

class Zacks:
    def __init__(self, ticker_symbol):
        base_url = "https://www.zacks.com/stock/quote"

        self.url = f"{base_url}/{ticker_symbol}/detailed-earning-estimates"
        self.ticker_symbol = ticker_symbol
        self.five_year_growth_rate = None
        self.maintenance_capital_expenditures = None

    def parse(self, response, **kwargs):
        if response.status_code != 200:
          print(f"{response.status_code}: {response.text}")
          return

        if not response.text:
          print("Response was empty")
          return

        try:
          self.five_year_growth_rate = self.get_growth_rate(response.text)
        except:
          self.five_year_growth_rate = None

    def get_estimate(self, lines, title):
      for i, line in enumerate(lines):
          if title in line:
              return lines[i+1]

    def get_growth_rate(self, text):
      lines = text.split("\n")

      result = self.get_estimate(lines, "Next 5 Years")

      if "NA" in result:
          result = self.get_estimate(lines, "Next Year")

      estimate = re.sub(r"[^\d\.]", "", result)

      try:
        result = float(estimate)
      except TypeError:
        print(
          "Unable to parse growth estimate from: {text}"
        )

      return float(estimate)
