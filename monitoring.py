from bot.connect_bot import RunBot

bot = RunBot()
bot.ping()

if __name__ == '__main__':
    message = 'Комманда введена не верно. Список комманд:\n' \
              '\tbalance - проверка баланса аккаунта\n' \
              '\tall-orders - проверка всех ордеров\n' \
              '\topen-orders - проверка открытых ордеров\n' \
              '\tinfo-order - информация по ID ордера\n' \
              '\tdelete-orders - удаление ордера по ID\n' \
              '\ttest-trade - запуск тестовой торговли\n' \
              '\ttrade - запустить торговлю\n' \
              '\tinfo-symbol - проверка информации по символу\n' \
              '\tinfo-rate - проверка информации по лимитам\n' \
              '\tlist-symbol - получить информацию всех торгуемых валют\n' \
              '\ttest-system - проверка сервера\n' \
              '\tconvert - конвертация рублей в другие валюты\n' \
              '\thelp - помощь по командам бота\n' \
              '\texit - выход из программы'
    print(message)

    while True:
        command = input('\nВыберите действие бота: ')

        if command == 'balance':
            bot.get_balance()
        elif command == 'open-orders':
            bot.get_open_orders()
        elif command == 'all-orders':
            bot.get_all_orders()
        elif command == 'info-order':
            id_order = (input('\nВведите номер ордера: '))
            bot.info_order(id_order)
        elif command == 'delete-order':
            id_order = (input('\nВведите номер ордера: '))
            bot.cancel_order(id_order)
        elif command == 'trade':
            bot.start_deal()
        elif command == 'info-symbol':
            bot.get_symbol_info()
        elif command == 'info-rate':
            bot.get_exchange_info()
        elif command == 'commission':
            bot.get_commission()
        elif command == 'list-symbol':
            bot.get_list_symbol()
        elif command == 'test-system':
            bot.get_info_system()
        elif command == 'server':
            bot.state_server_time()
        elif command == 'convert':
            currency = input('Введите валюту для торговли (BTC, USDT, ETH): ')
            bot.convert_currency(currency)
        elif command == 'exit':
            break
        elif command == 'help':
            print(message)
