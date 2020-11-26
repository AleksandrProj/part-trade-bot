from datetime import datetime
from bot.settings import FILES_BOT, MIN_AMOUNT_ORDER, TOKEN_TELEGRAM_BOT_ERROR, CHAT_ID_TELEGRAM_BOT, SYMBOL
from decimal import Decimal
from binance.exceptions import BinanceAPIException, BinanceRequestException
import telebot

# Подключение telegram бота для уведомлений
telegramBot = telebot.TeleBot(TOKEN_TELEGRAM_BOT_ERROR)


def init_time():
    return datetime.now().ctime()


def write_log(error):
    telegramBot.send_message(CHAT_ID_TELEGRAM_BOT, SYMBOL + ' - ' + str(error))
    with open(FILES_BOT['bot_log'], 'at') as fout:
        fout.write(init_time() + ' - ' + str(error) + '\n')


def convert_currency_symbol(client, currency):
    price = Decimal()
    price_lot_size = Decimal()
    symbol = ''
    filters = []

    if currency == 'BTC':
        symbol = 'BTCRUB'
    elif currency == 'USDT':
        symbol = 'USDTRUB'
    elif currency == 'ETH':
        symbol = 'ETHRUB'

    try:
        filters = client.get_symbol_info(symbol=symbol)['filters']
        price = Decimal(client.get_symbol_ticker(symbol=symbol)['price'])
    except BinanceRequestException as err:
        print(init_time() + ' - ' + str(err))
        write_log(err)
    except BinanceAPIException as err:
        print(init_time() + ' - ' + str(err))
        write_log(err)

    for info_filter in filters:
        if info_filter['filterType'] == 'LOT_SIZE':
            price_lot_size = Decimal(str(info_filter['stepSize'])).normalize()

    return Decimal(Decimal(MIN_AMOUNT_ORDER) / price).quantize(price_lot_size)


def convert_currency_rub(client, currency, price_test):
    price = Decimal()
    price_lot_size = Decimal()
    symbol = ''
    filters = []

    if currency == 'BTC':
        symbol = 'BTCRUB'
    elif currency == 'USDT':
        symbol = 'USDTRUB'
    elif currency == 'ETH':
        symbol = 'ETHRUB'
    elif currency == 'BNB':
        symbol = 'BNBRUB'

    try:
        filters = client.get_symbol_info(symbol=symbol)['filters']
        price = Decimal(client.get_symbol_ticker(symbol=symbol)['price'])
    except BinanceRequestException as err:
        print(init_time() + ' - ' + str(err))
        write_log(err)
    except BinanceAPIException as err:
        print(init_time() + ' - ' + str(err))
        write_log(err)

    for info_filter in filters:
        if info_filter['filterType'] == 'LOT_SIZE':
            price_lot_size = Decimal(str(info_filter['stepSize'])).normalize()

    return Decimal(Decimal(price_test) * price).quantize(price_lot_size)