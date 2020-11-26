from bot.settings import TOKEN_TELEGRAM_BOT, CHAT_ID_TELEGRAM_BOT, MIN_BALANCE_BNB, AMOUNT_ORDER_BNB
from bot.main_func import write_log, init_time, convert_currency_rub
from binance.enums import *
from binance.exceptions import BinanceAPIException
import telebot

from decimal import Decimal
import time


# Функция пополнения баланса BNB
def __do_top_up_balance_bnb(self, balance_bnb):
    if balance_bnb < MIN_BALANCE_BNB:

        # Подключение telegram бота для уведомлений
        telegram_bot = telebot.TeleBot(TOKEN_TELEGRAM_BOT)

        try:
            order = self.client.create_order(
                symbol='BNBBTC',
                side=SIDE_BUY,
                type=ORDER_TYPE_MARKET,
                quantity=AMOUNT_ORDER_BNB,
                newOrderRespType=ORDER_RESP_TYPE_FULL)
            telegram_bot.send_message(CHAT_ID_TELEGRAM_BOT, 'Происходит процедура пополнения BNB')
        except BinanceAPIException as err:
            print(init_time() + ' - ' + str(err))
            write_log(err)

            if err.message == 'Invalid quantity.':
                telegram_bot.send_message(CHAT_ID_TELEGRAM_BOT, 'BNBBTC - Не хватает лотов для входа')
                time.sleep(180)
                return
            else:
                telegram_bot.send_message(CHAT_ID_TELEGRAM_BOT, 'Что-то пошло не так при пополнении BNB')
                return

        if order['status'] == 'FILLED':
            telegram_bot.send_message(CHAT_ID_TELEGRAM_BOT, 'Баланс BNB пополнен')


# Определение socket метода
def get_user_socket(self, data):
    if data['e'] == 'outboundAccountPosition':
        for balance in data['B']:
            if balance['a'] == 'BNB':
                balance_bnb = convert_currency_rub(self.client, 'BNB', Decimal(balance['f']))
                __do_top_up_balance_bnb(self, balance_bnb)
