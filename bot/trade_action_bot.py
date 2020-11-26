from bot.settings import TYPE_ORDER, TOKEN_TELEGRAM_BOT, STOP_LOSS, TAKE_PROFIT, TARGET_PERCENT_PRICE
from binance.exceptions import BinanceAPIException
from binance.enums import *
from binance.websockets import BinanceSocketManager
from bot.main_func import write_log, convert_currency_symbol
import telebot

from decimal import Decimal
from twisted.internet import reactor
import time


from bot.lib.socket_method import get_user_socket
from bot.lib.files_method import check_open_order, check_signal_orders, save_signal_csv, delete_order_csv
from bot.lib.orders_method import open_order, close_order


# Подключение telegram бота для уведомлений
telegramBot = telebot.TeleBot(TOKEN_TELEGRAM_BOT)


class TradeActionBot:

    def __init__(self, client, symbol, interval):
        self.client = client
        self.symbol = symbol
        self.interval = interval
        self.current_price = Decimal()
        self.signal_bars = []
        self.bm = BinanceSocketManager(self.client, user_timeout=60)

        for info_filter in self.client.get_symbol_info(symbol=symbol)['filters']:
            if info_filter['filterType'] == 'PRICE_FILTER':
                self.price_tick_size = Decimal(info_filter['tickSize'])
            elif info_filter['filterType'] == 'LOT_SIZE':
                self.price_lot_size = Decimal(str(info_filter['stepSize'])).normalize()
            elif info_filter['filterType'] == 'MIN_NOTIONAL':
                self.price_min_order = Decimal(str(info_filter['minNotional']))

        # Получаем информацию по текущей валюте
        if self.symbol == 'ETHBTC':
            self.quote_asset = self.client.get_symbol_info(symbol=self.symbol)['baseAsset']
        else:
            self.quote_asset = self.client.get_symbol_info(symbol=self.symbol)['quoteAsset']

        # Описание для количества свечей
        if self.interval == '5m':
            self.qty_candlestick = "15 minutes ago UTC"
        elif self.interval == '1h':
            self.qty_candlestick = "3 hours ago UTC"

        self.subscription_socket()

    # Подписка на сокет
    def subscription_socket(self):
        self.bm.start_trade_socket(self.symbol, self.__get_current_price)
        self.bm.start_user_socket(self.__get_user_socket)
        self.bm.start()

        while self.current_price == 0:
            print('Ожидание первой цены')
            self.bm.join(timeout=1)

    # Пополение баланса BNB при низком остатке
    def __get_user_socket(self, data):
        get_user_socket(self, data)

    # Получение текущей цены от сокета
    def __get_current_price(self, data):
        self.current_price = Decimal(data['p'])

    # Получение информации по рынку
    def __get_market_info(self):
        arr_klines = []
        info_last_bars = []

        try:
            info_last_bars = self.client.get_historical_klines(self.symbol, self.interval, self.qty_candlestick)
        except BinanceAPIException as err:
            print('Обрыв на свечах')
            write_log(err)

        for index, last_bar in enumerate(info_last_bars):
            open_price = Decimal(last_bar[1])
            close_price = Decimal(last_bar[4])
            high_price = Decimal(last_bar[2])
            low_price = Decimal(last_bar[3])
            arr_klines.append([open_price, high_price, low_price, close_price])

        self.signal_bars.clear()

        if len(arr_klines) > 3:
            arr_klines.pop(0)

        # Собираем информацию по предыдущей свече
        for index, last_bar in enumerate(arr_klines):
            if index == 1:
                self.last_bar_open_price = Decimal(last_bar[0])
                self.last_bar_high_price = Decimal(last_bar[1])
                self.last_bar_low_price = Decimal(last_bar[2])
                self.last_bar_close_price = Decimal(last_bar[3])
            self.signal_bars.append(self.__check_bar(last_bar[0], last_bar[3]))

    # Определение статуса для предыдущего бара
    def __check_bar(self, min_price, max_price):
        if min_price < max_price:
            return 'bulls'
        elif min_price > max_price:
            return 'bears'
        elif min_price == max_price:
            return 'doji'

    # Получаем значения уровней для Take-profit и Stop-loss
    def __get_stop_take_order(self):
        sl_qty_point = self.price_tick_size * STOP_LOSS
        self.sl_buy = Decimal(self.last_bar_low_price - sl_qty_point).quantize(self.price_tick_size)

        tp_qty_point = (self.current_price - self.sl_buy) * TAKE_PROFIT
        self.tp_buy = Decimal(self.current_price + tp_qty_point).quantize(self.price_tick_size)

    # Расчет кол-во лотов для валюты
    def __get_order_lot(self):
        # Конвертация минимальной цены ордера
        min_order = convert_currency_symbol(self.client, self.quote_asset)

        # Кол-во лотов для валюты
        if self.price_lot_size == 1:
            return Decimal(round(Decimal(min_order / self.current_price))).quantize(self.price_lot_size)
        elif self.price_lot_size < 1:
            return Decimal(min_order).quantize(self.price_lot_size)

    # Определение сигнала
    def __check_signal_order(self, type_order, signals):
        if type_order == 'BUY':
            return True if signals[0] == 'bears' and signals[1] == 'bulls' else False
        elif type_order == 'SELL':
            return True if signals[0] == 'bulls' and signals[1] == 'bears' else False

    # Функция вычисления изменения цены в процентах
    def __get_change_price_percent(self, type_bar):
        signal_order = check_signal_orders(self)

        if signal_order is not None:
            max_price_order = Decimal(signal_order[0]['max_price'])
            min_price_order = Decimal(signal_order[0]['min_price'])
        else:
            # Сохранение информации по сигналу в файл
            save_signal_csv({
                'symbol': self.symbol,
                'max_price': self.last_bar_high_price,
                'min_price': self.last_bar_low_price,
                'type_bar': type_bar,
            })
            max_price_order = self.last_bar_high_price
            min_price_order = self.last_bar_low_price

        return {
            'change_price_percent': self.__change_price_percent(max_price_order, self.current_price, type_bar),
            'low_price_bar': min_price_order
        }

    # Вычисление изменения цены в процентах
    def __change_price_percent(self, max_price, current_price, type_bar):
        if type_bar == 'bulls':
            return Decimal((current_price / (max_price / 100)) - 100).quantize(Decimal('0.01'))
        elif type_bar == 'bears':
            return Decimal((max_price / (current_price / 100)) - 100).quantize(Decimal('0.01'))

    # Функция начала торговли
    def start_trade(self):
        is_active_order = False
        is_close_order = False

        while True:
            # Цикл для входа в сделку
            while not is_active_order:
                print('entry-deal')

                # Проверяем есть ли открытые сделки по валюте
                if check_open_order(self) is not None:
                    break

                self.__get_market_info()

                if TYPE_ORDER == 'ALL' or TYPE_ORDER == 'BUY':

                    signal = self.__check_signal_order('BUY', self.signal_bars)

                    if signal:
                        change_percent_price = self.__get_change_price_percent('bulls')
                        if change_percent_price['change_price_percent'] >= TARGET_PERCENT_PRICE:
                            print('Входим в сделку')

                            order_lot = self.__get_order_lot()
                            self.__get_stop_take_order()

                            is_active_order = open_order(self, SIDE_BUY, order_lot)
                            is_close_order = False

                    if check_signal_orders(self) is not None:
                        if self.current_price < Decimal(check_signal_orders(self)[0]['min_price']):
                            print('Снимаем слежение с валюты ' + self.symbol)
                            delete_order_csv(self.symbol, 'signal')

                time.sleep(1)

            # Цикл за слежением активности сделки
            while not is_close_order:
                print('monitoring')

                orders = check_open_order(self)

                if orders is not None:
                    sl_order = Decimal()
                    tp_order = Decimal()
                    type_order = Decimal()

                    for index, order in enumerate(orders):
                        if index == len(orders) - 1:
                            sl_order = Decimal(order['stop-loss'])
                            tp_order = Decimal(order['takeprofit'])
                            type_order = order['type-order']
                            break

                    if type_order == 'BUY':
                        # Закрытие по stop-loss
                        if self.current_price <= sl_order:
                            is_close_order = close_order(self, 'BUY', orders, False)
                            is_active_order = False

                        # Закрытие по take-profit
                        if self.current_price >= tp_order:
                            is_close_order = close_order(self, 'BUY', orders, True)
                            is_active_order = False

                time.sleep(1)

    # Закрытие бота
    def close_bot(self):
            print('Websocket close')
            self.bm.close()
            reactor.stop()