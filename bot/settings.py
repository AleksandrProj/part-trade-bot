import os
from bot.core import BinanceUser as Client

BASEDIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FILES_BOT = {
    'signal_orders': os.path.join(BASEDIR, 'files', 'signal_orders.csv'),
    'orders': os.path.join(BASEDIR, 'files', 'orders.csv'),
    'archive_orders': os.path.join(BASEDIR, 'files', 'archive_orders.csv'),
    'bot_log': os.path.join(BASEDIR, 'files', 'bot_log.txt')
}

# Job API data bot
API_KEY = os.environ['API_KEY_BIN']
API_SECRET = os.environ['API_SECRET_BIN']

# Настройки для телеграм бота
TOKEN_TELEGRAM_BOT = os.environ['TOKEN_TB']
TOKEN_TELEGRAM_BOT_ERROR = os.environ['TOKEN_TB_ERROR']
CHAT_ID_TELEGRAM_BOT = os.environ['CHAT_ID_TB']

# Настройки для бота (Делаем настройки для каждой валюты свои и под каждый timeframe)
INTERVAL = Client.KLINE_INTERVAL_1HOUR  # Таймфрейм на котором торгуем
MIN_BALANCE_BNB = 50  # Минимальный баланс BNB при котором надо пополнить BNB
AMOUNT_ORDER_BNB = 0.08  # Сумма на которую надо пополнить BNB

# Настройки для стратегии (Информация по правилам торговли https://www.binance.com/ru/trade-rule)
SYMBOL = 'ALPHABTC'  # Торгуемая валюта
MIN_AMOUNT_ORDER = '500'  # Размер ордера для торговли (в рублях)
TYPE_ORDER = 'BUY'           # Направление для торговли
STOP_LOSS = 10  # Отступ от уровня минимальной цены предыдущего бара (указывается в пунктах)
TAKE_PROFIT = 3  # Насколько Takeprofit больше Stoploss (множитель)
TARGET_PERCENT_PRICE = 5.00
