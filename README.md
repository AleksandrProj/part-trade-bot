## На сервере устанавливаем SUPERVISOR
apt-get install supervisor  
service supervisor restart

## Добавление бота на сервер
1. В папке /home создаем новую папку «bot_PAIRS»
2. В эту папку кладем файлы бота
3. /home/.env/bin/list-bot - создаем скрипт-файл с именем PAIRS.sh (переименовать в название торгуемой валюты) и даем права на исполнение «chmod +x name_path»
4. /etc/supervisor/conf.d/start_bots.conf - добавляем новый процесс под бота
5. Включаем бота в supervisorctl
    * reread
    * update
    
## Запуск остановленного бота на сервере
supervisorctl -> start "name_bot"

## Остановка ботов на сервере
supervisorctl -> stop all