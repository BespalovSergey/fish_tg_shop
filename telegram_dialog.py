from telegram.ext import  Updater, ConversationHandler, CommandHandler,MessageHandler,CallbackQueryHandler,Filters
from telegram import InlineKeyboardButton,InlineKeyboardMarkup
import os
import redis
from moltlin_cms import Moltlin_shop


class MyTelegram_bot():

    def __init__(self):
        redis_host = os.environ['SHOP_REDIS_ADDRESS']
        redis_password = os.environ['SHOP_REDIS_PASSWORD']
        redis_port = os.environ['SHOP_REDIS_PORT']

        self.database = redis.Redis(host= redis_host,password= redis_password, port= redis_port)
        self.moltlin = Moltlin_shop()
        
    
    def get_keyboard(self, state= 'menu', good_info = None):
      
        if state == 'menu':
          goods = self.moltlin.get_goods()
          
          buttons = [[InlineKeyboardButton(good['name'], callback_data = '{}'.format( good['id']))] for good in goods]
          buttons.append([InlineKeyboardButton('Cart', callback_data= 'cart')])

        elif state == 'description':
          weights = ['1кг', '2кг','5кг']

          buttons = [[InlineKeyboardButton(item , callback_data= '{},{}'.format(item[0], good_info)) for item in weights]]
          buttons.append( [InlineKeyboardButton('Назад' ,callback_data= 'back_menu')] )

        elif state == 'cart':
          buttons = [[InlineKeyboardButton('Убрать из корзины {}'.format(good[0]), callback_data=good[1])] for good in good_info]
          buttons.append( [InlineKeyboardButton('Меню' ,callback_data= 'back_menu')] )
          buttons.append([InlineKeyboardButton('Оплатить', callback_data= 'waiting_phone')])

        elif state == 'waiting_phone':
          buttons = [[InlineKeyboardButton('Меню' ,callback_data= 'back_menu')]]  
            
        return InlineKeyboardMarkup(buttons)
     

    def start(self, bot, update):
        text = 'Please shoose.'
        bot.send_message(chat_id= update.message.chat_id,
                         text= text , reply_markup = self.get_keyboard())
        return 'HANDLE_MENU'  


    def handle_menu(self, bot, update):
        query = update.callback_query
        chat_id = query.message.chat_id

        if query.data == 'cart':
          cart = self.moltlin.get_cart(chat_id)
          
          text, cart_good_info  = self.moltlin.get_good_info_for_cart(cart['data'])
          total_cart_price = self.moltlin.get_total_cart_price(query.message.chat_id)
          msg_text = '{}Total: {}'.format(text, total_cart_price)

          bot.send_message(chat_id = chat_id,
                       text= msg_text,
                       reply_markup = self.get_keyboard('cart',cart_good_info)
                       )
          bot.delete_message(chat_id= chat_id,
                          message_id = query.message.message_id,
                          ) 

          return 'HANDLE_CART'

        good_id = query.data
        good_data = self.moltlin.get_good_by_id(good_id)['data']
      
        text = self.moltlin.get_good_text_for_sale(good_data)
         
        image_id = good_data['relationships'] ['main_image']['data']['id']
        image_data = self.moltlin.get_image_by_id(image_id)['data']
        image_link = image_data['link']['href']

        bot.send_photo(chat_id = chat_id,
                       photo = image_link,
                       caption= text,
                       reply_markup= self.get_keyboard(state='description', good_info = good_id))
        bot.delete_message(chat_id= chat_id,
                          message_id = query.message.message_id,
                          )               
        
        return 'HANDLE_DESCRIPTION'  


    def handle_description(self, bot, update):
      query = update.callback_query
      chat_id = query.message.chat_id

      if query.data == 'back_menu':
        text = 'Please shoose'
        bot.send_message(text= text,
                         chat_id= chat_id,
                         reply_markup = self.get_keyboard())
        
        bot.delete_message(chat_id= chat_id,
                           message_id= query.message.message_id )
        
        return 'HANDLE_MENU'   

      else:
        callback_data = query.data.split(',')
        cart_data = self.moltlin.add_to_cart(callback_data[0], callback_data[1], chat_id)
        
        return 'HANDLE_DESCRIPTION'
       
                                                            
    def handle_cart(self, bot, update):
      
      query = update.callback_query
      chat_id = query.message.chat_id
      if query.data == 'back_menu':
        bot.delete_message(chat_id= chat_id,
                           message_id= query.message.message_id)

        return self.start(bot, query)

      elif query.data == 'waiting_phone':
        text = 'Пришлите телефон для связи'
        bot.edit_message_text(chat_id= chat_id,
                              text= text,
                              message_id= query.message.message_id,reply_markup = self.get_keyboard('waiting_phone'))

        return 'WAITING_PHONE_NUMBER'                      
          
      good_id = query.data
      cart_result = self.moltlin.delete_good_from_cart(chat_id, good_id )
      update.callback_query.data = 'cart'
      self.handle_menu(bot,update)
      return 'HANDLE_CART'
    

    def handle_phone_number(self, bot, update):

      if update.callback_query:
        query = update.callback_query
        if query.data == 'back_menu':
          bot.delete_message(chat_id= query.message.chat_id,
                           message_id= query.message.message_id)

          return self.start(bot, query)
          
      else:
        first_name = update.message.chat.first_name
        last_name = update.message.chat.last_name
         
        phone = update.message.text
        message_text = 'Вы отправили этот номер {} \n В ближайшее время Вам позвонит менеджер.'.format(phone)
        bot.send_message(text= message_text,
                         chat_id= update.message.chat_id)

        return self.start(bot, update)                 

   
    def handle_users_reply(self,bot, update):
        if update.message:
            user_reply = update.message.text
            chat_id = update.message.chat_id
            user_redis_key = 'user_state_{}'.format(chat_id)

        elif update.callback_query:
            user_reply = update.callback_query.data
            chat_id = update.callback_query.message.chat_id
            user_redis_key = 'user_state_{}'.format(chat_id)

        else:
            return

        if user_reply == '/start':
            user_state = 'START' 
            
        else:
            user_state = self.database.get(user_redis_key).decode('utf-8')
            
        states_functions = {
          'START': self.start,
          'HANDLE_MENU': self.handle_menu,
          'HANDLE_DESCRIPTION': self.handle_description,
          'HANDLE_CART':self.handle_cart,
          'WAITING_PHONE_NUMBER': self.handle_phone_number
          
        }    
        
        state_handler = states_functions[user_state]
        next_state = state_handler(bot,update)
        self.database.set(user_redis_key,next_state)
           
                   
    def run_telebot(self):
        token = os.environ['SHOP_TELEGRAM_TOKEN']
        updater = Updater(token= token)
        dispatcher = updater.dispatcher

        dispatcher.add_handler(CallbackQueryHandler(self.handle_users_reply))
        dispatcher.add_handler(MessageHandler(Filters.text,self.handle_users_reply))
        dispatcher.add_handler(CommandHandler('start',self.handle_users_reply))
        updater.start_polling()



