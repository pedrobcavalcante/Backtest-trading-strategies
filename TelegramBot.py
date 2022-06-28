import os
import telebot
import urllib
import json
import requests

API_KEY = os.getenv('QuantAITradeBot')
bot = telebot.TeleBot(API_KEY)

@bot.message_handler(commands=['start', 'help'])
def send_start_message(message):
    bot.reply_to(message, "Olá, eu sou o bot. 'Quem está no espaço?'\n"
                            "Envie o comando /people para saber quais "
                            "pessoas estão no espaço nesse momento.")
    
@bot.message_handler(commands=['people'])
def send_people(message):
    bot.reply_to(message, get_reply_message())
    
def get_reply_message():
    n_people, people = get_people()
    message = "Existem " \
        + str(n_people) + \
        " pessoas no espaço neste momento, são elas: \n\n"
    for person in people:
        message += person["name"] + \
            " na espaçonave " + person["craft"] + "\n\n"
    return message

def get_people():
    req = "http://api.open.notify.org/astros.json"
    response = urllib.request.urlopen(req)
    
    obj = json.loads(response.read())
    
    return obj["number"], obj["people"]

@bot.message_handler(commands=['send_message'])
def send_msg_on_telegram(message):
    request = message.text.split(' ', 1)
    telegram_api_url = f"https://api.telegram.org/bot{API_KEY}/sendMessage?chat_id=@BOTQuantAI&text={request[1]}"
    tel_resp = requests.get(telegram_api_url)
    
    if tel_resp.status_code == 200:
        print("INFO: Notification has been sent on Telegram")
    else:
        print("ERROR: Could not send message")
        

bot.polling()