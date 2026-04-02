import telebot
from telebot import types
import sqlite3
import time

TOKEN = "8716951130:AAEiikCG797kjvknQU3YuAFe-cyp5FJ3RFs"
ADMIN_ID = 6394219796

bot = telebot.TeleBot(TOKEN)

# ===== DATABASE =====
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
user_id INTEGER,
game_id TEXT,
uc TEXT,
status TEXT
)
""")

conn.commit()

user_uc = {}
last_msg_time = {}

# ===== SPAM PROTECTION =====
def is_spam(user_id):
    now = time.time()
    if user_id in last_msg_time:
        if now - last_msg_time[user_id] < 2:  # 2 sekund
            return True
    last_msg_time[user_id] = now
    return False

# ===== MENU =====
def menu(user_id):
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

    if user_id == ADMIN_ID:
        kb.add(types.InlineKeyboardButton("⚙️ Admin panel", callback_data="admin_panel"))

    return kb

# ===== START =====
@bot.message_handler(commands=['start'])
def start(m):
    if is_spam(m.chat.id): return

    user = cursor.execute("SELECT banned FROM users WHERE tg_id=?", (m.chat.id,)).fetchone()
    if user and user[0] == 1:
        bot.send_message(m.chat.id, "🚫 Siz bloklangansiz")
        return

    cursor.execute("INSERT OR IGNORE INTO users (tg_id) VALUES(?)",(m.chat.id,))
    conn.commit()

    kb = types.ReplyKeyboardMarkup(resize_keyboard=True)
    kb.add(types.KeyboardButton("📱 Raqam yuborish", request_contact=True))

    bot.send_message(m.chat.id, "📱 Telefon yuboring:", reply_markup=kb)

# ===== CONTACT =====
@bot.message_handler(content_types=['contact'])
def contact(m):
    if is_spam(m.chat.id): return

    cursor.execute("UPDATE users SET phone=? WHERE tg_id=?", (m.contact.phone_number, m.chat.id))
    conn.commit()

    bot.send_message(m.chat.id, "✅ Saqlandi", reply_markup=types.ReplyKeyboardRemove())
    bot.send_message(m.chat.id, "👇 Menu:", reply_markup=menu(m.chat.id))

# ===== CALLBACK =====
@bot.callback_query_handler(func=lambda c: True)
def callback(c):
    uid = c.from_user.id

    if is_spam(uid): return

    banned = cursor.execute("SELECT banned FROM users WHERE tg_id=?", (uid,)).fetchone()
    if banned and banned[0] == 1:
        bot.answer_callback_query(c.id, "🚫 Ban!")
        return

    if c.data == "price":
        bot.edit_message_text("""💎 UC NARXLAR

30 UC - 7 000
60 UC - 12 000
90 UC - 18 000
120 UC - 25 000
180 UC - 37 000
325 UC - 60 000
660 UC - 115 000
720 UC - 130 000
985 UC - 170 000
1800 UC - 290 000
3850 UC - 630 000
8100 UC - 1 130 000
""", uid, c.message.message_id)

    elif c.data == "buy":
        kb = types.InlineKeyboardMarkup(row_width=2)
        for uc in ["30","60","90","120","180","325","660","720","985","1800","3850","8100"]:
            kb.add(types.InlineKeyboardButton(f"{uc} UC", callback_data=f"uc_{uc}"))
        bot.edit_message_text("💰 UC tanlang:", uid, c.message.message_id, reply_markup=kb)

    elif c.data.startswith("uc_"):
        uc = c.data.split("_")[1]
        user_uc[uid] = uc
        msg = bot.send_message(uid, "🆔 PUBG ID yozing:")
        bot.register_next_step_handler(msg, get_id)

    elif c.data == "history":
        data = cursor.execute("SELECT id, game_id, uc, status FROM orders WHERE user_id=?", (uid,)).fetchall()
        txt = "\n".join([f"#{i[0]} | {i[1]} | {i[2]} UC | {i[3]}" for i in data]) or "Bo‘sh"
        bot.send_message(uid, txt)

    elif c.data == "pay":
        bot.send_message(uid, "💳 8600060964894142\n📸 Chek yuboring")

    elif c.data == "about":
        bot.edit_message_text("""ℹ️ BIZ HAQIMIZDA

🎮 CoMETA UC SHOP xushkebsz☺️
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

