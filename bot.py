import telebot
import os

TOKEN = os.getenv("8716951130:AAEiikCG797kjvknQU3YuAFe-cyp5FJ3RFs")

bot = telebot.TeleBot(TOKEN)

@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(message.chat.id, "Bot ishlayapti 🚀")

bot.infinity_polling()
