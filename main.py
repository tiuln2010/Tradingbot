from Lib.arbitrage import Arbitrage
from Lib.repeat import Repeat, Multi
from Lib.saveData import SaveData


from Lib.decorator import timeit, save_err
from Lib.slack_alert import Slack_Alert

import itertools
import time
import threading
import traceback
import datetime

'''
ARGUMENTS
'''

ob =[
    {'exchange' : 'binance', 'symbol' : 'BTCUSDT'},

    # {'exchange' : 'binance', 'symbol' : 'XRP/BTC'},
    # {'exchange' : 'binance', 'symbol' : 'QTUM/BTC'},
    # {'exchange' : 'binance', 'symbol' : 'IOTA/BTC'},
    # {'exchange' : 'binance', 'symbol' : 'BCH/BTC'},
    # {'exchange' : 'binance', 'symbol' : 'ETC/BTC'},
    # {'exchange' : 'binance', 'symbol' : 'LTC/BTC'},        
    # {'exchange' : 'binance', 'symbol' : 'ETH/BTC'},        

    # {'exchange' : 'coinone', 'symbol' : 'xrp'},
    # {'exchange' : 'coinone', 'symbol' : 'qtum'},
    # {'exchange' : 'coinone', 'symbol' : 'iota'},
    # {'exchange' : 'coinone', 'symbol' : 'bch'},
    # {'exchange' : 'coinone', 'symbol' : 'etc'},
    # {'exchange' : 'coinone', 'symbol' : 'ltc'},
    # {'exchange' : 'coinone', 'symbol' : 'eth'}
]   

ar_coin_list =[
    'xrp', 'qtum'#, 'iota', 'bch', 'etc', 'ltc', 'eth'
]

'''
ARGUMETNS
'''

#Methods

@timeit
def _runprocess(multi):
    processes = multi.run_process()
    multi.wait_end(processes)

@save_err
def _iterrator(li):
    multi = Multi(li)
    _runprocess(multi)

def _combination(li):
    coin_combination_list = list(itertools.combinations(li, 2))
    return coin_combination_list

def _make_ar_kwargs_list(ex_a, ex_b, coin_combination_list):
    ar_kwarg_list = []
    for li in coin_combination_list:
        ar = {
            'ex_a' : ex_a, 'ex_b' : ex_b, 'coin_x' : li[0], 'coin_y' : li[1]
        }
        ar_kwarg_list.append(ar)
    return ar_kwarg_list

def _make_ar_func_list(ar_kwarg_list):
    func_list = []
    for ar_kwarg in ar_kwarg_list:
        ins = Arbitrage(**ar_kwarg)
        func_ar = ins.arbitrage
        func_list.append(func_ar)
    return func_list

def _make_ob_func_list(li):
    ob_func_list = []
    for dic in li:
        ins = SaveData(**dic)
        fuc_save = ins.save_ob
        ob_func_list.append(fuc_save)
    return ob_func_list

def save_ob(li,t):
    ob_func_list = _make_ob_func_list(li)
    while True :
        _iterrator(ob_func_list)
        time.sleep(t)

def arbitrage(ar_coin_list, t):
    coin_combination_list = _combination(ar_coin_list)
    ar_kwarg_list = _make_ar_kwargs_list('coinone', 'binance', coin_combination_list)
    func_list = _make_ar_func_list(ar_kwarg_list)
    while True :
        _iterrator(func_list)
        time.sleep(t)

if __name__ == "__main__" :
    t1 = threading.Thread(target= save_ob, args=(ob,7))
    t1.start()
    t2 = threading.Thread(target= arbitrage, args=(ar_coin_list,3))
    t2.start()