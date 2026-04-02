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

cursor.execute("CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY, balance INTEGER DEFAULT 0, banned_until TEXT)")
cursor.execute("""CREATE TABLE IF NOT EXISTS orders (
id INTEGER PRIMARY KEY AUTOINCREMENT,
user_id INTEGER,
game_id TEXT,
uc TEXT,
amount INTEGER,
status TEXT,
time TEXT)""")
conn.commit()

# ===== DATA =====
prices = {
"60":12000,"120":25000,"180":37000,"240":49000,"325":60000,
"385":72000,"445":84000,"505":96000,"660":115000,"720":128000,
"985":168000,"1320":220000,"1800":290000,"2460":385000,"3850":630000,"8100":11200000,
}

# ===== USER =====
def add_user(uid):
    cursor.execute("INSERT OR IGNORE INTO users (id) VALUES (?)",(uid,))
    conn.commit()

def is_banned(uid):
    res = cursor.execute("SELECT banned_until FROM users WHERE id=?",(uid,)).fetchone()
    if res and res[0]:
        return datetime.now() < datetime.fromisoformat(res[0])
    return False

# ===== MENU =====
def menu(uid):
    kb = types.ReplyKeyboardMarkup(resize_keyboard=True)
    kb.add("💰 Narxlar","📦 Buyurtma")
    kb.add("💳 To‘lov","📜 Tarix")
    kb.add("👤 Profil","🔄 Qayta olish")
    kb.add("📞 Admin")
    if uid == ADMIN_ID:
        kb.add("👑 Admin Panel")
    return kb

# ===== START =====
@bot.message_handler(commands=['start'])
def start(m):
    add_user(m.from_user.id)
    if is_banned(m.from_user.id):
        return bot.send_message(m.chat.id,"⛔ Ban")
    bot.send_message(m.chat.id,"🎮 CoMETA UC SHOP",reply_markup=menu(m.from_user.id))

# ===== NARXLAR INLINE =====
@bot.message_handler(func=lambda m: m.text=="💰 Narxlar")
def narx(m):
    kb = types.InlineKeyboardMarkup(row_width=2)
    for uc,price in prices.items():
        kb.add(types.InlineKeyboardButton(f"{uc} UC — {price}",callback_data=f"uc_{uc}"))
    bot.send_message(m.chat.id,"💰 UC Narxlar:",reply_markup=kb)

# ===== BUY =====
@bot.callback_query_handler(func=lambda c: c.data.startswith("uc_"))
def uc(c):
    uc = c.data.split("_")[1]
    msg = bot.send_message(c.message.chat.id,f"{uc} UC tanlandi\nID yubor:")
    bot.register_next_step_handler(msg,save,uc)

def save(m,uc):
    gid = m.text
    amount = prices[uc]

    cursor.execute("INSERT INTO orders (user_id,game_id,uc,amount,status,time) VALUES (?,?,?,?,?,?)",
                   (m.from_user.id,gid,uc,amount,"pending",str(datetime.now())))
    conn.commit()

    oid = cursor.lastrowid

    kb = types.InlineKeyboardMarkup()
    kb.add(types.InlineKeyboardButton("✅",callback_data=f"ok_{oid}"),
           types.InlineKeyboardButton("❌",callback_data=f"no_{oid}"))

    bot.send_message(m.chat.id,"✅ Buyurtma qabul qilindi")
    bot.send_message(ADMIN_ID,f"#{oid}\nID:{gid}\n{uc} UC",reply_markup=kb)

# ===== ADMIN ORDER =====
@bot.callback_query_handler(func=lambda c: c.data.startswith("ok_") or c.data.startswith("no_"))
def admin_order(c):
    if c.from_user.id != ADMIN_ID:
        return

    oid = int(c.data.split("_")[1])
    user_id = cursor.execute("SELECT user_id FROM orders WHERE id=?",(oid,)).fetchone()[0]

    if c.data.startswith("ok"):
        cursor.execute("UPDATE orders SET status='done' WHERE id=?",(oid,))
        bot.send_message(user_id,"✅ Buyurtmangiz bajarildi")
        bot.edit_message_text("✅ Tasdiqlandi",c.message.chat.id,c.message.message_id)
    else:
        cursor.execute("UPDATE orders SET status='cancel' WHERE id=?",(oid,))
        bot.send_message(user_id,"❌ Bekor qilindi")
        bot.edit_message_text("❌ Bekor",c.message.chat.id,c.message.message_id)

    conn.commit()

# ===== TARIX =====
@bot.message_handler(func=lambda m: m.text=="📜 Tarix")
def history(m):
    data = cursor.execute("SELECT * FROM orders WHERE user_id=?",(m.from_user.id,)).fetchall()
    txt = "\n".join([f"{i[0]} | {i[3]}UC | {i[5]}" for i in data]) or "Yo‘q"
    bot.send_message(m.chat.id,txt)

# ===== PROFIL =====
@bot.message_handler(func=lambda m: m.text=="👤 Profil")
def profil(m):
    bal = cursor.execute("SELECT balance FROM users WHERE id=?",(m.from_user.id,)).fetchone()[0]
    bot.send_message(m.chat.id,f"💰 Balans: {bal}")

