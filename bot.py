import os
import telebot
from flask import Flask
import threading

# TOKEN olish
TOKEN = ("8716951130:AAEiikCG797kjvknQU3YuAFe-cyp5FJ3RFs")

if not TOKEN:
    raise ValueError("❌ TOKEN topilmadi! Render ENV ga qo‘sh!")

bot = telebot.TeleBot(TOKEN)

# /start komandasi
@bot.message_handler(commands=['start'])
def start(message):
    bot.reply_to(message, "Salom 👋 CoMETA siz yaratgan UC Bot ishlayapti!")

# oddiy javob (test uchun)
@bot.message_handler(func=lambda message: True)
def echo(message):
    bot.reply_to(message, message.text)

# Flask (Render o‘chib qolmasligi uchun)
app = Flask(__name__)

@app.route('/')
def home():
    return "Bot ishlayapti!"

def run():
    app.run(host='0.0.0.0', port=10000)

def keep_alive():
    t = threading.Thread(target=run)
    t.start()

# ishga tushirish
if __name__ == "__main__":
    keep_alive()
    print("✅CoMETA UC Botiz ishga tushdi💋...")
    bot.infinity_polling()
