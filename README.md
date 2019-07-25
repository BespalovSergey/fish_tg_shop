# fish_tg_shop
Данный скрипт работает как чат бот магазина расположенного на сайте moltin.com.

Чтобы запустить скрипт необходимо :

1 Установить необходимые зависимости командой

pip install -r requirements.txt

2 в корне создать файл ".env " с следующим содержанием

    SHOP_BOT_ERROR_TOKEN = 'Телеграм токен бота на который приходят ошибки'
    SHOP_TELEGRAM_TOKEN = 'Телеграм токен бота магазина'
    SHOP_TELEGRAMM_CHAT_ID = ' Ваш id чата' (его можно узнать обратившись с командой /start к телеграм боту с именем    userinfobot)
    SHOP_REDIS_PASSWORD = 'Пароль к базе данных на Redislab'
    SHOP_REDIS_ADDRESS = 'Адресс базы данных на Redislab'
    SHOP_REDIS_PORT = 'Порт базы данных на Redislab'
    MOLTIN_CLIENT_ID = 'ID клиента на moltin.com' 
    MOLTIN_CLIENT_SECRET = 'Secret ID клиента на moltin.com'
    
3 Запустить файл main.py набрав в консоли команду

python main.py
