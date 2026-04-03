import telebot
from telebot import types
import sqlite3, time, re, datetime

TOKEN = "8716951130:AAEiikCG797kjvknQU3YuAFe-cyp5FJ3RFs"
ADMIN_ID = 6394219796

bot = telebot.TeleBot(TOKEN)

conn = sqlite3.connect("bot.db", check_same_thread=False)
cursor = conn.cursor()

# ================= DATABASE =================
cursor.execute("""CREATE TABLE IF NOT EXISTS users(
id INTEGER PRIMARY KEY,
username TEXT,
phone TEXT,
balance INTEGER DEFAULT 0,
banned INTEGER DEFAULT 0,
warn INTEGER DEFAULT 0,
reg_date TEXT)""")

cursor.execute("""CREATE TABLE IF NOT EXISTS orders(
id INTEGER PRIMARY KEY AUTOINCREMENT,
user_id INTEGER,
pubg_id TEXT,
uc INTEGER,
price INTEGER,
status TEXT,
time TEXT)""")

cursor.execute("""CREATE TABLE IF NOT EXISTS logs(
id INTEGER PRIMARY KEY AUTOINCREMENT,
user_id INTEGER,
username TEXT,
action TEXT,
time TEXT)""")

conn.commit()

# ================= PRICES =================
prices = {
    30: 7000,
    60: 12000,
    90: 18000,
    120: 25000,
    180: 37000,
    325: 63000,
    660: 125000,
    985: 170000,
    1920: 305000,
    3850: 600000,
    8100: 1200000
}

# ================= LOG =================
def log(uid, username, action):
    cursor.execute("INSERT INTO logs(user_id, username, action, time) VALUES (?,?,?,?)",
                   (uid, username, action, time.strftime("%H:%M:%S")))
    conn.commit()

# ================= BAN CHECK =================
def banned(uid):
    r = cursor.execute("SELECT banned FROM users WHERE id=?", (uid,)).fetchone()
    return r and r[0] == 1

# ================= MENU =================
def menu():
    kb = types.InlineKeyboardMarkup(row_width=2)
    kb.add(
        types.InlineKeyboardButton("👤 Profil", callback_data="profile"),
        types.InlineKeyboardButton("🛒 Buyurtma", callback_data="order")
    )
    kb.add(
        types.InlineKeyboardButton("📦 Buyurtmalarim", callback_data="my_orders"),
        types.InlineKeyboardButton("💰 Narxlar", callback_data="prices")
    )
    kb.add(
        types.InlineKeyboardButton("💳 To‘lov", callback_data="card"),
        types.InlineKeyboardButton("ℹ️ Biz haqimizda", callback_data="about")
    )
    kb.add(types.InlineKeyboardButton("⚙️ Admin", callback_data="admin"))
    return kb

# ================= START =================
@bot.message_handler(commands=['start'])
def start(m):
    uid = m.from_user.id

    cursor.execute("INSERT OR IGNORE INTO users(id, username, reg_date) VALUES (?,?,?)",
                   (uid, m.from_user.username, str(datetime.date.today())))
    conn.commit()

    bot.send_message(uid, "🏠 Xush kelibsiz", reply_markup=menu())
    log(uid, m.from_user.username, "START")

