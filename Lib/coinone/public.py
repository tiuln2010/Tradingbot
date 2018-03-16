
import logging
import httplib2
import simplejson as json
from .common import error_code
from operator import itemgetter

import re

log_format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
logging.basicConfig(format=log_format, level=logging.DEBUG)
logger = logging.getLogger(__name__)

class Coinone_Public:
    def fetch_trades(self, currency='btc', period='day'):
        def eval(data):
            """ Convert fetched data to native types """
            return {'price': int(data['price']),
                    'qty': float(data['qty']),
                    'timestamp': int(data['timestamp'])}

        url = 'https://api.coinone.co.kr/trades/?currency={}&period={}&format=json&'.format(currency, period)
        http = httplib2.Http()
        response, content = http.request(url, 'GET')
        print(response)
        res = json.loads(content)

        # raise error if fetching is failed.
        if res['result'] != 'success':
            err = res['errorCode']
            logger.error('Failed to get chart data: %d %s' % (int(err), error_code[err]))
            raise Exception(int(err), error_code[err])

        # just make it sure that result is sorted by timestamp.
        res = sorted(map(eval, res['completeOrders']), key=itemgetter('timestamp'))
        return res


    def get_ticker(self, currency='btc'):
        url = 'https://api.coinone.co.kr/ticker/?currency={}&format=json'.format(currency)
        http = httplib2.Http()
        response, content = http.request(url, 'GET')
        print(response)
        return json.loads(content)
    
    def _refactoring_order_book(self, order_book):
        def _removeStrings(orderBook, _type):
            re_ob = {_type + 's': []}
            for dic in orderBook[_type] :
                valueList = list(map(lambda _value : float(_value), dic.values()))
                re_ob[_type + 's'].append(valueList)
            return re_ob
        
        res = {}
        timestamp = {'timestamp' : int(order_book['timestamp'])}
        bid_ref = _removeStrings(order_book, 'bid')
        ask_ref = _removeStrings(order_book, 'ask')
        res.update(timestamp)
        res.update(bid_ref)
        res.update(ask_ref)
        
        return res

    def fetch_order_book(self, currency='btc'):
        url = 'https://api.coinone.co.kr/orderbook/?currency={}&format=json'.format(currency)
        http = httplib2.Http()
        response, content = http.request(url, 'GET')
        print(response)
        res = json.loads(content)
        res = self._refactoring_order_book(res)
        return res
  