from Lib.arbitrage import Arbitrage
from Lib.repeat import Repeat, Multi
from Lib.saveData import SaveData

from Lib.slack_alert import Slack_Alert

import itertools
import time
import threading

ob =[
    {'exchange' : 'binance', 'symbol' : 'BTC/USDT'},

    {'exchange' : 'binance', 'symbol' : 'XRP/BTC'},
    {'exchange' : 'binance', 'symbol' : 'QTUM/BTC'},
    {'exchange' : 'binance', 'symbol' : 'IOTA/BTC'},
    {'exchange' : 'binance', 'symbol' : 'BCH/BTC'},
    {'exchange' : 'binance', 'symbol' : 'ETC/BTC'},
    {'exchange' : 'binance', 'symbol' : 'LTC/BTC'},        
    {'exchange' : 'binance', 'symbol' : 'ETH/BTC'},        

    {'exchange' : 'coinone', 'symbol' : 'xrp'},
    {'exchange' : 'coinone', 'symbol' : 'qtum'},
    {'exchange' : 'coinone', 'symbol' : 'iota'},
    {'exchange' : 'coinone', 'symbol' : 'bch'},
    {'exchange' : 'coinone', 'symbol' : 'etc'},
    {'exchange' : 'coinone', 'symbol' : 'ltc'},
    {'exchange' : 'coinone', 'symbol' : 'eth'}
]   


ar_coin_list =[
    'xrp', 'qtum', 'iota', 'bch', 'etc', 'ltc', 'eth'
]

def _make_ob_func_list(li):
    ob_func_list = []
    for dic in li:
        ins = SaveData(**dic)
        fuc_save = ins.save_ob
        ob_func_list.append(fuc_save)
    return ob_func_list
    

def _save_ob(li, t):
    ob_func_list = _make_ob_func_list(li)
    while True :
        st = time.process_time()
        multi = Multi(ob_func_list)
        processes = multi.run_process()
        multi.wait_end(processes)
        msg = time.process_time() - st
        m = Slack_Alert()
        m.send_msg("saving time :" + str(msg))
        time.sleep(t)
        print("ended")

def _iterArCoin(li):
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

def _arbitrage(ar_coin_list, t):
    coin_combination_list = _iterArCoin(ar_coin_list)
    ar_kwarg_list = _make_ar_kwargs_list('coinone', 'binance', coin_combination_list)
    func_list = _make_ar_func_list(ar_kwarg_list)
    while True :
        st = time.process_time()
        multi = Multi(func_list)
        processes = multi.run_process()
        multi.wait_end(processes)
        msg = time.process_time() - st
        m = Slack_Alert()
        m.send_msg("processing time :" + str(msg))
        time.sleep(t)
        print("ended")
    
if __name__ == "__main__" :
    t1 = threading.Thread(target= _save_ob, args=(ob,7))
    t1.start()
    t2 = threading.Thread(target= _arbitrage, args=(ar_coin_list,3))
    t2.start()
    print("ended")
