import telebot
from telebot import types
import sqlite3
import re

TOKEN = "8716951130:AAHSidAXRXT28CIcjvao5nSUM2hYIpjXakM"
ADMIN_ID = 6394219796

bot = telebot.TeleBot(TOKEN)

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
    game_id TEXT,
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
    kb.add(
        types.InlineKeyboardButton("📦 Buyurtmalarim",callback_data="orders"),
        types.InlineKeyboardButton("💳 To‘lov",callback_data="pay")
    )
    kb.add(
        types.InlineKeyboardButton("👤 Profil",callback_data="profile"),
        types.InlineKeyboardButton("ℹ️ Biz haqimizda",callback_data="about")
    )
    kb.add(types.InlineKeyboardButton("⚙️ Admin",callback_data="admin"))
    return kb

def back():
    kb = types.InlineKeyboardMarkup()
    kb.add(types.InlineKeyboardButton("🔙 Orqaga",callback_data="back"))
    return kb

# ===== START =====
@bot.message_handler(commands=['start'])
def start(m):
    uid = m.from_user.id
    name = m.from_user.first_name

    cursor.execute("INSERT OR IGNORE INTO users(id) VALUES(?)",(uid,))
    conn.commit()

    kb = types.ReplyKeyboardMarkup(resize_keyboard=True)
    kb.add(types.KeyboardButton("📱 Telefon yuborish",request_contact=True))

    bot.send_message(uid,
        f"👋 Salom {name}\n🆔 ID: {uid}\n\nTelefon yuboring:",
        reply_markup=kb)

# ===== CONTACT =====
@bot.message_handler(content_types=['contact'])
def contact(m):
    uid = m.from_user.id
    phone = m.contact.phone_number

    cursor.execute("UPDATE users SET phone=? WHERE id=?",(phone,uid))
    conn.commit()

    bot.send_message(uid,"✅ Ro‘yxatdan o‘tdingiz",reply_markup=types.ReplyKeyboardRemove())
    bot.send_message(uid,"🏠 MENU",reply_markup=menu())

# ===== /ID =====
@bot.message_handler(commands=['id'])
def get_id_cmd(m):
    username = m.from_user.username if m.from_user.username else "Yo‘q"
    bot.send_message(m.chat.id,
        f"🆔 ID: {m.from_user.id}\n👤 @oybekortiqboyevv")

