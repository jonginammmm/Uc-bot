import telebot
from telebot import types
import sqlite3
import traceback

TOKEN = "8716951130:AAEiikCG797kjvknQU3YuAFe-cyp5FJ3RFs"
ADMIN_ID = 6394219796

bot = telebot.TeleBot(TOKEN)

# ===== DATABASE =====
conn = sqlite3.connect("bot.db", check_same_thread=False)
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS users (
id INTEGER PRIMARY KEY AUTOINCREMENT,
tg_id INTEGER UNIQUE,
phone TEXT,
banned INTEGER DEFAULT 0
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS orders (
id INTEGER PRIMARY KEY AUTOINCREMENT,
user_id INTEGER,
info TEXT,
uc TEXT,
status TEXT
)
""")

conn.commit()

orders_temp = {}

# ===== UC NARXLAR (15 TA) =====
UC_PRICES = [
"30 UC — 7 000",
"60 UC — 12 000",
"90 UC — 18 000",
"120 UC — 24 000",
"180 UC — 37 000",
"325 UC — 60 000",
"360 UC — 72 000",
"660 UC — 115 000",
"720 UC — 130 000",
"985 UC — 170 000",
"1800 UC — 290 000",
"8100 UC — 1 120 000"
]

# ===== START =====
@bot.message_handler(commands=['start'])
def start(m):
    cursor.execute("INSERT OR IGNORE INTO users (tg_id) VALUES (?)",(m.chat.id,))
    conn.commit()

    kb = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    kb.add(types.KeyboardButton("📱 Raqam yuborish", request_contact=True))

    bot.send_message(m.chat.id,"📱 Telefon raqamingizni yuboring",reply_markup=kb)

# ===== CONTACT =====
@bot.message_handler(content_types=['contact'])
def contact(m):
    phone = m.contact.phone_number
    cursor.execute("UPDATE users SET phone=? WHERE tg_id=?",(phone,m.chat.id))
    conn.commit()

    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("💰 UC Narxlar", callback_data="price"),
               types.InlineKeyboardButton("📦 Buyurtma berish", callback_data="buy"))
    markup.add(types.InlineKeyboardButton("💳 To‘lov", callback_data="pay"),
               types.InlineKeyboardButton("📜 Tarix", callback_data="history"))
    markup.add(types.InlineKeyboardButton("ℹ️ Biz haqimizda", callback_data="about"),
               types.InlineKeyboardButton("📞 Admin", callback_data="admin"))

    bot.send_message(m.chat.id,"🎮 CoMETA UC SHOP\n👇 Tanlang:",reply_markup=markup)
    bot.send_message(ADMIN_ID,f"👤 Yangi user: {m.chat.id} | {phone}")

# ===== CALLBACK =====
@bot.callback_query_handler(func=lambda call: True)
def call(c):
    uid = c.message.chat.id

    if c.data == "price":
        text = "💎 UC NARXLAR\n\n━━━━━━━━━━━━━━━\n"
        for i in UC_PRICES:
            text += i + "\n"
        text += "━━━━━━━━━━━━━━━"
        bot.send_message(uid,text)

    elif c.data == "buy":
        msg = bot.send_message(uid,"📦 Pubg ID va Nikizni  kiriting:")
        bot.register_next_step_handler(msg, order)

    elif c.data == "pay":
        bot.send_message(uid,
"""💳 To‘lov turi UZCARD VISA:

8600060964894142
4278320021238612
👤 SATTAROV ISMAILJON

📸 Chek yuboring""")
  elif c.data == "history":
        data = cursor.execute("SELECT info,uc,status FROM orders WHERE user_id=?",(uid,)).fetchall()
        if not data:
            bot.send_message(uid,"📜 Tarix yo‘q")
        else:
            text = ""
            for i in data:
                text += f"{i[0]} | {i[1]} | {i[2]}\n"
            bot.send_message(uid,text)

    elif c.data == "about":
        bot.send_message(uid,
"""ℹ️ Biz haqimizda

🎮 CoMETA UC SHOP
💎 Eng arzon Uc narxlar Eslatib otamiz kattaroq UC Paket kerak bolsa Adminga✍️
⚡ Bot Qoidasi❗ 
1.Adminga zarurat bolsa yozing
2.Sohta check otkazaman deb oylamen Sohta chek bolsa Uc🖕
3.Pubg Nikizi va ID ni togri xatosiz kiriting 
4.Admin tezroq javob berishga harakat qiladi oqilmay qolsa vohima qilish hojati yoq👌
5.CHEKNI korib zarurat bolsa admin sizga yozishi mumkin shuning uchin profilizi ochib qoying.
6.Bizga sizi haqqiz kerak emas Sizni ishonchiz kerak❗
Bot qoidasiga amal qiling ortiqcha harakat qilmang hurmatli mijoz
🛡 Ishonchli xizmat

📞 Admin: @oybekortiqboyevv""")

    elif c.data == "admin":
        msg = bot.send_message(uid,"📩 Xabaringizni yozing:")
        bot.register_next_step_handler(msg, support)

    elif c.data.startswith("uc_"):
        uc = c.data.replace("uc_","")
        info = orders_temp[uid]

        cursor.execute("INSERT INTO orders (user_id,info,uc,status) VALUES (?,?,?,?)",
                       (uid,info,uc,"pending"))
        conn.commit()

        oid = cursor.lastrowid

        kb = types.InlineKeyboardMarkup()
        kb.add(types.InlineKeyboardButton("✅ Tasdiqlash", callback_data=f"ok_{oid}"),
               types.InlineKeyboardButton("❌ Rad etish", callback_data=f"no_{oid}"))

        bot.send_message(ADMIN_ID,
f"""📦 BUYURTMA #{oid}

👤 {uid}
🆔 {info}
💰 {uc}""",reply_markup=kb)

        bot.send_message(uid,"⏳ Buyurtma yuborildi")

    elif c.data.startswith("ok_"):
        oid = int(c.data.split("_")[1])
        cursor.execute("UPDATE orders SET status='done' WHERE id=?",(oid,))
        conn.commit()

        user = cursor.execute("SELECT user_id FROM orders WHERE id=?",(oid,)).fetchone()[0]
        bot.send_message(user,"✅ Buyurtma tasdiqlandi")

    elif c.data.startswith("no_"):
        oid = int(c.data.split("_")[1])
        cursor.execute("UPDATE orders SET status='cancel' WHERE id=?",(oid,))
        conn.commit()

        user = cursor.execute("SELECT user_id FROM orders WHERE id=?",(oid,)).fetchone()[0]
        bot.send_message(user,"❌ Buyurtma rad etildi")

# ===== ORDER =====
def order(m):
    orders_temp[m.chat.id] = m.text

    kb = types.InlineKeyboardMarkup()
    for i in UC_PRICES:
        kb.add(types.InlineKeyboardButton(i, callback_data=f"uc_{i}"))

    bot.send_message(m.chat.id,"💰 UC tanlang:",reply_markup=kb)

# ===== SUPPORT =====
def support(m):
    bot.send_message(ADMIN_ID,f"📩 {m.chat.id}:\n{m.text}")
    bot.send_message(m.chat.id,"✅ Yuborildi")

# ===== CHEK =====
@bot.message_handler(content_types=['photo'])
def check(m):
    bot.forward_message(ADMIN_ID,m.chat.id,m.message_id)
    bot.send_message(m.chat.id,"✅ Chek yuborildi")

# ===== ADMIN =====
@bot.message_handler(commands=['admin'])
def panel(m):
    if m.chat.id != ADMIN_ID:
        return
    bot.send_message(m.chat.id,
"""👑 ADMIN PANEL

/users
/phones
/find
/findphone
/send
/ban
/unban""")

@bot.message_handler(commands=['users'])
def users(m):
    if m.chat.id == ADMIN_ID:
        c = cursor.execute("SELECT COUNT(*) FROM users").fetchone()[0]
        bot.send_message(m.chat.id,f"👥 {c} ta user")

@bot.message_handler(commands=['phones'])
def phones(m):
    if m.chat.id == ADMIN_ID:
        data = cursor.execute("SELECT tg_id,phone FROM users").fetchall()
        text = ""
        for i in data:
            text += f"{i[0]} → {i[1]}\n"
        bot.send_message(m.chat.id,text)

@bot.message_handler(commands=['find'])
def find(m):
    if m.chat.id == ADMIN_ID:
        uid = int(m.text.split()[1])
        data = cursor.execute("SELECT * FROM orders WHERE user_id=?",(uid,)).fetchall()
        bot.send_message(m.chat.id,str(data))

@bot.message_handler(commands=['findphone'])
def findphone(m):
    if m.chat.id == ADMIN_ID:
        phone = m.text.split()[1]
        res = cursor.execute("SELECT tg_id FROM users WHERE phone=?",(phone,)).fetchone()
        bot.send_message(m.chat.id,str(res))

@bot.message_handler(commands=['send'])
def send(m):
    if m.chat.id == ADMIN_ID:
        msg = bot.send_message(m.chat.id,"✉️ Xabar:")
        bot.register_next_step_handler(msg,broadcast)

def broadcast(m):
    data = cursor.execute("SELECT tg_id FROM users").fetchall()
    for i in data:
        try:
            bot.send_message(i[0],m.text)
        except:
            pass

@bot.message_handler(commands=['ban'])
def ban(m):
    if m.chat.id == ADMIN_ID:
        uid = int(m.text.split()[1])
        cursor.execute("UPDATE users SET banned=1 WHERE tg_id=?",(uid,))
        conn.commit()

@bot.message_handler(commands=['unban'])
def unban(m):
    if m.chat.id == ADMIN_ID:
        uid = int(m.text.split()[1])
        cursor.execute("UPDATE users SET banned=0 WHERE tg_id=?",(uid,))
        conn.commit()

# ===== SMART =====
@bot.message_handler(func=lambda m: True)
def smart(m):
    t = m.text.lower()

    if "salom" in t:
        bot.send_message(m.chat.id,"Salom 👋")
    elif "narx" in t or "uc" in t:
        bot.send_message(m.chat.id,"\n".join(UC_PRICES))
    elif "tolov" in t:
        bot.send_message(m.chat.id,"💳 To‘lov tugmasini bosing")
    else:
        pass

# ===== RUN =====
while True:
    try:
        bot.polling(none_stop=True)
    except Exception as e:
        bot.send_message(ADMIN_ID,str(e))
