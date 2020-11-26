from bot.settings import TYPE_ORDER, CHAT_ID_TELEGRAM_BOT, TOKEN_TELEGRAM_BOT
from bot.main_func import write_log, init_time, convert_currency_rub
from bot.lib.files_method import save_csv, save_archive_order, delete_order_csv

from binance.enums import *
from binance.exceptions import BinanceAPIException

from decimal import Decimal
from pprint import pprint
import time
import telebot


# Открытие сделок
def open_order(self, type_order, lot):
    current_price = Decimal()

    # Подключение telegram бота для уведомлений
    telegramBot = telebot.TeleBot(TOKEN_TELEGRAM_BOT)

    try:
        order = self.client.create_order(
            symbol=self.symbol,
            side=type_order,
            type=ORDER_TYPE_MARKET,
            quantity=lot,
            newOrderRespType=ORDER_RESP_TYPE_FULL)
        pprint(order)
    except BinanceAPIException as err:
        if err.message == 'Invalid quantity.':
            telegramBot.send_message(CHAT_ID_TELEGRAM_BOT, self.symbol + ' - Не хватает лотов для входа')
            time.sleep(180)
            return
        elif err.message == 'Account has insufficient balance for requested action.':
            telegramBot.send_message(CHAT_ID_TELEGRAM_BOT, self.symbol + ' - Не хватает средств на балансе для входа')
            time.sleep(120)
            return
        else:
            print(init_time() + ' - ' + str(err))
            write_log(err)
            return

    status = order['status']

    if status == 'FILLED':
        for index, fill in enumerate(order['fills']):
            if index == 0:
                current_price = fill['price']
            save_csv(order, fill['price'], self.sl_buy, self.tp_buy, fill['qty'], fill['commission'], True)

        delete_order_csv(self.symbol, 'signal')
        telegramBot.send_message(CHAT_ID_TELEGRAM_BOT,
                                 self.symbol + ' - ' + type_order + '\n'
                                 'OrderID: ' + str(order['orderId']) + '\n'
                                 'Цена сделки: ' + str(current_price) + '\n'
                                 'Take-profit: ' + str(self.tp_buy) + '\n'
                                 'Stop-loss: ' + str(self.sl_buy) + '\n'
                                 'Lot: ' + str(lot))

        return True

    elif status == 'EXPIRED':
        for fill in order['fills']:
            save_csv(order, fill['price'], self.sl_buy, self.tp_buy, fill['qty'], fill['commission'], False)
    else:
        message = 'Внимание: Ордер получил статус - ' + str(status)
        print(init_time() + ' - ' + message)
        write_log(message)

    return False


# Закрытие сделок
def close_order(self, type_order, orders, result):
    id_order = ''
    commission_bnb = Decimal()
    exit_price_order = Decimal()
    entry_price = Decimal()
    lot_order = Decimal()
    side_order = SIDE_SELL if type_order == 'BUY' else SIDE_BUY
    result_order = 'Take-profit' if result else 'Stop-loss'

    # Подключение telegram бота для уведомлений
    telegramBot = telebot.TeleBot(TOKEN_TELEGRAM_BOT)

    # Разбор открытых ордеров
    for index, order in enumerate(orders):
        if index == len(orders) - 1:
            id_order = order['order-id']
            entry_price = order['price']

            for order_detail in orders:
                if id_order == order_detail['order-id']:
                    commission_bnb += Decimal(order_detail['commission'])
                    lot_order += Decimal(order_detail['lot'])

    # Алгоритм закрытия сделки
    try:
        send_close_order = self.client.create_order(
            symbol=self.symbol,
            side=side_order,
            type=ORDER_TYPE_MARKET,
            quantity=lot_order,
            newOrderRespType=ORDER_RESP_TYPE_FULL)
        pprint(send_close_order)
    except BinanceAPIException as err:
        print(init_time() + ' - ' + str(err))
        write_log(err)
        return

    for index, fill in enumerate(send_close_order['fills']):
        if index == 0:
            exit_price_order = fill['price']
        commission_bnb += Decimal(fill['commission'])

    if send_close_order['status'] == 'FILLED':
        price_profit = Decimal()

        if TYPE_ORDER == 'BUY':
            price_profit = Decimal(exit_price_order) - Decimal(entry_price)
        elif TYPE_ORDER == 'SELL':
            price_profit = Decimal(entry_price) - Decimal(exit_price_order)

        price_profit_result = convert_currency_rub(self.client, self.quote_asset, price_profit)
        price_profit_fee_result = convert_currency_rub(self.client, 'BNB', commission_bnb)
        main_profit = price_profit_result - price_profit_fee_result

        telegramBot.send_message(CHAT_ID_TELEGRAM_BOT,
                                 self.symbol + '[ ' + type_order + ' ]' + ' - СДЕЛКА ЗАКРЫТА\n'
                                 'OrderID: ' + str(id_order) + '\n'
                                 'Цена закрытия сделки: ' + str(exit_price_order) + '\n'
                                 'Результат: закрыта по ' + result_order + '\n'
                                 'Прибыль: ' + str(main_profit))

        delete_order_csv(id_order, 'order')
        save_archive_order(self.symbol, id_order, type_order, entry_price, exit_price_order, main_profit, lot_order,
                           price_profit_fee_result)
        return True