# ===== REORDER =====
@bot.message_handler(func=lambda m: m.text=="🔄 Qayta olish")
def reorder(m):
    last = cursor.execute("SELECT game_id,uc FROM orders WHERE user_id=? ORDER BY id DESC LIMIT 1",(m.from_user.id,)).fetchone()
    if not last:
        return bot.send_message(m.chat.id,"❌ Yo‘q")
    gid,uc = last
    amount = prices[uc]

    cursor.execute("INSERT INTO orders (user_id,game_id,uc,amount,status,time) VALUES (?,?,?,?,?,?)",
                   (m.from_user.id,gid,uc,amount,"pending",str(datetime.now())))
    conn.commit()

    bot.send_message(m.chat.id,"✅ Qayta buyurtma")

# ===== ADMIN PANEL =====
@bot.message_handler(func=lambda m: m.text=="👑 Admin Panel")
def admin_panel(m):
    if m.from_user.id != ADMIN_ID:
        return
    kb = types.ReplyKeyboardMarkup(resize_keyboard=True)
    kb.add("📊 Statistika","📦 Buyurtmalar")
    kb.add("💬 Xabar yuborish","🚫 Ban")
    kb.add("✅ Unban","🔙 Orqaga")
    bot.send_message(m.chat.id,"👑 Admin Panel",reply_markup=kb)

# ===== ADMIN BUTTONS =====
@bot.message_handler(func=lambda m: m.text=="📊 Statistika")
def stats(m):
    if m.from_user.id != ADMIN_ID: return
    u = cursor.execute("SELECT COUNT(*) FROM users").fetchone()[0]
    o = cursor.execute("SELECT COUNT(*) FROM orders").fetchone()[0]
    bot.send_message(m.chat.id,f"Users:{u}\nOrders:{o}")

@bot.message_handler(func=lambda m: m.text=="📦 Buyurtmalar")
def orders(m):
    if m.from_user.id != ADMIN_ID: return
    data = cursor.execute("SELECT * FROM orders ORDER BY id DESC LIMIT 10").fetchall()
    txt = "\n".join([f"{i[0]} | {i[2]} | {i[3]}UC | {i[5]}" for i in data]) or "Yo‘q"
    bot.send_message(m.chat.id,txt)

@bot.message_handler(func=lambda m: m.text=="💬 Xabar yuborish")
def send(m):
    if m.from_user.id != ADMIN_ID: return
    msg = bot.send_message(m.chat.id,"Xabar yoz:")
    bot.register_next_step_handler(msg,send_all)

def send_all(m):
    users = cursor.execute("SELECT id FROM users").fetchall()
    for u in users:
        try: bot.send_message(u[0],m.text)
        except: pass

@bot.message_handler(func=lambda m: m.text=="🚫 Ban")
def ban(m):
    if m.from_user.id != ADMIN_ID: return
    msg = bot.send_message(m.chat.id,"ID yubor:")
    bot.register_next_step_handler(msg,do_ban)

def do_ban(m):
    uid = int(m.text)
    until = datetime.now()+timedelta(hours=1)
    cursor.execute("UPDATE users SET banned_until=? WHERE id=?",(until.isoformat(),uid))
    conn.commit()
    bot.send_message(m.chat.id,"Ban berildi")

@bot.message_handler(func=lambda m: m.text=="✅ Unban")
def unban(m):
    if m.from_user.id != ADMIN_ID: return
    msg = bot.send_message(m.chat.id,"ID yubor:")
    bot.register_next_step_handler(msg,do_unban)

def do_unban(m):
    uid = int(m.text)
    cursor.execute("UPDATE users SET banned_until=NULL WHERE id=?",(uid,))
    conn.commit()
    bot.send_message(m.chat.id,"Unban")

@bot.message_handler(func=lambda m: m.text=="🔙 Orqaga")
def back(m):
    bot.send_message(m.chat.id,"Menu",reply_markup=menu(m.from_user.id))

# ===== SMART =====
@bot.message_handler(func=lambda m: True)
def smart(m):
    t = m.text.lower()
    if "salom" in t:
        bot.send_message(m.chat.id,"Salom 👋")
    elif "narx" in t or "uc" in t:
        narx(m)
    else:
        bot.send_message(m.chat.id,"❌ Tushunmadim",reply_markup=menu(m.from_user.id))
# ===== TO‘LOV =====
@bot.message_handler(func=lambda m: m.text=="💳 To‘lov")
def payment(m):
    bot.send_message(m.chat.id,
"""💳 To‘lov uchun karta UZCARD VISA:

8600060964894142  4278320021238612
👤 Ism: SATTAROV ISMAILJAN

📸 To‘lov qilgach chek yuboring""")

# ===== CHEK =====
@bot.message_handler(content_types=['photo'])
def check(m):
    bot.forward_message(ADMIN_ID, m.chat.id, m.message_id)
    bot.send_message(m.chat.id,"✅ Chek yuborildi")
  # ===== BIZ HAQIMIZDA =====
@bot.message_handler(func=lambda m: m.text=="ℹ️ Biz haqimizda")
def about(m):
    bot.send_message(m.chat.id,
"""ℹ️ Biz haqimizda

🎮 CoMETA UC SHOP
💎 Eng arzon narxlar CoMETA UCda Kattaro Uc paket kerak bosa adminga✍️
⚡ Soxta chek otkazaman deb oylamela Soxta chekka UC🖕
🛡 Ishonchli UC servis 
✅ Qandaydir savoliz bosa adminga✍️ bekorchi narsa yozmelar 
👌 Uc hisobizda 2 7minut oraligida tushadi biroz kechksa vohima qivormeylar. Bizga birovni haqqi keremas Faqat silani ishonchila kerak

📞 Admin: @oybekortiqboyevv
""")
# ===== RUN =====
bot.polling()
