import requests

import config


class Price_service:



    def get_current_price(self, symbol):
        key = "https://api.binance.com/api/v3/ticker/price?symbol="
        url = key + symbol
        data = requests.get(url)
        data = data.json()
        return float(data['price'])
