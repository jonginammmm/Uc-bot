import telebot
from telebot import types
import json
from datetime import datetime

TOKEN = "8716951130:AAEiikCG797kjvknQU3YuAFe-cyp5FJ3RFs"
ADMIN_ID = 6394219796

bot = telebot.TeleBot(TOKEN)

user_data = {}

# ===== SAVE USER =====
def save_user(user_id):
    try:
        with open("users.json", "r") as f:
            users = json.load(f)
    except:
        users = []

    if user_id not in users:
        users.append(user_id)

    with open("users.json", "w") as f:
        json.dump(users, f)


# ===== SAVE ORDER =====
def save_order(user_id, game_id, uc, summa):
    order = {
        "user_id": user_id,
        "game_id": game_id,
        "uc": uc,
        "summa": summa,
        "time": datetime.now().strftime("%Y-%m-%d %H:%M")
    }

    try:
        with open("orders.json", "r") as f:
            data = json.load(f)
    except:
        data = []

    data.append(order)

    with open("orders.json", "w") as f:
        json.dump(data, f, indent=4)


# ===== START =====
@bot.message_handler(commands=['start'])
def start(message):
    save_user(message.from_user.id)

    markup = types.InlineKeyboardMarkup(row_width=2)
    markup.add(
        types.InlineKeyboardButton("🛒 Buyurtma berish", callback_data="buy"),
        types.InlineKeyboardButton("💰 Narxlar", callback_data="price"),
        types.InlineKeyboardButton("📜 Tarix", callback_data="history"),
        types.InlineKeyboardButton("📞 Admin", callback_data="admin")
    )

    bot.send_message(message.chat.id,
                     "🎮 <b>UC SHOP</b>\n\n"
                     "Halollik 1-o‘rinda\n"
                     "⚡ Uc Tezkor yetkazib berish\n\n"
                     "👇 Tanlang",
                     parse_mode="HTML",
                     reply_markup=markup)


# ===== CALLBACK =====
@bot.callback_query_handler(func=lambda call: True)
def callback(call):

    if call.data == "buy":
        user_data[call.from_user.id] = {}
        bot.send_message(call.message.chat.id, "🎮 Pubg ID va Nikingizni kiriting:")
        bot.register_next_step_handler(call.message, get_id)

    elif call.data == "price":
        bot.send_message(call.message.chat.id,
                         "💰 UC Narxlari tayyor 🔥")

    elif call.data == "admin":
        bot.send_message(call.message.chat.id, "Admin: @oybekortiqboyevv")

    elif call.data == "history":
        try:
            with open("orders.json", "r") as f:
                data = json.load(f)
        except:
            data = []

        user_orders = [o for o in data if o["user_id"] == call.from_user.id]

        if not user_orders:
            bot.send_message(call.message.chat.id, "❌ Tarix bo‘sh")
            return

        text = "📜 Tarix:\n\n"

        for o in user_orders[-5:]:
            text += f"{o['game_id']} | {o['uc']} UC | {o['summa']} so‘m\n"

        bot.send_message(call.message.chat.id, text)


# ===== GET ID =====
def get_id(message):
    user_data[message.from_user.id]["game_id"] = message.text

    markup = types.InlineKeyboardMarkup()
    markup.add(
        types.InlineKeyboardButton("60 UC", callback_data="uc_60"),
        types.InlineKeyboardButton("120 UC", callback_data="uc_120"),
        types.InlineKeyboardButton("325 UC", callback_data="uc_325"),
        types.InlineKeyboardButton("660 UC", callback_data="uc_660"),
        types.InlineKeyboardButton("1800 UC", callback_data="uc_1800"),
        types.InlineKeyboardButton("8100 UC", callback_data="uc_8100")
    )

    bot.send_message(message.chat.id, "📦 Marhamat kerakli UCni tanlang:", reply_markup=markup)


# ===== UC TANLASH =====
@bot.callback_query_handler(func=lambda call: call.data.startswith("uc_"))
def uc_select(call):
    uc = call.data.replace("uc_", "")

    user_data[call.from_user.id]["uc"] = uc

    bot.send_message(call.message.chat.id,
                     "💳 To‘lov qiling To'lov turi UZCARD chekni  yuboring\n8600060964894142  SATTAROV ISMAILJAN")


# ===== CHEK =====
@bot.message_handler(content_types=['photo'])
def check(message):

    bot.forward_message(ADMIN_ID, message.chat.id, message.message_id)

bot.send_message(message.chat.id,
                     "📸 Chekingiz qabul qilindi!\n"
                     "💰 Summani yozing:")

    bot.register_next_step_handler(message, get_sum)


# ===== SUMMA =====
def get_sum(message):
    summa = message.text
    user_id = message.from_user.id

    game_id = user_data[user_id]["game_id"]
    uc = user_data[user_id]["uc"]

    save_order(user_id, game_id, uc, summa)

    # ADMIN BUTTON
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("✅ TASDIQLASH", callback_data=f"ok_{user_id}"))

    bot.send_message(ADMIN_ID,
                     f"🆕 BUYURTMA\n\n"
                     f"User: {user_id}\n"
                     f"Game ID: {game_id}\n"
                     f"UC: {uc}\n"
                     f"Summa: {summa}",
                     reply_markup=markup)

    bot.send_message(user_id, "⏳ Tekshirilmoqda...")


# ===== ADMIN TASDIQLASH =====
@bot.callback_query_handler(func=lambda call: call.data.startswith("ok_"))
def approve(call):
    user_id = int(call.data.split("_")[1])

    bot.send_message(user_id,
                     "🎉 UC hisobingizga tushdi!\n💯 Rahmat bizni tanlaganingiz uchun❤️")


bot.infinity_polling()
