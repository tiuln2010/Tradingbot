import json
import os
from pymongo import MongoClient

import ccxt

from .coinone.public import Coinone_Public
from .secret.secret import key

from .slack_alert import Slack_Alert
from .decorator import timeit, save_err

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
        t = Slack_Alert(msg)
        t.send_msg()
    
    def _save_mongo(self, db, col,res):
        client = MongoClient()
        database = getattr(client, db)
        collection = getattr(database, col)
        res = collection.insert_one(res)

    
    def save_ob(self):

        @timeit
        @save_err
        def binance(symbol) :
            bi = ccxt.binance()
            bi.apiKey = key['Binance']['ApiKey']
            bi.secret = key['Binance']['Secret']
            ob = bi.fetch_order_book(symbol)
            re_symbol = symbol.replace("/","")
            res = self._save_mongo(self.exchange, 'OB_'+re_symbol, ob)
            return res

        def coinone(symbol) :
            co = Coinone_Public()
            ob = co.fetch_order_book(symbol)
            res = self._save_mongo(self.exchange, 'OB_'+symbol, ob)            
            return res

        def bithumb(symbol) :
            bit = ccxt.bithumb()
            ob = bit.fetch_order_book(symbol)
            re_symbol = symbol.replace("/KRW","")
            res = self._save_mongo(self.exchange, 'OB_'+re_symbol, ob)            
            return res

        if self.exchange == 'binance':
            res = binance(self.symbol)
        elif self.exchange == 'coinone':
            res = coinone(self.symbol)
        elif self.exchange == 'bithumb':
            res = bithumb(self.symbol)
            
        return res
