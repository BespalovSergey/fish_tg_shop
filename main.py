import logging
from log_handler import MyLogsHandler
import os
from dotenv import load_dotenv
from telegram_dialog import MyTelegram_bot



def main():
    load_dotenv()

    logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    logger = logging.getLogger('bot_logger')
    logger.setLevel(logging.INFO)
    logger.addHandler(MyLogsHandler(my_chat_id= os.environ['SHOP_TELEGRAMM_CHAT_ID']))
    logger.info('Бот проверки ошибок магазина запущен')

    try:
        telebot = MyTelegram_bot()
        telebot.run_telebot()
    except ConnectionError:
        logger.exception()

if __name__=='__main__':
    main()
