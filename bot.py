import telebot
from telebot import types
import sqlite3
from datetime import datetime, timedelta

TOKEN = "8716951130:AAEiikCG797kjvknQU3YuAFe-cyp5FJ3RFs"
ADMIN_ID = 6394219796

bot = telebot.TeleBot(TOKEN)

# ===== DB =====
conn = sqlite3.connect("bot.db", check_same_thread=False)
cursor = conn.cursor()

cursor.execute("CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY, balance INTEGER DEFAULT 0, ref INTEGER)")
cursor.execute("""CREATE TABLE IF NOT EXISTS orders (
id INTEGER PRIMARY KEY AUTOINCREMENT,
user_id INTEGER,
game_id TEXT,
uc TEXT,
amount TEXT,
status TEXT,
time TEXT)""")
conn.commit()

# ===== GLOBAL =====
last_action = {}

# ===== USER =====
def add_user(user_id, ref=None):
    cursor.execute("SELECT * FROM users WHERE id=?", (user_id,))
    if cursor.fetchone() is None:
        cursor.execute("INSERT INTO users (id, ref) VALUES (?,?)", (user_id, ref))
        conn.commit()

# ===== START =====
@bot.message_handler(commands=['start'])
def start(message):
    args = message.text.split()
    ref = int(args[1]) if len(args) > 1 else None

    add_user(message.from_user.id, ref)

    bot.send_message(message.chat.id, "♻️ Yangilandi", reply_markup=types.ReplyKeyboardRemove())

    menu = types.InlineKeyboardMarkup(row_width=2)
    menu.add(
        types.InlineKeyboardButton("💰 Narxlar", callback_data="price"),
        types.InlineKeyboardButton("📦 Buyurtma", callback_data="buy"),
        types.InlineKeyboardButton("📜 Tarix", callback_data="history"),
        types.InlineKeyboardButton("💳 Balans", callback_data="balance"),
        types.InlineKeyboardButton("👥 Referal", callback_data="ref"),
        types.InlineKeyboardButton("📊 Statistika", callback_data="stats"),
        types.InlineKeyboardButton("📞 Admin", callback_data="admin")
    )

    bot.send_message(message.chat.id, "🎮CoMETA UC SHOP\n\n👇 Tanlang:", reply_markup=menu)

