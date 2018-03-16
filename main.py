from Lib.arbitrage import Arbitrage
from Lib.repeat import Repeat, Multi
from Lib.saveData import SaveData


from Lib.decorator import timeit, save_err
from Lib.slack_alert import Slack_Alert

import itertools
import time
import threading
from multiprocessing import Process
import traceback
import datetime

'''
ARGUMENTS
'''

save_ob_dict = {
    'binance' : [
        'BTC/USDT',
        'XRP/BTC',
        'QTUM/BTC',
        'IOTA/BTC',
        'BCH/BTC',
        'ETC/BTC',
        'LTC/BTC',
        'ETH/BTC',
        'XMR/BTC',
        'ZEC/BTC',
        'EOS/BTC'
    ],

    'coinone' : [
        'xrp',
        'qtum',
        'iota',
        'bch',
        'etc',
        'ltc',
        'eth'
    ],

    'bithumb' : [
        'XRP/KRW',
        'QTUM/KRW',
        'BCH/KRW',
        'ETC/KRW',
        'LTC/KRW',
        'ETH/KRW',
        'ZEC/KRW',
        'XMR/KRW',
        'EOS/KRW'
    ]
}

ar_coin_list ={
    'coinone_binance' : ['xrp', 'qtum', 'bch', 'etc', 'ltc', 'eth', 'iota'],
    'coinone_bithumb' : ['xrp', 'qtum', 'bch', 'etc', 'ltc', 'eth'],
    'bithumb_binance' : ['xrp', 'qtum', 'bch', 'etc', 'ltc', 'eth', 'zec', 'xmr', 'eos']
}
    

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

def arbitrage(ex_a, ex_b, ar_coin_list, t):
    coin_combination_list = _combination(ar_coin_list)
    ar_kwarg_list = _make_ar_kwargs_list(ex_a, ex_b, coin_combination_list)
    func_list = _make_ar_func_list(ar_kwarg_list)
    while True :
        _iterrator(func_list)
        time.sleep(t)

if __name__ == "__main__" :
    save_binance = SaveData(exchange = 'binance', symbols = save_ob_dict['binance'])
    save_coinone = SaveData(exchange = 'coinone', symbols = save_ob_dict['coinone'])
    save_bithumb = SaveData(exchange = 'bithumb', symbols = save_ob_dict['bithumb'])
    P1 = Process(target= save_binance.save_obs())
    P2 = Process(target= save_coinone.save_obs())
    P3 = Process(target= save_bithumb.save_obs())
    P1.start()
    P2.start()
    P3.start()    
