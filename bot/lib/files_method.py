from bot.settings import FILES_BOT

from datetime import datetime
import os
import csv


# Проверка открытых ордеров
def check_open_order(self):
    try:
        with open(FILES_BOT['orders'], 'r') as fin:
            cin = csv.DictReader(fin)
            orders = [row for row in cin if row['symbol'] == self.symbol and row['active-order'] == 'True']
            if len(orders) > 0:
                return orders
            else:
                return None
    except FileNotFoundError as err:
        return None


# Проверка есть ли занесенный сигнал
def check_signal_orders(self):
    try:
        with open(FILES_BOT['signal_orders'], 'r') as fin:
            cin = csv.DictReader(fin)
            signal_order = [row for row in cin if row['symbol'] == self.symbol]
            if len(signal_order) > 0:
                return signal_order
            else:
                return None
    except FileNotFoundError as err:
        return None


# Сохранение сигналов в файл
def save_signal_csv(signal):
    header_signal = [
        'symbol',
        'max_price',
        'min_price',
        'type_bar'
    ]
    data_signal = {
        'symbol': signal['symbol'],
        'max_price': signal['max_price'],
        'min_price': signal['min_price'],
        'type_bar': signal['type_bar'],
    }

    if os.path.exists(FILES_BOT['signal_orders']):
        with open(FILES_BOT['signal_orders'], 'at', newline='', encoding='UTF-8') as fout:
            csv_writer = csv.DictWriter(fout, header_signal)
            csv_writer.writerow(data_signal)
    else:
        with open(FILES_BOT['signal_orders'], 'wt', newline='', encoding='UTF-8') as fout:
            csv_writer = csv.DictWriter(fout, header_signal)
            csv_writer.writeheader()
            csv_writer.writerow(data_signal)


# Сохранение сделок в файл
def save_csv(order, current_price, stoploss, takeprofit, lot, commission, active):
    date = datetime.now().strftime("%Y-%m-%d %H:%M")

    header_order = [
        'date',
        'symbol',
        'order-id',
        'client-order-id',
        'price',
        'stop-loss',
        'takeprofit',
        'status-order',
        'type-order',
        'lot',
        'commission',
        'active-order'
    ]
    data_order = {
        'date': date,
        'symbol': order['symbol'],
        'order-id': order['orderId'],
        'client-order-id': order['clientOrderId'],
        'price': current_price,
        'stop-loss': stoploss,
        'takeprofit': takeprofit,
        'status-order': order['status'],
        'type-order': order['side'],
        'lot': lot,
        'commission': commission,
        'active-order': active
    }

    if os.path.exists(FILES_BOT['orders']):
        with open(FILES_BOT['orders'], 'at', newline='', encoding='UTF-8') as fout:
            csv_writer = csv.DictWriter(fout, header_order)
            csv_writer.writerow(data_order)
    else:
        with open(FILES_BOT['orders'], 'wt', newline='', encoding='UTF-8') as fout:
            csv_writer = csv.DictWriter(fout, header_order)
            csv_writer.writeheader()
            csv_writer.writerow(data_order)


# Сохранение статистики торговли бота
def save_archive_order(symbol, order_id, type_order, entry_price, exit_price, price_profit, lot, commission):
    date = datetime.now().strftime("%Y-%m-%d %H:%M")

    header_order = [
        'date',
        'symbol',
        'order-id',
        'entry price',
        'exit price',
        'type-order',
        'lot',
        'commission',
        'profit'
    ]
    data_order = {
        'date': date,
        'symbol': symbol,
        'order-id': order_id,
        'entry price': entry_price,
        'exit price': exit_price,
        'type-order': type_order,
        'lot': lot,
        'commission': commission,
        'profit': price_profit,
    }

    if os.path.exists(FILES_BOT['archive_orders']):
        with open(FILES_BOT['archive_orders'], 'at', newline='', encoding='UTF-8') as fout:
            csv_writer = csv.DictWriter(fout, header_order)
            csv_writer.writerow(data_order)
    else:
        with open(FILES_BOT['archive_orders'], 'wt', newline='', encoding='UTF-8') as fout:
            csv_writer = csv.DictWriter(fout, header_order)
            csv_writer.writeheader()
            csv_writer.writerow(data_order)


# Удаление сделок из файла
def delete_order_csv(id_mark, type_order):

    file = ''
    update_list = []

    if type_order == 'order':
        file = FILES_BOT['orders']
    elif type_order == 'signal':
        file = FILES_BOT['signal_orders']

    with open(file, 'rt') as fin:
        csv_reader = csv.reader(fin)

        for data in csv_reader:
            if id_mark not in data:
                update_list.append(data)

    with open(file, 'wt', newline='', encoding='UTF-8') as fout:
        csv_writer = csv.writer(fout)

        for data in update_list:
            csv_writer.writerow(data)