import logging
import httplib2
import simplejson as json
from coinone.common import error_code
from operator import itemgetter

import re

create


log_format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
logging.basicConfig(format=log_format, level=logging.DEBUG)
logger = logging.getLogger(__name__)

class Public:
    def fetch_trades(self, currency='btc', period='day'):
        def eval(data):
            """ Convert fetched data to native types """
            return {'price': int(data['price']),
                    'qty': float(data['qty']),
                    'timestamp': int(data['timestamp'])}

        url = 'https://api.coinone.co.kr/trades/?currency={}&period={}&format=json&'.format(currency, period)
        http = httplib2.Http()
        response, content = http.request(url, 'GET')
        res = json.loads(content)

        # raise error if fetching is failed.
        if res['result'] != 'success':
            err = res['errorCode']
            logger.error('Failed to get chart data: %d %s' % (int(err), error_code[err]))
            raise Exception(int(err), error_code[err])

        # just make it sure that result is sorted by timestamp.
        res = sorted(map(eval, res['completeOrders']), key=itemgetter('timestamp'))
        return res


    def get_ticker(currency='btc'):
        url = 'https://api.coinone.co.kr/ticker/?currency={}&format=json'.format(currency)
        http = httplib2.Http()
        response, content = http.request(url, 'GET')
        return json.loads(content)


    def fetch_order_book(currency='btc'):
        url = 'https://api.coinone.co.kr/orderbook/?currency={}&format=json'.format(currency)
        http = httplib2.Http()
        response, content = http.request(url, 'GET')
        res = json.loads(content)

        res['bids'] = res['bid']
        res['asks'] = res['ask']
        del res['bid'], res['ask']

        return res
    
