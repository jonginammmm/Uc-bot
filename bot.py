import telebot
from telebot import types
import sqlite3
import time

TOKEN = "TOKENINGNI_QO‘Y"
ADMIN_ID = 6394219796

bot = telebot.TeleBot(TOKEN)

# ===== ANTISPAM =====
last_msg_time = {}

def check_spam(uid):
    now = time.time()
    if uid in last_msg_time:
        if now - last_msg_time[uid] < 1.5:
            return True
    last_msg_time[uid] = now
    return False

# ===== DB =====
conn = sqlite3.connect("bot.db", check_same_thread=False)
cursor = conn.cursor()

cursor.execute("""CREATE TABLE IF NOT EXISTS users(
    id INTEGER PRIMARY KEY,
    phone TEXT,
    balance INT DEFAULT 0,
    banned INT DEFAULT 0
)""")

cursor.execute("""CREATE TABLE IF NOT EXISTS orders(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INT,
    uc INT,
    price INT,
    status TEXT
)""")

conn.commit()

# ===== PRICES =====
prices = {
    30:7000, 60:12000, 90:18000,120:25000, 180:37000,
    325:63000, 660:125000,
    985:170000, 1920:305000, 8100:1120000,
}

# ===== MENU =====
def menu():
    kb = types.InlineKeyboardMarkup(row_width=2)
    kb.add(
        types.InlineKeyboardButton("🛒 Buyurtma",callback_data="order"),
        types.InlineKeyboardButton("💰 Narxlar",callback_data="prices")
    )
    return kb

# ===== CHECK USER =====
def is_registered(uid):
    data = cursor.execute("SELECT phone FROM users WHERE id=?",(uid,)).fetchone()
    return data and data[0]

# ===== PUBG ID CHECK =====
def check_pubg_id(user_id):
    return user_id.isdigit() and 6 <= len(user_id) <= 12

# ===== START =====
@bot.message_handler(commands=['start'])
def start(m):
    uid = m.from_user.id

    cursor.execute("INSERT OR IGNORE INTO users(id) VALUES(?)",(uid,))
    conn.commit()

    kb = types.ReplyKeyboardMarkup(resize_keyboard=True)
    kb.add(types.KeyboardButton("📱 Telefon yuborish",request_contact=True))

    bot.send_message(uid,"📱 Telefon yuboring:",reply_markup=kb)

# ===== CONTACT =====
@bot.message_handler(content_types=['contact'])
def contact(m):
    uid = m.from_user.id

    cursor.execute("UPDATE users SET phone=? WHERE id=?",(m.contact.phone_number,uid))
    conn.commit()

    bot.send_message(uid,"✅ Ro‘yxatdan o‘tdingiz",reply_markup=types.ReplyKeyboardRemove())
    bot.send_message(uid,"🏠 MENU",reply_markup=menu())

# ===== CALLBACK =====
@bot.callback_query_handler(func=lambda c: True)
def call(c):
    uid = c.from_user.id

    # 🚫 BAN CHECK
    ban = cursor.execute("SELECT banned FROM users WHERE id=?",(uid,)).fetchone()
    if ban and ban[0] == 1:
        bot.answer_callback_query(c.id,"🚫 Ban olgansiz")
        return

    # 🚫 SPAM CHECK
    if check_spam(uid):
        bot.answer_callback_query(c.id,"⏳ Sekinroq bos 😅")
        return

    # 🚫 REGISTRATION CHECK
    if not is_registered(uid):
        bot.answer_callback_query(c.id,"❗ Avval ro‘yxatdan o‘ting")
        return

    if c.data == "order":
        msg = bot.send_message(uid,"🎮 PUBG ID kiriting:")
        bot.register_next_step_handler(msg,get_pubg_id)

    elif c.data == "prices":
        txt = "\n".join([f"{k} UC = {v} so‘m" for k,v in prices.items()])
        bot.send_message(uid,txt)

    elif c.data.startswith("uc_"):
        uc = int(c.data.split("_")[1])
        price = prices[uc]

        cursor.execute("INSERT INTO orders(user_id,uc,price,status) VALUES(?,?,?,?)",
                       (uid,uc,price,"kutilmoqda"))
        conn.commit()

        bot.send_message(uid,f"✅ Buyurtma qabul qilindi\n{uc} UC")

        kb = types.InlineKeyboardMarkup()
        kb.add(
            types.InlineKeyboardButton("✅ Tasdiqlash",callback_data=f"ok_{uid}_{uc}"),
            types.InlineKeyboardButton("❌ Bekor",callback_data=f"no_{uid}")
        )

        bot.send_message(ADMIN_ID,f"🆕 BUYURTMA\nID:{uid}\nUC:{uc}",reply_markup=kb)

    elif c.data.startswith("ok_"):
        if uid != ADMIN_ID:
            return
        user_id = int(c.data.split("_")[1])
        bot.send_message(user_id,"🎉 UC tushdi!")

    elif c.data.startswith("no_"):
        if uid != ADMIN_ID:
            return
        user_id = int(c.data.split("_")[1])
        bot.send_message(user_id,"❌ Bekor qilindi")

# ===== PUBG ID =====
def get_pubg_id(m):
    uid = m.from_user.id

    if check_spam(uid):
        bot.send_message(uid,"⏳ Sekinroq yoz 😅")
        return

    user_id = m.text.strip()

    if not check_pubg_id(user_id):
        bot.send_message(m.chat.id,"❌ ID xato")
        return

    kb = types.InlineKeyboardMarkup(row_width=2)

    for k,v in prices.items():
        kb.add(types.InlineKeyboardButton(f"{k} UC - {v} so‘m",callback_data=f"uc_{k}"))

    bot.send_message(m.chat.id,"✅ ID topildi\nUC tanlang:",reply_markup=kb)

# ===== RUN =====
bot.infinity_polling()
