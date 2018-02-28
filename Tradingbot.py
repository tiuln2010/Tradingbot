import ccxt

from Lib.coinone.public import Public
from Lib.trade_alert import Trade_alert

from pprint import pprint
from recorder import Repeat

# def save(msg):
#     with File("log.txt", 'a'):
#         pprint(str(msg))

bi = ccxt.binance()

bi.apiKey = '9endinNUJkuKffy5b0kh9T3elnTscRCkepLa2TOyEhrdYyJSNGpVR5bC819XkN5O'
bi.secret = 'dL1S08eF2k2o9frupRr5QTNMoAb2H3jJV9t8yfyeffJfRkWKFwsgEFypnJqUfz4LAPI'

Public = Public()

#call bid, ask

def bid(orderbook):
    bid = orderbook['bids'][0]
    return bid

def ask(orderbook):
    ask = orderbook['asks'][0]
    return ask


def gap():
    #bi = ccxt.bitfinex()
    coinone_xrp_orderbook = Public.fetch_order_book(currency = 'xrp')
    coinone_qtum_orderbook = Public.fetch_order_book(currency = 'qtum')

    
    binance_xrp_orderbook = bi.fetch_order_book('XRP/BTC')
    binance_qtum_orderbook = bi.fetch_order_book('QTUM/BTC')
    binance_btc_orderbook = bi.fetch_order_book('BTC/USDT')

        
    co_qtum_ask = float(ask(coinone_qtum_orderbook)['price'])
    co_xrp_bid = float(bid(coinone_xrp_orderbook)['price'])

    co_qtum_bid = float(bid(coinone_qtum_orderbook)['price'])
    co_xrp_ask = float(ask(coinone_xrp_orderbook)['price'])


    
    btc = float(binance_btc_orderbook['asks'][0][0])*1089
    bi_qtum_bid = float(binance_qtum_orderbook['bids'][0][0])*btc
    bi_xrp_ask = float(binance_xrp_orderbook['asks'][0][0])*btc
    
    bi_qtum_ask = float(binance_qtum_orderbook['asks'][0][0])*btc
    bi_xrp_bid = float(binance_xrp_orderbook['bids'][0][0])*btc

    #1 sin
    co_bi_qtum = co_qtum_bid/bi_qtum_ask
    co_bi_xrp = co_xrp_ask/bi_xrp_bid
    #2 sin
    bi_co_xrp = co_xrp_bid/bi_xrp_ask
    bi_co_qtum = co_qtum_ask/bi_qtum_bid

    a = (co_bi_qtum - co_bi_xrp)
    b = (bi_co_xrp - bi_co_qtum)

    msg =(
    'sell qtum in coinone {}, \n'.format(str(a)) +
    'sell xrp in coinone {} \n'.format(str(b)) 
    )

    Trade_alert.send_msg(msg)

def test():
    print(123)


r = Repeat(gap, 1)
r.start()
