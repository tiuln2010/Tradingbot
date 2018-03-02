import ccxt

from .coinone.public import Coinone_Public
from .secret.secret import key

from .repeat import Repeat
from .ex_fee import trade_fee

from .trade_alert import Trade_alert

from pprint import pprint
import os
import json

class Arbitrage :
    def __init__(self, ex_a, ex_b, coin_x, coin_y):
        self.ex_a = ex_a
        self.ex_b = ex_b
        self.coin_x = coin_x
        self.coin_y = coin_y

    def _fetch_price_dict(self, ex_a, ex_b, coin_x, coin_y):
        def _name_path(name):
            path = "./Data"
            absPath = os.path.abspath(path)
            jsonPath = "{}\\{}.json".format(absPath, name)
            return jsonPath

        def _save_json(self, name, res):
            jsonPath = _name_path(name)
            contents = open(jsonPath, 'w')
            json.dump(res, contents)
            contents.close()
            print("{}.json is saved".format(name))
        
        def _load_json(name):
            jsonPath = _name_path(name)
            res = json.load(open(jsonPath))
            print("{}.json is loaded".format(name))
            return res

        def _first_one(_type, orderbook):
            one = orderbook[_type+'s'][0][0]
            return one

        def _change_into_krw(ex, price):
            if ex == 'binance':
                BTC_USDT = _first_one('bid', _load_json('binance_btcUSDT'))
                USDT = 1080
                _res_price = price * BTC_USDT * USDT
            return _res_price

        def _fetch_price(ex, coin, _type):
            if ex == 'binance':
                ob = _load_json('binance_'+coin+'BTC')
                price = _first_one(_type, ob)
                krw_price = _change_into_krw(ex, price)
            elif ex == 'coinone':
                ob = _load_json('coinone_'+coin.lower())
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

    def _set_profit_arguments(self, price_dict):
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

            def _set_arbitrage_arguments(arg):
                _arbitrage_arguments = {
                    'a_sell_price' : arg[0],
                    'a_buy_price' : arg[1],
                    'b_buy_price' : arg[2],
                    'b_sell_price' : arg[3]
                }
                return _arbitrage_arguments

            if _ax_is_higer_than_ay(li):
                arg = [dic['ax_ask'], dic['ay_bid'], dic['bx_bid'], dic['by_ask']]
                res = _set_arbitrage_arguments(arg)
            else:
                arg = [dic['ay_ask'],dic['ax_bid'],dic['by_bid'],dic['bx_ask']]
                res = _set_arbitrage_arguments(arg)
            return res        

        bid_ask_average_list = _make_bid_ask_average_list(price_dict)
        arg_for_calc_profit = _find_better_arbitrage_chance(bid_ask_average_list, price_dict)
        return arg_for_calc_profit

    def _calc_arbitrage_profit_rate(self, arg):        
        a_sell_coin = 100000
        Earn = a_sell_coin * arg['a_sell_price'] * (1 - trade_fee[self.ex_a])
        b_Earn = a_sell_coin / (1 - trade_fee[self.ex_b]) * arg['b_buy_price'] * (1 + trade_fee[self.ex_b])
        Cost = b_Earn / arg['b_sell_price'] / (1 + trade_fee[self.ex_a]) * arg['a_buy_price']

        profit = Earn - Cost
        profit_rate = profit / (Earn + b_Earn)
        return profit_rate

    def arbitrage(self):
        price_dict = self._fetch_price_dict(self.ex_a, self.ex_b, self.coin_x, self.coin_y)
        arg = self._set_profit_arguments(price_dict)
        profit_rate = self._calc_arbitrage_profit_rate(arg)
        t = Trade_alert(profit_rate)
        t.send_msg()
        return profit_rate
