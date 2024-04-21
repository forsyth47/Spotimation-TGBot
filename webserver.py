from flask import Flask
import requests
from os import environ
from threading import Thread

app = Flask('')


@app.route('/')
def home():
  botun = requests.get(f"https://api.telegram.org/bot{environ['Telegram_BotKey']}/getMe").json()['result']['username']
  return f"""<meta http-equiv="refresh" content="2; URL=https://t.me/{botun}" /> If you see this, the bot is working. Start using the Bot by sending /start"""


def run():

  app.run(host='0.0.0.0', port=8080)


def keep_alive():

  t = Thread(target=run)

  t.start()
