import telebot
from telebot import types
import sqlite3
import time

TOKEN = "8716951130:AAEiikCG797kjvknQU3YuAFe-cyp5FJ3RFs"
ADMIN_ID = 6394219796

bot = telebot.TeleBot(TOKEN)

# ===== DB =====
conn = sqlite3.connect("bot.db", check_same_thread=False)
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS users(
id INTEGER PRIMARY KEY AUTOINCREMENT,
tg_id INTEGER UNIQUE,
phone TEXT,
banned INTEGER DEFAULT 0
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS orders(
id INTEGER PRIMARY KEY AUTOINCREMENT,
tg_id INTEGER,
game_id TEXT,
uc TEXT,
status TEXT
)
""")

conn.commit()

user_uc = {}
last_msg = {}

# ===== SPAM =====
def spam(uid):
    now = time.time()
    if uid in last_msg and now - last_msg[uid] < 1:
        return True
    last_msg[uid] = now
    return False

# ===== MENU =====
def menu(uid):
    kb = types.InlineKeyboardMarkup()
    kb.add(
        types.InlineKeyboardButton("💰 Narxlar", callback_data="price"),
        types.InlineKeyboardButton("📦 Buyurtma", callback_data="buy")
    )
    kb.add(
        types.InlineKeyboardButton("📜 Tarix", callback_data="history"),
        types.InlineKeyboardButton("💳 To‘lov", callback_data="pay")
    )
    kb.add(
        types.InlineKeyboardButton("ℹ️ Biz haqimizda", callback_data="about")
    )

    if uid == ADMIN_ID:
        kb.add(types.InlineKeyboardButton("⚙️ Admin panel", callback_data="admin"))

    bot.send_message(uid, "👇 Menu:", reply_markup=kb)

# ===== START =====
@bot.message_handler(commands=['start'])
def start(m):
    cursor.execute("INSERT OR IGNORE INTO users (tg_id) VALUES(?)",(m.chat.id,))
    conn.commit()

    kb = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    kb.add(types.KeyboardButton("📱 Telefon yuborish", request_contact=True))

    bot.send_message(m.chat.id, "📱 Telefon yuboring:", reply_markup=kb)

# ===== CONTACT =====
@bot.message_handler(content_types=['contact'])
def contact(m):
    phone = m.contact.phone_number
    uid = m.chat.id

    cursor.execute("UPDATE users SET phone=? WHERE tg_id=?", (phone, uid))
    conn.commit()

    bot.send_message(uid, "✅ Saqlandi", reply_markup=types.ReplyKeyboardRemove())
    menu(uid)

# ===== CALLBACK =====
@bot.callback_query_handler(func=lambda c: True)
def call(c):
    uid = c.from_user.id

    if spam(uid): return

    banned = cursor.execute("SELECT banned FROM users WHERE tg_id=?", (uid,)).fetchone()
    if banned and banned[0] == 1:
        bot.answer_callback_query(c.id, "🚫 Ban!")
        return

    # BACK
    if c.data == "back":
        bot.edit_message_text("👇 Menu:", uid, c.message.message_id, reply_markup=menu(uid))

    # PRICE
    elif c.data == "price":
        kb = types.InlineKeyboardMarkup()
        kb.add(types.InlineKeyboardButton("🔙 Orqaga", callback_data="back"))

        bot.edit_message_text(
"""💎 UC NARXLAR

30 UC - 7.000
60 UC - 12.000
90 UC - 18.000
120 UC - 25.000
180 UC - 37.000
325 UC - 60.000
660 UC - 115.000
720 UC - 130.000
985 UC - 170.000
1800 UC - 290.000
3850 UC - 630.000
8100 UC - 1.120.000
""",
            uid,
            c.message.message_id,
            reply_markup=kb
        )

    # BUY
    elif c.data == "buy":
        kb = types.InlineKeyboardMarkup(row_width=2)
        for uc in ["30","60","90","120","180","325","660","720","985","1800","3850","8100"]:
            kb.add(types.InlineKeyboardButton(f"{uc} UC", callback_data=f"uc_{uc}"))

        kb.add(types.InlineKeyboardButton("🔙 Orqaga", callback_data="back"))

        bot.edit_message_text("💰 UC tanlang:", uid, c.message.message_id, reply_markup=kb)

    # UC TANLANDI
    elif c.data.startswith("uc_"):
        uc = c.data.split("_")[1]
        user_uc[uid] = uc
        msg = bot.send_message(uid, "🆔 PUBG ID va Nik yubor:")
        bot.register_next_step_handler(msg, get_id)

    # HISTORY
    elif c.data == "history":
        kb = types.InlineKeyboardMarkup()
        kb.add(types.InlineKeyboardButton("🔙 Orqaga", callback_data="back"))

        data = cursor.execute("SELECT id, game_id, uc, status FROM orders WHERE tg_id=?", (uid,)).fetchall()
        txt = "\n".join([f"#{i[0]} | {i[1]} | {i[2]} UC | {i[3]}" for i in data]) or "Bo‘sh"

        bot.edit_message_text(txt, uid, c.message.message_id, reply_markup=kb)

    # PAY
    elif c.data == "pay":
        kb = types.InlineKeyboardMarkup()
        kb.add(types.InlineKeyboardButton("🔙 Orqaga", callback_data="back"))

        bot.edit_message_text(
"""💳 TO‘LOV turi UZCARD VISA

8600060964894142
4278320021238612
SATTAROV ISMAILJON
Chek yuboring Soxta Bosa UC yoq
""",
            uid,
            c.message.message_id,
            reply_markup=kb
        )

    # ABOUT
    elif c.data == "about":
        kb = types.InlineKeyboardMarkup()
        kb.add(types.InlineKeyboardButton("🔙 Orqaga", callback_data="back"))

        bot.edit_message_text(
            "ℹ️ Biz haqimizda\n\n"            
"🎮 CoMETA UC SHOP"l\n"
"💎 Eng arzon Uc narxlar Eslatib otamiz kattaroq UC Paket kerak bolsa Adminga✍️\n"
"⚡ Bot Qoidasi❗\n" 
"1.Adminga zarurat bolsa yozing\n"
"2.Sohta check otkazaman deb oylamen Sohta chek bolsa Uc🖕\n"
"3.Pubg Nikizi va ID ni togri xatosiz kiriting\n"
"4.Admin tezroq javob berishga harakat qiladi oqilmay qolsa vohima qilish hojati yoq👌\n"
"5.CHEKNI korib zarurat bolsa admin sizga yozishi mumkin shuning uchin profilizi ochib qoying.\n"
"6.Bizga sizi haqqiz kerak emas Sizni ishonchiz kerak❗\n"
"Bot qoidasiga amal qiling ortiqcha harakat qilmang hurmatli mijoz?\n"
"🛡 Ishonchli xizmat\n\n"
"📞 Admin: @oybekortiqboyevv\n",
            uid,
            c.message.message_id,
            reply_markup=kb
        )

    # ===== ADMIN =====
    elif c.data == "admin":
        if uid != ADMIN_ID: return

        kb = types.InlineKeyboardMarkup()
        kb.add(
            types.InlineKeyboardButton("👥 Userlar", callback_data="users"),
            types.InlineKeyboardButton("📦 Orders", callback_data="orders")
        )
        kb.add(
            types.InlineKeyboardButton("🔍 Qidirish", callback_data="find"),
            types.InlineKeyboardButton("📢 Broadcast", callback_data="broadcast")
        )
        kb.add(
            types.InlineKeyboardButton("📩 Userga yozish", callback_data="sendone"),
            types.InlineKeyboardButton("📊 Stat", callback_data="stat")
        )
        kb.add(
            types.InlineKeyboardButton("🚫 Ban", callback_data="ban"),
            types.InlineKeyboardButton("✅ Unban", callback_data="unban")
        )
        kb.add(types.InlineKeyboardButton("🔙 Orqaga", callback_data="back"))

        bot.edit_message_text("⚙️ ADMIN PANEL", uid, c.message.message_id, reply_markup=kb)

    elif c.data == "users":
        data = cursor.execute("SELECT * FROM users").fetchall()
        txt = "\n\n".join([f"ID:{i[0]}\nTG:{i[1]}\nTEL:{i[2]}" for i in data]) or "Bo‘sh"
        bot.send_message(uid, txt)

    elif c.data == "orders":
        data = cursor.execute("SELECT * FROM orders").fetchall()
        txt = "\n".join([str(i) for i in data]) or "Bo‘sh"
        bot.send_message(uid, txt)

    elif c.data == "find":
        msg = bot.send_message(uid, "ID / Telefon / TG yoz:")
        bot.register_next_step_handler(msg, find_user)

    elif c.data == "broadcast":
        msg = bot.send_message(uid, "Xabar yoz:")
        bot.register_next_step_handler(msg, send_all)

    elif c.data == "sendone":
        msg = bot.send_message(uid, "User TG_ID yoz:")
        bot.register_next_step_handler(msg, send_one)

    elif c.data == "stat":
        count = cursor.execute("SELECT COUNT(*) FROM users").fetchone()[0]
        bot.send_message(uid, f"👥 Userlar: {count}")

    elif c.data == "ban":
        msg = bot.send_message(uid, "User TG_ID:")
        bot.register_next_step_handler(msg, do_ban)

    elif c.data == "unban":
        msg = bot.send_message(uid, "User TG_ID:")
        bot.register_next_step_handler(msg, do_unban)

# ===== FUNKSIYALAR =====
def find_user(m):
    txt = m.text
    data = cursor.execute("SELECT * FROM users WHERE tg_id=? OR phone=? OR id=?", (txt,txt,txt)).fetchall()
    bot.send_message(m.chat.id, str(data) or "Topilmadi")

def send_all(m):
    users = cursor.execute("SELECT tg_id FROM users").fetchall()
    for u in users:
        try:
            bot.send_message(u[0], m.text)
        except:
            pass
    bot.send_message(m.chat.id, "Yuborildi")

def send_one(m):
    uid = m.text
    msg = bot.send_message(m.chat.id, "Xabar yoz:")
    bot.register_next_step_handler(msg, lambda x: bot.send_message(uid, x.text))

def do_ban(m):
    cursor.execute("UPDATE users SET banned=1 WHERE tg_id=?", (m.text,))
    conn.commit()
    bot.send_message(m.chat.id, "Ban qilindi")

def do_unban(m):
    cursor.execute("UPDATE users SET banned=0 WHERE tg_id=?", (m.text,))
    conn.commit()
    bot.send_message(m.chat.id, "Unban")

def get_id(m):
    uid = m.chat.id
    uc = user_uc.get(uid, "?")

    cursor.execute("INSERT INTO orders(tg_id,game_id,uc,status) VALUES(?,?,?,?)",
                   (uid,m.text,uc,"pending"))
    conn.commit()

    bot.send_message(uid, "✅ Buyurtma qabul qilindi")

# ===== RUN =====
print("Bot ishladi")
bot.polling(none_stop=True)
