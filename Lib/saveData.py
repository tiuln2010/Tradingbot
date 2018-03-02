import json
import os

import ccxt
from .coinone.public import Coinone_Public
from .secret.secret import key
from .trade_alert import Trade_alert

class SaveData :
    def __init__(self, exchange, symbol):
        self.exchange = exchange
        self.symbol = symbol

    def _save_json(self, name, res):
        def _name_path(name):
            path = "./Data"
            absPath = os.path.abspath(path)
            jsonPath = "{}\\{}.json".format(absPath, name)
            return jsonPath
        jsonPath = _name_path(name)
        contents = open(jsonPath, 'w')
        json.dump(res, contents)
        contents.close()
        msg = "{}.json is saved".format(name)
        t = Trade_alert(msg)
        t.send_msg()
    
    def _save_mongo(self, exchange, symbol, res):
        

    def save_ob(self):
        def _mk_ins(exchange):
            if exchange == 'binance':
                bi = ccxt.binance()
                bi.apiKey = key['Binance']['ApiKey']
                bi.secret = key['Binance']['Secret']
                res = bi    
            elif exchange == 'coinone':
                res = Coinone_Public()
            return res

        exIns = _mk_ins(self.exchange)
        ob = exIns.fetch_order_book(self.symbol)
            
        if self.exchange == 'binance':
            symbol = self.symbol.replace("/","")
            self._save_json('binance_'+symbol, ob)
        elif self.exchange == 'coinone':
            self._save_json('coinone_'+self.symbol, ob)