# ===== CALLBACK =====
@bot.callback_query_handler(func=lambda c: True)
def call(c):
    uid = c.from_user.id

    # BAN CHECK
    ban = cursor.execute("SELECT banned FROM users WHERE id=?",(uid,)).fetchone()
    if ban and ban[0] == 1:
        bot.answer_callback_query(c.id,"🚫Siz Ban olgansiz")
        return

    if c.data == "back":
        bot.edit_message_text("🏠 MENU",c.message.chat.id,c.message.message_id,reply_markup=menu())

    elif c.data == "profile":
        data = cursor.execute("SELECT phone,balance FROM users WHERE id=?",(uid,)).fetchone()
        bot.edit_message_text(
            f"👤 Profil\n🆔 {uid}\n📱 {data[0]}\n💰 {data[1]}",
            c.message.chat.id,c.message.message_id,reply_markup=back())

    elif c.data == "about":
        bot.edit_message_text(
            "ℹ️ Biz haqimizda\n💎 Demak bot qoidalari bilan tanishing\n⚡ 1.Adminga bekordan bekorga emas aniq maqsad bilan✍️ 2.Pubg 🆔zi togri kiriting muammo bolmasligi uchin👌 3.Admin kechroq javob berib qolishi mumkin Vohima qivormang☺️. 4.Bizga sizni ishonchiz kerak harom luqma emas❗ 5.Soxta chek otkazaman bilmidi deb oyalmen Soxta chek UC❌ 🫵 Sizni ishonchiz biz uchin 1orinda turadi✅ \n❤️CoMETA UC tanlaganiz uchin Rahmat🫱🏻‍🫲🏼",
            c.message.chat.id,c.message.message_id,reply_markup=back())

    elif c.data == "prices":
        txt = "\n".join([f"{k} UC = {v} so‘m" for k,v in prices.items()])
        bot.edit_message_text(txt,c.message.chat.id,c.message.message_id,reply_markup=back())

    elif c.data == "order":
        msg = bot.send_message(uid,"🎮 PUBG ID kiriting xato bolsa UC xato ketib qoladi qolganiga Bot javob bermaydi ID togri kiriting:",reply_markup=back())
        bot.register_next_step_handler(msg,get_pubg_id)

    elif c.data == "orders":
        data = cursor.execute("SELECT uc,status FROM orders WHERE user_id=?",(uid,)).fetchall()
        txt = "\n".join([f"{i[0]} UC - {i[1]}" for i in data]) or "Yo‘q"
        bot.send_message(uid,txt)

    elif c.data == "pay":
        msg = bot.send_message(uid,
            "💳 KARTA. UZCARD VISA\n8600060964894142 4278320021238612 SATTAROV ISMAILJAN\n\n📸 CHEKNI JO‘NATING❗",
            reply_markup=back())
        bot.register_next_step_handler(msg,get_check)

    # ===== UC SELECT =====
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

    # ===== ADMIN =====
    elif c.data == "admin":
        if uid != ADMIN_ID:
            return

        kb = types.InlineKeyboardMarkup()
        kb.add(types.InlineKeyboardButton("📊 Stat",callback_data="stat"))
        kb.add(types.InlineKeyboardButton("📢 Broadcast",callback_data="bc"))
        kb.add(types.InlineKeyboardButton("🚫 Ban",callback_data="ban"))
        kb.add(types.InlineKeyboardButton("✅ Unban",callback_data="unban"))
        kb.add(types.InlineKeyboardButton("👤 User Info",callback_data="userinfo"))

        bot.send_message(uid,"⚙️ Admin panel",reply_markup=kb)

    elif c.data == "stat":
        users = cursor.execute("SELECT COUNT(*) FROM users").fetchone()[0]
        bot.send_message(uid,f"👥 {users} ta user")

    elif c.data == "bc":
        msg = bot.send_message(uid,"Xabar yuboring Xurmatli admin:")
        bot.register_next_step_handler(msg,broadcast)

    elif c.data == "ban":
        msg = bot.send_message(uid,"User ID:")
        bot.register_next_step_handler(msg,ban_user)

    elif c.data == "unban":
        msg = bot.send_message(uid,"User ID:")
        bot.register_next_step_handler(msg,unban_user)

    elif c.data == "userinfo":
        msg = bot.send_message(uid,"User ID:")
        bot.register_next_step_handler(msg,user_info)

    # ===== ADMIN TASDIQLASH =====
    elif c.data.startswith("ok_"):
        user_id = int(c.data.split("_")[1])
        bot.send_message(user_id,"🎉 UC tushdi! Rahmat CoMETA UCni tanlaganiz uchin ❤️")

    elif c.data.startswith("no_"):
        user_id = int(c.data.split("_")[1])
        bot.send_message(user_id,"❌ Bekor qilindi\nNimadur xato ketdi.Qayta urinib ko‘ring☺️")

# ===== FUNCTIONS =====
def get_pubg_id(m):
    if not m.text or not re.match(r"\d{6,}",m.text):
        bot.send_message(m.chat.id,"❌ ID xato yoki kiritilmadi")
        return

    kb = types.InlineKeyboardMarkup()
    for k in prices:
        kb.add(types.InlineKeyboardButton(f"{k} UC",callback_data=f"uc_{k}"))

    bot.send_message(m.chat.id,"UC tanlang:",reply_markup=kb)

def get_check(m):
    if not m.photo:
        bot.send_message(m.chat.id,"❌ Chek yuborilmadi")
        return

    bot.send_message(m.chat.id,"✅ Chek yuborildi")

    bot.send_photo(ADMIN_ID,m.photo[-1].file_id,
                   caption=f"📸 CHEK\nID:{m.from_user.id}")

def broadcast(m):
    users = cursor.execute("SELECT id FROM users").fetchall()
    for u in users:
        try:
            bot.send_message(u[0],m.text)
        except:
            pass

def ban_user(m):
    cursor.execute("UPDATE users SET banned=1 WHERE id=?",(m.text,))
    conn.commit()
    bot.send_message(m.chat.id,"🚫 Ban qilindi")

def unban_user(m):
    cursor.execute("UPDATE users SET banned=0 WHERE id=?",(m.text,))
    conn.commit()
    bot.send_message(m.chat.id,"✅ Unban")

def user_info(m):
    data = cursor.execute("SELECT phone,balance,banned FROM users WHERE id=?",(m.text,)).fetchone()
    if not data:
        bot.send_message(m.chat.id,"Topilmadi")
        return

    bot.send_message(m.chat.id,
        f"👤 ID:{m.text}\n📱 {data[0]}\n💰 {data[1]}\n🚫 {data[2]}")

# ===== RUN =====
bot.infinity_polling()
