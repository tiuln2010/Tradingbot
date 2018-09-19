import ccxt

from .coinone.public import Coinone_Public
from .secret.secret import key

from .slack_alert import Slack_Alert
from .decorator import timeit, save_err

class Fetch_order_book:
    def __init__(self, exchange, symbol):
        self.exchange = exchange
        self.symbol = symbol

    @ob_list
    def binance(self, symbol) :
        bi = ccxt.binance()
        bi.apiKey = key['Binance']['ApiKey']
        bi.secret = key['Binance']['Secret']
        ob = bi.fetch_order_book(symbol)
        re_symbol = symbol.replace("/","")
        res = {'db' = self.exchange, 'col' = 'OB_'+re_symbol, 'res' = ob}
        return res

    @ob_list
    def coinone(self, symbol) :
        co = Coinone_Public()
        ob = co.fetch_order_book(symbol)
        res = {'db' = self.exchange, 'col' = 'OB_'+symbol, 'res' = ob}
        return res

    @ob_list
    def bithumb(self, symbol) :
        bit = ccxt.bithumb()
        ob = bit.fetch_order_book(symbol)
        re_symbol = symbol.replace("/KRW","")
        res = {'db' = self.exchange, 'col' = 'OB_'+re_symbol, 'res' = ob}
        return res

    def fetch_order_book(self):
        if self.exchange == 'binance':
            res = self.binance(self.symbol)
        elif self.exchange == 'coinone':
            res = self.coinone(self.symbol)
        elif self.exchange == 'bithumb':
            res = self.bithumb(self.symbol)
        return res