# ================= CALLBACK =================
@bot.callback_query_handler(func=lambda c: True)
def call(c):
    uid = c.from_user.id
    username = c.from_user.username

    if banned(uid):
        bot.answer_callback_query(c.id, "🚫 Ban olgansiz")
        return

    # ===== PROFILE =====
    if c.data == "profile":
        user = cursor.execute("SELECT balance, phone FROM users WHERE id=?", (uid,)).fetchone()
        bot.edit_message_text(
            f"👤 ID: {uid}\n📱 {user[1]}\n💰 {user[0]} so‘m",
            c.message.chat.id,
            c.message.message_id,
            reply_markup=menu()
        )

    # ===== PRICES =====
    elif c.data == "prices":
        text = "💰 UC Narxlari:\n\n"
        for k,v in prices.items():
            text += f"{k} UC = {v} so‘m\n"
        bot.edit_message_text(text, c.message.chat.id, c.message.message_id, reply_markup=menu())

    # ===== ABOUT =====
    elif c.data == "about":
        bot.edit_message_text("💯 Eng ishonchli CoMETA UC bot\n⚡ Tezkor UC xizmat☺️",
                              c.message.chat.id, c.message.message_id, reply_markup=menu())

    # ===== CARD =====
    elif c.data == "card":
        bot.edit_message_text("TOLOV TURI UZCARD VISA💳 8600060964894142 4278320021238612\n👤 SATTAROV ISMAILJAN",
                              c.message.chat.id, c.message.message_id, reply_markup=menu())

    # ===== ORDER =====
    elif c.data == "order":
        msg = bot.send_message(uid, "PUBG ID kiriting:")
        bot.register_next_step_handler(msg, get_pubg)

    # ===== UC SELECT =====
    elif c.data.startswith("uc_"):
        uc = int(c.data.split("_")[1])
        price = prices[uc]

        cursor.execute("INSERT INTO orders(user_id, uc, price, status, time) VALUES (?,?,?,?,?)",
                       (uid, uc, price, "pending", str(datetime.date.today())))
        conn.commit()

        bot.send_message(uid, f"{uc} UC buyurtma qabul qilindi\n💰 {price}")

    # ===== MY ORDERS =====
    elif c.data == "my_orders":
        data = cursor.execute("SELECT uc, price, status FROM orders WHERE user_id=?", (uid,)).fetchall()
        txt = "\n".join([f"{i[0]} UC | {i[1]} | {i[2]}" for i in data]) or "Yo‘q"
        bot.send_message(uid, txt)

    # ===== ADMIN =====
    elif c.data == "admin":
        if uid != ADMIN_ID:
            return

        kb = types.InlineKeyboardMarkup()
        kb.add(types.InlineKeyboardButton("📊 Stat", callback_data="stat"))
        kb.add(types.InlineKeyboardButton("🚫 Ban", callback_data="ban"))
        kb.add(types.InlineKeyboardButton("✅ Unban", callback_data="unban"))
        kb.add(types.InlineKeyboardButton("📢 Reklama", callback_data="broadcast"))
        kb.add(types.InlineKeyboardButton("💰 Daromad", callback_data="income"))
        kb.add(types.InlineKeyboardButton("📜 Loglar", callback_data="logs"))

        bot.send_message(uid, "Admin panel", reply_markup=kb)

    # ===== ADMIN FUNCS =====
    elif c.data == "stat":
        u = cursor.execute("SELECT COUNT(*) FROM users").fetchone()[0]
        o = cursor.execute("SELECT COUNT(*) FROM orders").fetchone()[0]
        bot.send_message(uid, f"Users: {u}\nOrders: {o}")

    elif c.data == "income":
        s = cursor.execute("SELECT SUM(price) FROM orders").fetchone()[0]
        bot.send_message(uid, f"💰 {s or 0}")

    elif c.data == "logs":
        data = cursor.execute("SELECT user_id, action FROM logs ORDER BY id DESC LIMIT 20").fetchall()
        bot.send_message(uid, "\n".join([str(i) for i in data]))

    elif c.data == "ban":
        msg = bot.send_message(uid, "ID:")
        bot.register_next_step_handler(msg, ban_user)

    elif c.data == "unban":
        msg = bot.send_message(uid, "ID:")
        bot.register_next_step_handler(msg, unban_user)

    elif c.data == "broadcast":
        msg = bot.send_message(uid, "Xabar:")
        bot.register_next_step_handler(msg, send_all)

# ================= FUNCTIONS =================
def get_pubg(m):
    uid = m.from_user.id
    if not re.match(r"\d{8,}", m.text):
        bot.send_message(uid, "❌ ID xato")
        return

    kb = types.InlineKeyboardMarkup()
    for k in prices:
        kb.add(types.InlineKeyboardButton(f"{k} UC", callback_data=f"uc_{k}"))

    bot.send_message(uid, "UC tanlang:", reply_markup=kb)

def ban_user(m):
    cursor.execute("UPDATE users SET banned=1 WHERE id=?", (m.text,))
    conn.commit()
    bot.send_message(m.chat.id, "Ban qilindi")

def unban_user(m):
    cursor.execute("UPDATE users SET banned=0 WHERE id=?", (m.text,))
    conn.commit()
    bot.send_message(m.chat.id, "Unban qilindi")

def send_all(m):
    users = cursor.execute("SELECT id FROM users").fetchall()
    for u in users:
        try:
            bot.send_message(u[0], m.text)
        except:
            pass

# ================= RUN =================
bot.infinity_polling()
