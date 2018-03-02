from Lib.arbitrage import Arbitrage
from Lib.repeat import Repeat
from Lib.saveData import SaveData

binance_xrp = SaveData('binance', 'XRP/BTC')
binance_qtum = SaveData('binance', 'QTUM/BTC')
binance_btc = SaveData('binance', 'BTC/USDT')

coinone_xrp = SaveData('coinone', 'xrp')
coinone_qtum = SaveData('coinone', 'qtum')

save_binance_xrp = binance_xrp.save_ob
save_binance_qtum = binance_qtum.save_ob
save_binance_btc = binance_btc.save_ob

save_coinone_xrp = coinone_xrp.save_ob
save_coinone_qtum = coinone_qtum.save_ob

bi_xrp = Repeat(save_binance_xrp, 1)
bi_qtum = Repeat(save_binance_qtum, 1)
bi_btc = Repeat(save_binance_qtum, 1)

co_xrp = Repeat(save_coinone_xrp, 1)
co_qtum = Repeat(save_coinone_qtum, 1)

bi_xrp.start()
bi_qtum.start()
bi_btc.start()

co_xrp.start()
co_qtum.start()


a = Arbitrage('coinone', 'binance', 'xrp', 'qtum')
func = a.arbitrage
re_a = Repeat(func, 1)
re_a.start()