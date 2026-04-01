import telebot
from telebot import types
import json
from datetime import datetime

TOKEN = "8716951130:AAEiikCG797kjvknQU3YuAFe-cyp5FJ3RFs"
ADMIN_ID = 6394219796

bot = telebot.TeleBot(TOKEN)

user_data = {}

# ===== USER SAVE =====
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

# ===== GET USERS =====
def get_users():
    try:
        with open("users.json", "r") as f:
            return json.load(f)
    except:
        return []

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
        types.InlineKeyboardButton("💰 Narxlar", callback_data="price"),
        types.InlineKeyboardButton("📦 Buyurtma", callback_data="buy"),
        types.InlineKeyboardButton("📜 Tarix", callback_data="history"),
        types.InlineKeyboardButton("📊 Statistika", callback_data="stats"),
        types.InlineKeyboardButton("📢 Xabar yuborish", callback_data="broadcast"),
        types.InlineKeyboardButton("ℹ️ Biz haqimizda", callback_data="about"),
        types.InlineKeyboardButton("📞 Admin", callback_data="admin")
    )

    bot.send_message(message.chat.id,
                     "🎮 <b>CoMETA UC Botga xushkebsz</b>\n\n"
                     "Qoidalar bilan tanishib chiqing!  1.Soxta chek jonatsayiz Uc🖕 2.Adminga bekordan bekorga yozmang aniq maqsad bilan Admin kechroq javob berishi mumkin biroz kutasiz javob beriladi. Togri bolsayiz bizam togrimiz\n"
                     "⚡ Xalollik 1orinda Tez va ishonchli xizmat\n\n"
                     "👇 Tanlang:",
                     parse_mode="HTML",
                     reply_markup=markup)

# ===== CALLBACK =====
@bot.callback_query_handler(func=lambda call: True)
def callback(call):

    if call.data == "price":
        bot.send_message(call.message.chat.id,
                         "💰 UC Narxlari:\n\n"
                         "30 UC = 7.000\n"
                         "60 UC = 12.000\n"
                         "90 UC = 18.000\n"
                         "120 UC = 25.000\n"
                         "180 UC = 37.000\n"
                         "325 UC = 60.000\n"
                         "660 UC = 115.000\n"
                         "720 UC = 130.000\n"
                         "985 UC = 170.000\n"
                         "1800 UC = 290.000\n"
                         "1920 UC = 305.000\n"
                         "8100 UC = 1.130.000")

    elif call.data == "buy":
        user_data[call.from_user.id] = {}
        bot.send_message(call.message.chat.id, "🎮 ID kiriting:")
        bot.register_next_step_handler(call.message, get_id)

    elif call.data == "about":
        bot.send_message(call.message.chat.id,
                         "ℹ️ Biz haqimizda:\n\n"
                         "💯 Halollik 1-o‘rinda\n"
                         "⚡ Tepada qoidalar bilan tanishdiz deb oyleyman\n"
                         "📞 24/7 xizmat\n"
                         "🔥 Eng arzon Uc narxlar Kattaro Uc paket Kerak bosa adminga✍️")

    elif call.data == "admin":
        bot.send_message(call.message.chat.id, "📞 Admin: @oybekortiqboyevv")

    elif call.data == "stats":
        users = get_users()
        bot.send_message(call.message.chat.id,
                         f"📊 Foydalanuvchilar soni: {len(users)} ta")

    elif call.data == "broadcast":
        if call.from_user.id != ADMIN_ID:
            bot.answer_callback_query(call.id, "❌ Faqat admin")
            return

        bot.send_message(call.message.chat.id, "📢 Xabar yozing:")
        bot.register_next_step_handler(call.message, send_all)

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

    elif call.data.startswith("uc_"):
        uc = call.data.replace("uc_", "")
        user_data[call.from_user.id]["uc"] = uc

        bot.send_message(call.message.chat.id,
                         "💳 To‘lov qiling Tolov UZCARD VISA:\n8600060964894142 4278320021238612 SATTAROV ISMAILJAN Chqadi \n\n📸 Chek yuboring")

    elif call.data.startswith("ok_"):
        user_id = int(call.data.split("_")[1])

        bot.send_message(user_id,
                         "🎉 UC hisobingizga tushdi!\n💯 Rahmat CoMETA UCni tanlaganingiz uchun❤️")

# ===== BROADCAST =====
def send_all(message):
    users = get_users()

    for user in users:
        try:
            bot.send_message(user, message.text)
        except:
            pass

    bot.send_message(message.chat.id, "✅ Yuborildi!")

# ===== GET ID =====
def get_id(message):
    user_data[message.from_user.id]["game_id"] = message.text

    markup = types.InlineKeyboardMarkup()
    markup.add(
        types.InlineKeyboardButton("30 UC", callback_data="uc_30"),
        types.InlineKeyboardButton("60 UC", callback_data="uc_60"),
        types.InlineKeyboardButton("90 UC", callback_data="uc_90"),
        types.InlineKeyboardButton("120 UC", callback_data="uc_120"),
        types.InlineKeyboardButton("180 UC", callback_data="uc_180"),
        types.InlineKeyboardButton("325 UC", callback_data="uc_325"),
        types.InlineKeyboardButton("660 UC", callback_data="uc_660"),
        types.InlineKeyboardButton("1800 UC", callback_data="uc_1800"),
        types.InlineKeyboardButton("8100 UC", callback_data="uc_8100")
    )

    bot.send_message(message.chat.id, "📦 UC tanlang:", reply_markup=markup)

# ===== CHEK =====
@bot.message_handler(content_types=['photo'])
def check(message):

    bot.forward_message(ADMIN_ID, message.chat.id, message.message_id)

    bot.send_message(message.chat.id,
                     "📸 Chek qabul qilindi!\n💰 Summani yozing:")

    bot.register_next_step_handler(message, get_sum)

# ===== SUMMA =====
def get_sum(message):
    summa = message.text
    user_id = message.from_user.id

    game_id = user_data[user_id]["game_id"]
    uc = user_data[user_id]["uc"]

    save_order(user_id, game_id, uc, summa)

    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("✅ TASDIQLASH", callback_data=f"ok_{user_id}"))

    bot.send_message(ADMIN_ID,
                     f"🆕 BUYURTMA\n\nUser: {user_id}\nID: {game_id}\nUC: {uc}\nSumma: {summa}",
                     reply_markup=markup)

    bot.send_message(user_id, "⏳ Tekshirilmoqda...")

# ===== RUN =====
bot.infinity_polling()