# ===== CALLBACK =====
@bot.callback_query_handler(func=lambda call: True)
def callback(call):

    user_id = call.from_user.id

    # anti spam
    if user_id in last_action:
        if datetime.now() - last_action[user_id] < timedelta(seconds=2):
            return bot.answer_callback_query(call.id, "⏳ Sekinroq")
    last_action[user_id] = datetime.now()

    # ===== PRICE =====
    if call.data == "price":
        if  call.data == "admin":
    bot.send_message(call.message.chat.id,
    "ℹ️ Biz haqimizda:\n\n"
    "🎮 UC SHOP — ishonchli xizmat\n"
    "💯 Halollik 1-o‘rinda Soxta chek otkazaman deb oylamang Soxta chek bosa Uc yoq\n"
    "⚡ Tez yetkazib berish xizmati UC 2daqiqadan 7daqiqagacha hisobingizda boladi\n"
    "🔥 Eng yaxshi narxlar CoMETA UCda\n\n"
    f"📞 Admin: @oybekortiqboyevv"
)
        "💰 UC NARXLAR:\n\n"
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
        "8100 UC = 1.130.000\n\n"
        "💯 Halollik 1-o‘rinda\n⚡ Tez yetkazib berish"

    # ===== BUY =====
    elif call.data == "buy":
        bot.send_message(call.message.chat.id, "🎮 PUBG NIK VA ID KIRITING ❌xato bolmasin:")
        bot.register_next_step_handler(call.message, get_id)

    # ===== HISTORY =====
    elif call.data == "history":
        cursor.execute("SELECT * FROM orders WHERE user_id=? ORDER BY id DESC LIMIT 5", (user_id,))
        data = cursor.fetchall()

        if not data:
            return bot.send_message(call.message.chat.id, "❌ Tarix bo‘sh")

        text = "📜 Oxirgi buyurtmalar:\n\n"
        for o in data:
            text += f"#{o[0]} | {o[3]} UC | {o[5]}\n"

        bot.send_message(call.message.chat.id, text)

    # ===== BALANCE =====
    elif call.data == "balance":
        cursor.execute("SELECT balance FROM users WHERE id=?", (user_id,))
        bal = cursor.fetchone()[0]
        bot.send_message(call.message.chat.id, f"💳 Balans: {bal} so‘m")

    # ===== REF =====
    elif call.data == "ref":
        bot.send_message(call.message.chat.id,
        f"👥 Referal link:\nhttps://t.me/YOURBOT?start={user_id}")

    # ===== STATS =====
    elif call.data == "stats":
        users = cursor.execute("SELECT COUNT(*) FROM users").fetchone()[0]
        orders = cursor.execute("SELECT COUNT(*) FROM orders").fetchone()[0]

        bot.send_message(call.message.chat.id,
        f"📊 Statistika\n\n👤 Users: {users}\n📦 Orders: {orders}")

    # ===== ADMIN =====
    elif call.data == "admin":
        if user_id != ADMIN_ID:
            return

        menu = types.InlineKeyboardMarkup()
        menu.add(
            types.InlineKeyboardButton("➕ Balans", callback_data="addbal"),
            types.InlineKeyboardButton("📢 Broadcast", callback_data="broadcast")
        )

        bot.send_message(call.message.chat.id, "🧑‍💼 Admin panel", reply_markup=menu)

    # ===== ADD BAL =====
    elif call.data == "addbal":
        bot.send_message(call.message.chat.id, "User ID Nik yubor:")
        bot.register_next_step_handler(call.message, add_balance_user)

    elif call.data == "broadcast":
        bot.send_message(call.message.chat.id, "📢 Xabar yubor:")
        bot.register_next_step_handler(call.message, send_all)

    # ===== UC SELECT =====
    elif call.data.startswith("uc_"):
        uc, game_id = call.data.split("_")[1:]

        bot.send_message(call.message.chat.id,
        "💳 To‘lov qiling Tolov Turi UZCARD VISA karta:\n\n8600060964894142 4278320021238612 SATTAROV ISMAILJAN chiqadi\n\n📸 Chek yuboring")

        bot.register_next_step_handler(call.message, save_order, game_id, uc)

    # ===== CONFIRM =====
    elif call.data.startswith("ok_"):
        order_id = int(call.data.split("_")[1])

        cursor.execute("UPDATE orders SET status='done' WHERE id=?", (order_id,))
        conn.commit()

        cursor.execute("SELECT user_id FROM orders WHERE id=?", (order_id,))
        uid = cursor.fetchone()[0]

        bot.send_message(uid, "🎉 UC tushdi! CoMETA UC tanlaganiz uchin raxmat❤️")

# ===== BUY FLOW =====
def get_id(message):
    game_id = message.text

    menu = types.InlineKeyboardMarkup()
    uc_list = ["30","60","90","120","180","325","660","720","985","1800","1920","8100"]

    for uc in uc_list:
        menu.add(types.InlineKeyboardButton(f"{uc} UC", callback_data=f"uc_{uc}_{game_id}"))

    bot.send_message(message.chat.id, "📦 UC tanlang:", reply_markup=menu)

def save_order(message, game_id, uc):
    user_id = message.from_user.id

    cursor.execute("INSERT INTO orders (user_id, game_id, uc, amount, status, time) VALUES (?,?,?,?,?,?)",
    (user_id, game_id, uc, "?", "pending", str(datetime.now())))
    conn.commit()

    order_id = cursor.lastrowid

    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("✅ TASDIQLASH", callback_data=f"ok_{order_id}"))

    bot.send_message(ADMIN_ID,
    f"🆕 Order #{order_id}\nUser: {user_id}\nID: {game_id}\nUC: {uc}",
    reply_markup=markup)

    bot.send_message(user_id, "⏳ Tekshirilmoqda...")

# ===== ADMIN BALANCE =====
def add_balance_user(message):
    uid = int(message.text)
    bot.send_message(message.chat.id, "Summa yoz:")
    bot.register_next_step_handler(message, add_balance_sum, uid)

def add_balance_sum(message, uid):
    amount = int(message.text)

    cursor.execute("UPDATE users SET balance = balance + ? WHERE id=?", (amount, uid))
    conn.commit()

    bot.send_message(uid, f"💳 Balans +{amount}")

# ===== BROADCAST =====
def send_all(message):
    users = cursor.execute("SELECT id FROM users").fetchall()

    for u in users:
        try:
            bot.send_message(u[0], message.text)
        except:
            pass

    bot.send_message(message.chat.id, "✅ Yuborildi")

# ===== RUN =====
bot.infinity_polling()
