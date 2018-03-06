import ccxt

from .coinone.public import Coinone_Public
from .secret.secret import key
from .repeat import Repeat
from .ex_fee import trade_fee
from .slack_alert import Slack_Alert

from pprint import pprint
from pymongo import MongoClient
import os
import json

class Arbitrage :
    def __init__(self, ex_a, ex_b, coin_x, coin_y):
        self.ex_a = ex_a
        self.ex_b = ex_b
        self.coin_x = coin_x
        self.coin_y = coin_y

    def _name_path(self, name):
        path = "./Data"
        absPath = os.path.abspath(path)
        jsonPath = "{}\\{}.log".format(absPath, name)
        return jsonPath

    def _save_log(self, name, res):
        jsonPath = self._name_path(name)
        contents = open(jsonPath, 'a')
        contents.write(res)
        contents.close()
        print("{}.json is saved".format(name))

    def _fetch_price_dict(self, ex_a, ex_b, coin_x, coin_y):
        
        def _load_json(name):
            jsonPath = self._name_path(name)
            res = json.load(open(jsonPath))
            print("{}.json is loaded".format(name))
            return res

        def _load_db(exchange, coin):
            print(exchange, coin)
            c = MongoClient()
            col = getattr(c, exchange)
            db = getattr(col, 'OB_'+coin)
            count = db.count() -1
            data = db.find()[count]
            return data

        def _first_one(_type, orderbook):
            one = orderbook[_type+'s'][0][0]
            return one

        def _change_into_krw(ex, price):
            if ex == 'binance':
                BTC_USDT = _first_one('bid', _load_db(ex, 'BTCUSDT'))
                USDT = 1080
                _res_price = price * BTC_USDT * USDT
            return _res_price

        def _fetch_price(ex, coin, _type):
            if ex == 'binance':
                ob = _load_db(ex, coin.upper()+'BTC')
                price = _first_one(_type, ob)
                krw_price = _change_into_krw(ex, price)
            elif ex == 'coinone':
                ob = _load_db(ex, coin)
                krw_price = _first_one(_type, ob)
            elif ex == 'bithumb':
                ob = _load_db(ex, coin.upper())
                krw_price = _first_one(_type, ob)
            return krw_price

        price_dict = {
        'ax_bid' : _fetch_price(ex_a, coin_x, 'bid'),
        'ax_ask' : _fetch_price(ex_a, coin_x, 'ask'),
        'ay_bid' : _fetch_price(ex_a, coin_y, 'bid'),
        'ay_ask' : _fetch_price(ex_a, coin_y, 'ask'),
        'bx_bid' : _fetch_price(ex_b, coin_x, 'bid'),
        'bx_ask' : _fetch_price(ex_b, coin_x, 'ask'),
        'by_bid' : _fetch_price(ex_b, coin_y, 'bid'),
        'by_ask' : _fetch_price(ex_b, coin_y, 'ask')
        }
        return price_dict

    def _set_buy_sell_arguments(self, price_dict):
        def _calc_bid_ask_average(bid, ask):
            average = (bid + ask) /2
            return average

        def _make_bid_ask_average_list(price_dict):
            bid_ask_average_list = {
            'ax' : _calc_bid_ask_average(price_dict['ax_bid'], price_dict['ax_ask']),
            'ay' : _calc_bid_ask_average(price_dict['ay_bid'], price_dict['ax_ask']),
            'bx' : _calc_bid_ask_average(price_dict['bx_bid'], price_dict['bx_ask']),
            'by' : _calc_bid_ask_average(price_dict['by_bid'], price_dict['bx_ask'])
            }
            return bid_ask_average_list

        def _find_better_arbitrage_chance(li, dic):
            def _ax_is_higer_than_ay(li):
                flag = li['ax']/li['bx'] > li['ay']/li['by']
                return flag

            if _ax_is_higer_than_ay(li):
                arg = {
                    'sell' : self.coin_x,
                    'buy' : self.coin_y,
                    'a_sell_price' : dic['ax_bid'], 
                    'a_buy_price' : dic['ay_ask'], 
                    'b_buy_price' : dic['bx_ask'], 
                    'b_sell_price' : dic['by_bid']
                }
            else:
                arg = {
                    'sell' : self.coin_y,
                    'buy' : self.coin_x,
                    'a_sell_price' : dic['ay_bid'],
                    'a_buy_price' : dic['ax_ask'],
                    'b_buy_price' : dic['by_ask'],
                    'b_sell_price' : dic['bx_bid']
                }
            return arg

        bid_ask_average_list = _make_bid_ask_average_list(price_dict)
        buy_sell_arg = _find_better_arbitrage_chance(bid_ask_average_list, price_dict)
        return buy_sell_arg

    def _calc_arbitrage_profit_rate(self, arg):        
        a_sell_coin = 100000
        Earn = a_sell_coin * arg['a_sell_price'] * (1 - trade_fee[self.ex_a])
        b_Earn = a_sell_coin / (1 - trade_fee[self.ex_b]) * arg['b_buy_price'] * (1 + trade_fee[self.ex_b])
        Cost = b_Earn / arg['b_sell_price'] / (1 + trade_fee[self.ex_a]) * arg['a_buy_price']

        profit = Earn - Cost
        profit_rate = profit / (Earn + b_Earn)
        return profit_rate

    def _result_msg(self, buy_sell_arg, profit_rate):
        res = (
            "Exchange    : {}, {}\n".format(self.ex_a, self.ex_b) +
            "Sell/buy    : {}, {}\n".format(buy_sell_arg['sell'], buy_sell_arg['buy']) +
            "Profit rate : {} \n".format(profit_rate)
            )
        return res

    def arbitrage(self):
        price_dict = self._fetch_price_dict(self.ex_a, self.ex_b, self.coin_x, self.coin_y)
        buy_sell_arg = self._set_buy_sell_arguments(price_dict)
        profit_rate = self._calc_arbitrage_profit_rate(buy_sell_arg)
        if profit_rate > 0.002:
            msg = self._result_msg(buy_sell_arg, profit_rate)
            self._save_log('output', msg)
            m = Slack_Alert()
            m.send_msg(msg)

