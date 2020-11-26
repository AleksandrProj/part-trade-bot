from bot.connect_bot import RunBot

bot = RunBot()
bot.ping()

if __name__ == '__main__':
    try:
        bot.start_deal()
    except KeyboardInterrupt:
        print('Выход из программы')