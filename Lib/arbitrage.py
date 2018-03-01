import ccxt

from coinone.public import Coinone_Public
from secret.secret import key

from trade_alert import Trade_alert
from repeat import Repeat
from ex_fee import trade_fee

from pprint import pprint
import os
import json

def _name_path(name):
    path = "./Data"
    absPath = os.path.abspath(path)
    jsonPath = "{}\\{}.json".format(absPath, name)
    return jsonPath

def _save_json(name, res):
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

def save_ob(ex, coin):
    exIns = _mk_ins(ex)
    if ex == 'binance':
        _coin = _change_symbol(ex, coin)
        ob = exIns.fetch_order_book(_coin)
        _save_json('binance_'+coin+'BTC', ob)
    elif ex == 'coinone':
        ob = exIns.fetch_order_book(coin)
        _save_json('coinone_'+coin, ob)

def _mk_ins(ex):
    if ex == 'binance':
        bi = ccxt.binance()
        bi.apiKey = key['Binance']['ApiKey']
        bi.secret = key['Binance']['Secret']
        res = bi
    elif ex == 'coinone':
        res = Coinone_Public()
    return res

def _change_symbol(ex, coin):
    if ex == 'binance':
        coin = coin.upper()+'/BTC'
    return coin

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
        ob = _load_json('coinone_'+coin)
        prices = _first_one(_type, ob)
        krw_price = prices

    return krw_price

# 만들어야 될 것 : 거래소랑 코인, 타입을 넣으면, 해당하는 0번째 가격을 불러오는 함수를 만든다. 불러오는 가격은 반드시 한화여야 하고, 거래소에 따라 다른 방식으로 가공하도록 만들어야 한다.

def gap(ex_a, ex_b, coin_x, coin_y):

    save_ob(ex_a, coin_x)
    save_ob(ex_a, coin_y)
    save_ob(ex_b, coin_x)
    save_ob(ex_b, coin_y)
    bi = _mk_ins('binance')
    ob = bi.fetch_order_book('BTC/USDT')
    _save_json('binance_btcUSDT', ob)
    
    ax_bid = _fetch_price(ex_a, coin_x, 'bid')
    ax_ask = _fetch_price(ex_a, coin_x, 'ask')
    ay_bid = _fetch_price(ex_a, coin_y, 'bid')
    ay_ask = _fetch_price(ex_a, coin_y, 'ask')
    
    bx_bid = _fetch_price(ex_b, coin_x, 'bid')
    bx_ask = _fetch_price(ex_b, coin_x, 'ask')
    by_bid = _fetch_price(ex_b, coin_y, 'bid')
    by_ask = _fetch_price(ex_b, coin_y, 'ask')

    ax = (ax_bid + ax_ask) / 2
    ay = (ay_bid + ax_ask ) / 2
    bx = (bx_bid + bx_ask) / 2
    by = (by_bid + bx_ask ) / 2

    if ax/bx > ay/by :
        a_sell_price = ax_ask
        a_buy_price = ay_bid
        b_buy_price = bx_bid
        b_sell_price = by_ask
        
    else:
        a_sell_price = ay_ask
        a_buy_price = ax_bid
        b_buy_price = by_bid
        b_sell_price = bx_ask
    
    a_sell_coin = 100000
    Earn = a_sell_coin * a_sell_price * (1 - trade_fee[ex_a])
    b_Earn = a_sell_coin / (1 - trade_fee[ex_b]) * b_buy_price * (1 + trade_fee[ex_b])
    Cost = b_Earn / b_sell_price / (1 + trade_fee[ex_a]) * a_buy_price

    profit = Earn - Cost
    profit_rate = profit / (Earn + b_Earn)

    msg = profit_rate

    Trade_alert.send_msg(msg)

gap('coinone', 'binance', 'xrp', 'qtum')

