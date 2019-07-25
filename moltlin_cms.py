import requests
import os
import datetime

class Moltlin_shop():

  def __init__(self):

    self.client_id = os.environ['MOLTIN_CLIENT_ID']
    self.client_secret = os.environ['MOLTIN_CLIENT_SECRET']
    self.token , self.expires = self.get_token_info()
   
    
  def get_token_info(self):
    url= 'https://api.moltin.com/oauth/access_token'
    data = {'client_id':self.client_id,
            'client_secret': self.client_secret,
            'grant_type': 'client_credentials'}
    response = requests.post(url= url, data= data)
    response.raise_for_status()
    response_json = response.json()

    return response_json['access_token'] , response_json['expires']


  def update_not_valid_token(self):
    now_time = datetime.datetime.now()
    token_expires_time = datetime.datetime.fromtimestamp(self.expires-10)
    if now_time > token_expires_time:
      self.token , self.expires = self.get_token_info()


  def get_goods(self):
    self.update_not_valid_token()

    url = 'https://api.moltin.com/v2/products'
    headers = {'Authorization': 'Bearer {}'.format(self.token)}

    goods_response = requests.get(url= url ,headers= headers)
    goods_response.raise_for_status()

    return goods_response.json()['data']

  def get_good_by_id(self, good_id):
    self.update_not_valid_token()

    url = 'https://api.moltin.com/v2/products/{}'.format(good_id)  
    headers = {'Authorization': 'Bearer {}'.format(self.token)}
    
    good_response = requests.get(url= url, headers= headers)
    good_response.raise_for_status()

    return good_response.json()


  def get_image_by_id(self,image_id):
    self.update_not_valid_token()

    url= 'https://api.moltin.com/v2/files/{}'.format(image_id)
    headers = {'Authorization': 'Bearer {}'.format(self.token)}  

    image_response = requests.get(url= url, headers= headers)
    image_response.raise_for_status()

    return image_response.json()


  def add_to_cart(self, quantity, good_id, chat_id):
      self.update_not_valid_token()

      add_cart_url = 'https://api.moltin.com/v2/carts/:{}/items'.format(chat_id)
      add_cart_headers = {'Authorization': 'Bearer {}'.format(self.token),
                            'content_type': 'application/json'}
      add_cart_data = {'data':{'id':good_id,
                                 'type':'cart_item',
                                 'quantity':int(quantity)
                                    
                        }} 

      add_cart_response = requests.post(url= add_cart_url, 
                                        json = add_cart_data,
                                        headers= add_cart_headers)  
      add_cart_response.raise_for_status()

      return add_cart_response.json()                                    
  

  def get_cart(self, cart_id):
    self.update_not_valid_token()
    
    cart_url = 'https://api.moltin.com/v2/carts/:{}/items'.format(cart_id)
    headers = {'Authorization': 'Bearer {}'.format(self.token),
               'content_type': 'application/json'}

    cart_response = requests.get(url= cart_url, headers= headers)
    cart_response.raise_for_status()

    return cart_response.json() 


  def get_good_text_for_sale(self, good_data):
    good_name = good_data['name']
    good_price = good_data['meta']['display_price']['with_tax']['formatted']
    good_description = good_data['description']
    good_stock = good_data['meta']['stock']['level']

    text = '{}\n\n{} per kg\n{} kg on stock\n\n{}'.format(good_name, good_price,good_stock, good_description)

    return text


  def get_good_info_for_cart(self, goods):
    text = ''
    good_info=[]
    
    for good_data in goods:
      good_name = good_data['name'] 
      good_id = good_data['id']
      good_description = good_data['description']
      price = good_data['meta']['display_price']['with_tax']['unit']['formatted'] 
      good_price = '{} per kg'.format(price)
      total_price = good_data['meta']['display_price']['with_tax']['value']['formatted']
      good_items = good_data['quantity']

      good_info.append((good_name , good_id))
      good_text = '{}\n{}\n{}\n{}kg in cart for {}\n\n'.format(good_description, good_name, good_price, good_items, total_price)
      text='{}{}'.format(text, good_text)
    
    return text , good_info


  def get_total_cart_price(self, cart_id):
    self.update_not_valid_token()

    cart_url = 'https://api.moltin.com/v2/carts/:{}'.format(cart_id)
    headers = {'Authorization': 'Bearer {}'.format(self.token),
               'content_type': 'application/json'}

    cart_response = requests.get(url= cart_url, headers= headers)
    cart_response.raise_for_status()
    price = cart_response.json()['data']['meta']['display_price']['with_tax']['formatted']

    return price


  def delete_good_from_cart(self, cart_id, item_id):
    self.update_not_valid_token()

    url = 'https://api.moltin.com/v2/carts/:{}/items/{}'.format(cart_id, item_id)
    headers = {'Authorization': 'Bearer {}'.format(self.token)}

    delete_response = requests.delete(url=url, headers = headers)
    delete_response.raise_for_status()

    return delete_response.json()


  def create_customer(self, first_name, last_name, phone):
    self.updata_not_valid_token()

    headers = {'Authorization': 'Bearer {}'.format(self.token)}
    name = '{} {}'.format(first_name, last_name)
    url = 'https://api.moltin.com/v2/customers'
    castomer_data = {'type':'customer',
                     'name': name ,
                     'email': phone}

    customer_response = requests.post(url= url, 
                                      headers= headers,
                                      data= castomer_data)
    customer_response.raise_for_status()
