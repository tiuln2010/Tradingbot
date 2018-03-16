import json
import os
from pymongo import MongoClient
from multiprocessing.pool import ThreadPool

import ccxt

from .coinone.public import Coinone_Public
from .secret.secret import key

from .slack_alert import Slack_Alert
from .decorator import timeit, save_err

class SaveData :
    def __init__(self, exchange = 'binance', symbol = 'BTC/USDT', symbols = ['BTC/USDT', 'ETH/USDT']):
        self.exchange = exchange
        self.symbol = symbol
        self.symbols = symbols

    def _save_json(self, name, res):
        def _name_path(name):
            path = "./Data"
            absPath = os.path.abspath(path)
            jsonPath = "{}\\{}.log".format(absPath, name)
            return jsonPath
        jsonPath = _name_path(name)
        contents = open(jsonPath, 'a')
        contents.write(res)
        contents.close()
    
    def _save_mongo(self, db, col, ress):
        client = MongoClient()
        database = getattr(client, db)
        collection = getattr(database, col)
        res = collection.insert_many(ress)
    
    def save_ob(self):
        @timeit
        @save_err
        def binance(symbol) :
            bi = ccxt.binance()
            bi.apiKey = key['Binance']['ApiKey']
            bi.secret = key['Binance']['Secret']
            ob = bi.fetch_order_book(symbol)
            timestamp = ob['timestamp']
            re_symbol = symbol.replace("/","")
            res = self._save_mongo(self.exchange, 'OB_'+re_symbol, ob)
            return res, timestamp

        def coinone(symbol) :
            co = Coinone_Public()
            ob = co.fetch_order_book(symbol)
            timestamp = ob['timestamp']
            res = self._save_mongo(self.exchange, 'OB_'+symbol, ob)            
            return res, timestamp

        def bithumb(symbol) :
            bit = ccxt.bithumb()
            ob = bit.fetch_order_book(symbol)
            timestamp = ob['timestamp']
            re_symbol = symbol.replace("/KRW","")
            res = self._save_mongo(self.exchange, 'OB_'+re_symbol, ob)            
            return res, timestamp

        if self.exchange == 'binance':
            res, timestamp = binance(self.symbol)
        elif self.exchange == 'coinone':
            res, timestamp = coinone(self.symbol)
        elif self.exchange == 'bithumb':
            res, timestamp = bithumb(self.symbol)
        print(res, timestamp)

        return res, timestamp

    @timeit
    @save_err
    def save_obs(self):
        pool = ThreadPool()
        if self.exchange == 'binance':
            bi = ccxt.binance()
            bi.apiKey = key['Binance']['ApiKey']
            bi.secret = key['Binance']['Secret']
            func = bi.fetch_order_book
        elif self.exchange == 'coinone':
            co = Coinone_Public()
            func = co.fetch_order_book
        elif self.exchange == 'bithumb':
            bit = ccxt.bithumb()
            func = bit.fetch_order_book
        
        asyncs = []
        for symbol in self.symbols:
            async_res = pool.apply_async(func, (symbol,))     
            
            #change symbol for save in mongodb
            if self.exchange == 'binance':
                symbol = symbol.replace("/","")
            elif self.exchange == 'bithumb':
                symbol = symbol.replace("/KRW","")
            
            tu = (symbol, async_res)
            asyncs.append(tu)
        res = []

        for symbol, asy in asyncs:
            ob = asy.get()
            dic = {
                'symbol' : symbol,
                'order_book' : ob,
                'timestamp' : ob['timestamp']
                    }
            res.append(dic)
            msg = str(symbol) + str(ob['timestamp']) + str(self.exchange) + "\n"
            self._save_json('timestamp', msg)

        client = MongoClient()
        database = getattr(client, self.exchange)
        for dic in res:
            collection = getattr(database, 'OB_'+dic['symbol'])
            res = collection.insert(dic['order_book'])
        return res