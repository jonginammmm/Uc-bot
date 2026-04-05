import telebot
import os
from flask import Flask
import threading

TOKEN = os.getenv("8716951130:AAEiikCG797kjvknQU3YuAFe-cyp5FJ3RFs")
bot = telebot.TeleBot(TOKEN)

@bot.message_handler(commands=['start'])
def start(message):
    bot.reply_to(message, "Salom 👋 CoMETA Botingiz ishlayapti muammolar❌!")

# KEEP ALIVE
app = Flask('')

@app.route('/')
def home():
    return "Alive"

def run():
    app.run(host='0.0.0.0', port=10000)

def keep_alive():
    t = threading.Thread(target=run)
    t.start()

keep_alive()

bot.infinity_polling()
