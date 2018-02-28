
from Lib.coinone.secret import ACCESS_TOKEN, SECRET_KEY
from Lib.coinone.public import Public
from Lib.trade_alert import Trade_alert

from datetime import datetime
from pymongo import MongoClient

import threading
import re

client = MongoClient()
coinonedb = client.coinone

class Recorder:
    def __init__(self, currency):
        self.currency = currency
        self.available = ['btc', 'bch', 'eth', 'etc','xrp', 'qtum', 'ltc', 'iota', 'btg']
        
    def _msg_form(self, method_name, currency, start_time, end_time, res):
        msg = ('{0} - {1} is recorded\n' +
                'start : {2} \n' +
                'end : {3} \n' +

                'detail :'+ str(res)).format(method_name, currency, start_time, end_time)
        return msg
    
    def _get_end_time(self, post):
        timestamp = int(post["timestamp"])
        end = str(datetime.fromtimestamp(timestamp))
        return end

    def record_OB(self):            #Record Order Book
        
        st = str(datetime.now())
        
        if self.currency not in self.available:
            msg = 'record_OB - %s is not availabe' % self.currency
            
        else :
            db_OB_btc = coinonedb.OB_btc
            db_OB_bch = coinonedb.OB_bch
            db_OB_eth = coinonedb.OB_eth
            db_OB_etc = coinonedb.OB_etc
            db_OB_xrp = coinonedb.OB_xrp
            db_OB_qtum = coinonedb.OB_qtum
            db_OB_ltc = coinonedb.OB_ltc
            db_OB_iota = coinonedb.OB_iota
            db_OB_btg = coinonedb.OB_btg
            
            post = Public.fetch_order_book(self.currency)
            end = self._get_end_time(post)
            
            if self.currency == 'btc':
                res = db_OB_btc.insert_one(post)
            elif self.currency == 'bch':
                res = db_OB_bch.insert_one(post)
            elif self.currency == 'eth':
                res = db_OB_eth.insert_one(post)
            elif self.currency == 'etc':
                res = db_OB_etc.insert_one(post)
            elif self.currency == 'xrp':
                res = db_OB_xrp.insert_one(post)
            elif self.currency == 'qtum':
                res = db_OB_qtum.insert_one(post)
            elif self.currency == 'ltc':
                res = db_OB_ltc.insert_one(post)
            elif self.currency == 'iota':
                res = db_OB_iota.insert_one(post)
            elif self.currency == 'btg':
                res = db_OB_btg.insert_one(post)
            
            msg = self._msg_form('record_OB', self.currency, st, end, res)
            
        Trade_alert.send_msg(msg)

    def record_TH(self):        #Record Trade History
        
        st = str(datetime.now())
        
        if self.currency not in self.available:
            msg = 'record_TH - %s is not availabe' % self.currency
           
        else :

            def _get_latest_timestamp(col):
                if col.count() > 0: 
                    num = col.count() - 1
                    doc = col.find()[num]
                    ts = doc['timestamp']
                else : ts = 0 
                return  ts

            def _get_updated_TH(trade_history, col):       #compare timestamp and return updated list
                i = 0
                old_time = _get_latest_timestamp(col)
                max = len(trade_history)
 
                while True:
                    if max > i:
                        i += 1
                        new_time = trade_history[-i].get('timestamp')
                        if new_time == old_time :
                            t = i - 1
                            if t == 0:
                                updated_list = None
                                break
                            updated_list = trade_history[-t:]
                            break
                    else:
                        updated_list = trade_history
                        break
                    
                return updated_list

            def _reform_post(post):      #remove 's in timestamp, price and make a list
                completeOrders = str(post['completeOrders'])
                comp = re.compile(
                    r"'timestamp': '(?P<timestamp>[\d]+)', 'price': '(?P<price>[\d]+)', 'qty': '(?P<qty>[\d]+.[\d]+)'"
                    )
                sub = comp.sub(
                    r"'timestamp': \g<timestamp>, 'price': \g<price>, 'qty': \g<qty>", completeOrders
                    )
                trade_history = eval(sub)
                trade_history.sort(key=lambda x: x['timestamp'])
                return trade_history

            db_TH_btc = coinonedb.TH_btc
            db_TH_bch = coinonedb.TH_bch
            db_TH_eth = coinonedb.TH_eth
            db_TH_etc = coinonedb.TH_etc
            db_TH_xrp = coinonedb.TH_xrp
            db_TH_qtum = coinonedb.TH_qtum
            db_TH_iota = coinonedb.TH_iota
            db_TH_ltc = coinonedb.TH_ltc
            db_TH_btg = coinonedb.TH_btg

            post = Public.fetch_trades(self.currency, period='hour')
            trade_history = _reform_post(post)

            end = self._get_end_time(post)
            try:
                if self.currency == 'btc':
                    updated_list = _get_updated_TH(trade_history, db_TH_btc)
                    res = db_TH_btc.insert(updated_list)
                elif self.currency == 'bch':
                    updated_list = _get_updated_TH(trade_history, db_TH_bch)
                    res = db_TH_bch.insert(updated_list)
                elif self.currency == 'eth':
                    updated_list = _get_updated_TH(trade_history, db_TH_eth)
                    res = db_TH_eth.insert(updated_list)
                elif self.currency == 'etc':
                    updated_list = _get_updated_TH(trade_history, db_TH_etc)
                    res = db_TH_etc.insert(updated_list)
                elif self.currency == 'xrp':
                    updated_list = _get_updated_TH(trade_history, db_TH_xrp)
                    res = db_TH_xrp.insert(updated_list)
                elif self.currency == 'qtum':
                    updated_list = _get_updated_TH(trade_history, db_TH_qtum)
                    res = db_TH_qtum.insert(updated_list)
                elif self.currency == 'iota':
                    updated_list = _get_updated_TH(trade_history, db_TH_iota)
                    res = db_TH_iota.insert(updated_list)
                elif self.currency == 'ltc':
                    updated_list = _get_updated_TH(trade_history, db_TH_ltc)
                    res = db_TH_ltc.insert(updated_list)
                elif self.currency == 'btg':
                    updated_list = _get_updated_TH(trade_history, db_TH_btg)
                    res = db_TH_btg.insert(updated_list)
                res = str(len(res)) + ' trade(s) was(were) recorded.'

            except TypeError:
                res = 'no change'
    
            msg = self._msg_form('record_TH', self.currency, st, end, res)

        Trade_alert.send_msg(msg)

        
class Repeat():
    def __init__(self, fuc, t):
        self.t = t
        self.fuc = fuc
        self.thread = threading.Timer(self.t, self.handling)
        
    def handling(self):
        self.fuc()
        self.thread = threading.Timer(self.t, self.handling)
        self.thread.start()

    def start(self):
        self.thread.start()

    def cancel(self):
        self.thread.cancel()




