import telebot
from telebot import types

TOKEN = "8716951130:AAEiikCG797kjvknQU3YuAFe-cyp5FJ3RFs"
ADMIN_ID = 123456789  # BU YERGA O'ZINGNI IDingni yoz

bot = telebot.TeleBot(TOKEN)

# START
@bot.message_handler(commands=['start'])
def start(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add("💰 UC narxlari", "📦 Buyurtma berish")
    markup.add("📞 Admin", "ℹ️ Biz haqimizda")

    bot.send_message(message.chat.id,
                     "Assalomu alaykum Xurmatli mijoz!\n\n🎮 CoMETA UC shop botga xush kelibsiz!\n\n✅ Bizda halollik 1-o‘rinda\n⚡ Tez va ishonchli xizmat\n\nIltimos Kerakli bo‘limni tanlang 👇",
                     reply_markup=markup)


# UC NARXLARI
@bot.message_handler(func=lambda m: m.text == "💰 UC narxlari")
def narxlar(message):
    text = """
💰 UC narxlari:

30 UC - 7 000 so'm
60 UC - 13 000 so'm
120 UC - 25 000 so'm
180UC - 40 000 so'm
325 UC - 60 000 so'm
660 UC - 115 000 so'm
1800 UC - 300 000 so'm
3850 UC - 620 000 so'm
8100 UC - 1 200 000 so'm

✅ Halollik 1-o‘rinda
"""
    bot.send_message(message.chat.id, text)


# BIZ HAQIMIZDA
@bot.message_handler(func=lambda m: m.text == "ℹ️ Biz haqimizda")
def about(message):
    bot.send_message(message.chat.id,
                     "🎮 Biz UC sotamiz\n\n✅ Halol ishlaymiz\n⚡ Tezkor yetkazib beramiz\n💯 Ishonchli xizmat")


# BUYURTMA BOSHLASH
@bot.message_handler(func=lambda m: m.text == "📦 Buyurtma berish")
def order(message):
    bot.send_message(message.chat.id,
                     "Marhamat Kerakli UC miqdorini yozing (masalan: 60 UC)")


# UC TANLASH
@bot.message_handler(func=lambda m: "UC" in m.text.upper())
def uc_order(message):
    user = message.from_user

    bot.send_message(message.chat.id,
                     "💳 To‘lov uchun karta:\nUZCARD 8600060964894142\n\n📸 To‘lov qilgach chekni yuboring")

    bot.send_message(ADMIN_ID,
                     f"🆕 Yangi buyurtma!\n\n👤 @oybekortiqboyevv\n🆔 {user.id}\n📦 {message.text}")


# CHEKNI QABUL QILISH
@bot.message_handler(content_types=['photo'])
def check_photo(message):
    user = message.from_user

    bot.forward_message(ADMIN_ID, message.chat.id, message.message_id)

    bot.send_message(message.chat.id,
                     "✅ Chekingiz qabul qilindi!\n⏳ Tez orada UC tashlanadi")

    bot.send_message(ADMIN_ID,
                     f"💸 Chek keldi!\n👤 @oybekortiqboyevv\n🆔 {user.id}")


# ADMIN - UC BERILDI
@bot.message_handler(commands=['done'])
def done(message):
    if message.from_user.id == ADMIN_ID:
        try:
            user_id = int(message.text.split()[1])

            bot.send_message(user_id,
                             "🎉 Hisobingizga UC tushdi!\n\nRahmat bizni tanlaganingiz uchun ❤️")

            bot.send_message(message.chat.id, "✅ Mijozga yuborildi")
        except:
            bot.send_message(message.chat.id, "❌ Format xato!\n\n/done user_id")
    else:
        bot.send_message(message.chat.id, "❌ Siz admin emassiz")


# ADMIN
@bot.message_handler(func=lambda m: m.text == "📞 Admin")
def admin(message):
    bot.send_message(message.chat.id, "Admin: @oybekortiqboyevv")


bot.infinity_polling()
