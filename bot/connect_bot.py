from binance.exceptions import BinanceAPIException, BinanceRequestException, BinanceWithdrawException
from bot.settings import API_KEY, API_SECRET, Client, SYMBOL, INTERVAL
from bot.trade_action_bot import TradeActionBot
from bot.main_func import write_log, init_time, convert_currency_symbol
from requests.exceptions import ReadTimeout

from pprint import pprint
import time


class RunBot:
    def __init__(self):
        try:
            self.client = Client(API_KEY, API_SECRET, {"timeout": 20})
        except ReadTimeout as timeout_err:
            print('Идет переподключение к серверам')
            print(init_time() + ' - ' + str(timeout_err))
            write_log(timeout_err)
        except Exception as err:
            print(init_time() + ' - ' + str(err))
            write_log(err)

    def ping(self):
        try:
            if self.client.ping() == {}:
                print('Соединение с брокером установлено')
            else:
                print('Соединение с брокером не установлено')
        except BinanceRequestException as err:
            print(init_time() + ' - ' + str(err))
            write_log(err.message)
        except BinanceAPIException as err:
            print(init_time() + ' - ' + str(err))
            write_log(err.message)
        except Exception as err:
            print(init_time() + ' - ' + str(err))
            write_log(err)

    def state_server_time(self):
        local_time = int(time.time())
        server_time = int(self.client.get_server_time()['serverTime'])//1000
        shift_seconds = server_time - local_time
        job_time = int(local_time + shift_seconds - 1) * 1000

        print('Локальное время - ' + str(time.ctime(local_time)))
        print('Серверное время - ' + str(time.ctime(server_time)))
        print('Рабочее время - ' + str(time.ctime(job_time)))

    def get_balance(self):
        try:
            pprint(self.client.get_account()['balances'])
        except BinanceRequestException as err:
            print(init_time() + ' - ' + str(err))
            write_log(err.message)
        except BinanceAPIException as err:
            print(init_time() + ' - ' + str(err))
            write_log(err.message)

    def get_commission(self):
        try:
            pprint(self.client.get_trade_fee(symbol=SYMBOL))
            pprint(self.client.get_my_trades(symbol=SYMBOL))
        except BinanceWithdrawException as err:
            print(init_time() + ' - ' + str(err))
            write_log(err.message)

    def get_open_orders(self):
        try:
            pprint(self.client.get_open_orders())
        except BinanceRequestException as err:
            print(init_time() + ' - ' + str(err))
            write_log(err.message)
        except BinanceAPIException as err:
            print(init_time() + ' - ' + str(err))
            write_log(err.message)

    def get_all_orders(self):
        try:
            pprint(self.client.get_all_orders(symbol=SYMBOL))
        except BinanceRequestException as err:
            print(init_time() + ' - ' + str(err))
            write_log(err.message)
        except BinanceAPIException as err:
            print(init_time() + ' - ' + str(err))
            write_log(err.message)

    def get_symbol_info(self):
        try:
            pprint(self.client.get_symbol_info(SYMBOL))
        except Exception as err:
            print(init_time() + ' - ' + str(err))
            write_log(err)

    def get_exchange_info(self):
        try:
            pprint(self.client.get_exchange_info()['rateLimits'])
        except BinanceRequestException as err:
            print(init_time() + ' - ' + str(err))
            write_log(err)
        except BinanceAPIException as err:
            print(init_time() + ' - ' + str(err))
            write_log(err)

    def cancel_order(self, orderId):
        try:
            pprint(self.client.cancel_order(symbol=SYMBOL, orderId=orderId))
        except BinanceRequestException as err:
            print(init_time() + ' - ' + str(err))
            write_log(err.message)
        except BinanceAPIException as err:
            print(init_time() + ' - ' + str(err))
            write_log(err.message)

    def info_order(self, order_id):
        try:
            pprint(self.client.get_order(symbol=SYMBOL, orderId=order_id))
        except BinanceRequestException as err:
            print(init_time() + ' - ' + str(err))
            write_log(err.message)
        except BinanceAPIException as err:
            print(init_time() + ' - ' + str(err))
            write_log(err.message)

    def get_info_system(self):
        try:
            pprint(self.client.get_system_status())
        except BinanceRequestException as err:
            print(init_time() + ' - ' + str(err))
            write_log(err.message)
        except BinanceAPIException as err:
            print(init_time() + ' - ' + str(err))
            write_log(err.message)

    def get_list_symbol(self):
        # Получаем список валют торгуемых на бирже
        try:
            info_symbols = self.client.get_exchange_info()['symbols']
            list_currency = [symbol['symbol'] for symbol in info_symbols if
                             symbol['quoteAsset'] == 'BTC' and symbol['status'] == 'TRADING']
            pprint(list_currency)
        except BinanceRequestException as err:
            print(init_time() + ' - ' + str(err))
            write_log(err)
        except BinanceAPIException as err:
            print(init_time() + ' - ' + str(err))
            write_log(err)

    def convert_currency(self, currency):
        print(convert_currency_symbol(self.client, currency))

    def start_deal(self):
        trade_action_bot = TradeActionBot(self.client, SYMBOL, INTERVAL)

        try:
            trade_action_bot.start_trade()
        except BinanceAPIException as err:
            print(init_time() + ' - ' + str(err.message))
            write_log(err.message)
            if err.message == 'Invalid symbol.':
                print('Такой валюты не существует')
            trade_action_bot.close_bot()
        except Exception as err:
            print(init_time() + ' - ' + str(err))
            write_log(err)
            trade_action_bot.close_bot()
        finally:
            trade_action_bot.close_bot()