📞 Admin: @oybekortiqboyev
        uid, c.message.message_id)

    # ===== ADMIN PANEL =====
    elif c.data == "admin_panel":
        if uid != ADMIN_ID: return

        kb = types.InlineKeyboardMarkup()
        kb.add(
            types.InlineKeyboardButton("👥 Userlar", callback_data="admin_users"),
            types.InlineKeyboardButton("📦 Buyurtmalar", callback_data="admin_orders")
        )
        kb.add(
            types.InlineKeyboardButton("🚫 Ban", callback_data="admin_ban"),
            types.InlineKeyboardButton("✅ Unban", callback_data="admin_unban")
        )
        kb.add(types.InlineKeyboardButton("🔙 Orqaga", callback_data="back_menu"))

        bot.edit_message_text("⚙️ ADMIN PANEL", uid, c.message.message_id, reply_markup=kb)

    elif c.data == "admin_users":
        if uid != ADMIN_ID: return
        count = cursor.execute("SELECT COUNT(*) FROM users").fetchone()[0]
        bot.send_message(uid, f"👥 Userlar: {count}")

    elif c.data == "admin_orders":
        if uid != ADMIN_ID: return
        data = cursor.execute("SELECT * FROM orders").fetchall()
        txt = "\n".join([f"#{i[0]} | {i[1]} | {i[3]} UC | {i[4]}" for i in data]) or "Bo‘sh"
        bot.send_message(uid, txt)

    elif c.data == "admin_ban":
        if uid != ADMIN_ID: return
        msg = bot.send_message(uid, "User ID:")
        bot.register_next_step_handler(msg, do_ban)

    elif c.data == "admin_unban":
        if uid != ADMIN_ID: return
        msg = bot.send_message(uid, "User ID:")
        bot.register_next_step_handler(msg, do_unban)

    elif c.data == "back_menu":
        bot.edit_message_text("👇 Menu:", uid, c.message.message_id, reply_markup=menu(uid))

# ===== BAN =====
def do_ban(m):
    if m.from_user.id != ADMIN_ID: return
    try:
        uid = int(m.text)
        cursor.execute("UPDATE users SET banned=1 WHERE tg_id=?", (uid,))
        conn.commit()
        bot.send_message(m.chat.id, "🚫 Ban qilindi")
    except:
        bot.send_message(m.chat.id, "Xato")

# ===== UNBAN =====
def do_unban(m):
    if m.from_user.id != ADMIN_ID: return
    try:
        uid = int(m.text)
        cursor.execute("UPDATE users SET banned=0 WHERE tg_id=?", (uid,))
        conn.commit()
        bot.send_message(m.chat.id, "✅ Unban qilindi")
    except:
        bot.send_message(m.chat.id, "Xato")

# ===== ORDER =====
def get_id(m):
    if is_spam(m.chat.id): return

    uid = m.chat.id
    game_id = m.text
    uc = user_uc.get(uid, "?")

    phone = cursor.execute("SELECT phone FROM users WHERE tg_id=?", (uid,)).fetchone()
    phone = phone[0] if phone else "yo‘q"

    cursor.execute("INSERT INTO orders(user_id,game_id,uc,status) VALUES(?,?,?,?)",
                   (uid,game_id,uc,"pending"))
    conn.commit()

    oid = cursor.lastrowid

    kb = types.InlineKeyboardMarkup()
    kb.add(
        types.InlineKeyboardButton("✅", callback_data=f"ok_{oid}"),
        types.InlineKeyboardButton("❌", callback_data=f"no_{oid}")
    )

    bot.send_message(ADMIN_ID,
                     f"BUYURTMA #{oid}\nUser:{uid}\nTel:{phone}\nID:{game_id}\nUC:{uc}",
                     reply_markup=kb)

    bot.send_message(uid, "✅ Qabul qilindi")

# ===== ADMIN TASDIQ =====
@bot.callback_query_handler(func=lambda c: c.data.startswith("ok_") or c.data.startswith("no_"))
def admin_check(c):
    if c.from_user.id != ADMIN_ID:
        return

    oid = int(c.data.split("_")[1])

    if c.data.startswith("ok_"):
        cursor.execute("UPDATE orders SET status='done' WHERE id=?", (oid,))
    else:
        cursor.execute("UPDATE orders SET status='cancel' WHERE id=?", (oid,))

    conn.commit()
    bot.answer_callback_query(c.id, "OK")

# ===== CHEK =====
@bot.message_handler(content_types=['photo'])
def check(m):
    if is_spam(m.chat.id): return
    bot.forward_message(ADMIN_ID, m.chat.id, m.message_id)
    bot.send_message(m.chat.id, "✅ Chek yuborildi")

# ===== RUN =====
print("Bot ishladi")
bot.polling(none_stop=True)
