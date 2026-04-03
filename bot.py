import telebot
from telebot import types
import sqlite3
from datetime import datetime, timedelta
import re

TOKEN = "8716951130:AAEiikCG797kjvknQU3YuAFe-cyp5FJ3RFs"
ADMIN_ID = 6394219796

bot = telebot.TeleBot(TOKEN)

# ===== DB =====
conn = sqlite3.connect("bot.db", check_same_thread=False)
cursor = conn.cursor()

cursor.execute("CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY, balance INTEGER DEFAULT 0, banned INTEGER DEFAULT 0)")
cursor.execute("""CREATE TABLE IF NOT EXISTS orders (
id INTEGER PRIMARY KEY AUTOINCREMENT,
user_id INTEGER,
game_id TEXT,
uc INTEGER,
amount INTEGER,
status TEXT,
time TEXT)""")
conn.commit()

# ===== PRICES =====
prices = {
60:12000,120:25000,180:37000,240:49000,325:60000,
385:72000,445:84000,505:96000,660:115000,720:128000,
985:168000,1320:220000,1800:290000,2460:385000,3850:600000,8100:1120000,
}

last = {}

# ===== USER =====
def add_user(uid):
    cursor.execute("INSERT OR IGNORE INTO users (id) VALUES (?)",(uid,))
    conn.commit()

def is_banned(uid):
    res = cursor.execute("SELECT banned FROM users WHERE id=?",(uid,)).fetchone()
    return res and res[0]==1

# ===== MENU =====
def menu():
    kb = types.InlineKeyboardMarkup(row_width=2)
    kb.add(
        types.InlineKeyboardButton("💰 Narxlar","prices"),
        types.InlineKeyboardButton("🛒 Buyurtma","order")
    )
    kb.add(
        types.InlineKeyboardButton("📜 Tarix","history"),
        types.InlineKeyboardButton("👤 Profil","profile")
    )
    kb.add(
        types.InlineKeyboardButton("💳 To‘lov","pay"),
        types.InlineKeyboardButton("🔄 Qayta","reorder")
    )
    kb.add(
        types.InlineKeyboardButton("ℹ️ Biz haqimizda","about"),
        types.InlineKeyboardButton("📞 Admin",url="https://t.me/@oybekortiqboyevv")
    )
    return kb

# ===== ADMIN =====
def admin_menu():
    kb = types.InlineKeyboardMarkup(row_width=2)
    kb.add(
        types.InlineKeyboardButton("📊 Statistika","stat"),
        types.InlineKeyboardButton("🔎 User qidirish","find")
    )
    kb.add(
        types.InlineKeyboardButton("💰 Balans berish","addbal"),
        types.InlineKeyboardButton("📢 Xabar yuborish","broadcast")
    )
    kb.add(
        types.InlineKeyboardButton("🧮 Kalkulyator","calc"),
        types.InlineKeyboardButton("📦 Buyurtmalar","orders")
    )
    return kb

# ===== START =====
@bot.message_handler(commands=['start'])
def start(m):
    try:
        add_user(m.from_user.id)

        if is_banned(m.from_user.id):
            return bot.send_message(m.chat.id,"⛔ Ban")

        bot.send_message(
            m.chat.id,
            f"🎮CoMETA UC SHOPga xush kebsiz❗\n\n🆔 ID: {m.from_user.id}",
            reply_markup=menu()
        )
    except:
        pass

# ===== ADMIN PANEL =====
@bot.message_handler(commands=['admin'])
def admin(m):
    if m.from_user.id!=ADMIN_ID: return
    bot.send_message(m.chat.id,"⚙️ Admin panel",reply_markup=admin_menu())

# ===== FIND USER =====
def find_user(m):
    try:
        uid=int(m.text)
        user=cursor.execute("SELECT * FROM users WHERE id=?",(uid,)).fetchone()

        if not user:
            return bot.send_message(m.chat.id,"❌ Topilmadi")

        orders=cursor.execute("SELECT COUNT(*) FROM orders WHERE user_id=?",(uid,)).fetchone()[0]

        bot.send_message(m.chat.id,
            f"👤 ID: {uid}\n💰 Balans: {user[1]}\n📦 Buyurtmalar: {orders}"
        )
    except:
        bot.send_message(m.chat.id,"❌ Xato")

# ===== SEND USER =====
@bot.message_handler(commands=['send'])
def send_user(m):
    if m.from_user.id!=ADMIN_ID: return
    try:
        parts=m.text.split()
        uid=int(parts[1])
        text=" ".join(parts[2:])
        bot.send_message(uid,text)
        bot.send_message(m.chat.id,"✅ Yuborildi")
    except:
        bot.send_message(m.chat.id,"❌ Format: /send ID text")

# ===== ADD BAL =====
@bot.message_handler(commands=['addbal'])
def addbal_cmd(m):
    if m.from_user.id!=ADMIN_ID: return
    try:
        uid,amount=map(int,m.text.split()[1:])
        cursor.execute("UPDATE users SET balance=balance+? WHERE id=?",(amount,uid))
        conn.commit()
        bot.send_message(m.chat.id,"✅ Qo‘shildi")
    except:
        bot.send_message(m.chat.id,"❌ Xato")

# ===== CALLBACK =====
@bot.callback_query_handler(func=lambda c: True)
def cb(c):
    uid=c.from_user.id

    if is_banned(uid): return

    if uid in last and datetime.now()-last[uid]<timedelta(seconds=2):
        return
    last[uid]=datetime.now()

    try:
        if c.data=="prices":
            kb=types.InlineKeyboardMarkup()
            for uc,p in prices.items():
                kb.add(types.InlineKeyboardButton(f"{uc} UC","uc_"+str(uc)))
            kb.add(types.InlineKeyboardButton("🔙","back"))
            bot.edit_message_text("💰 Tanlang:",c.message.chat.id,c.message.message_id,reply_markup=kb)

        elif c.data.startswith("uc_"):
            uc=int(c.data.split("_")[1])
            bot.answer_callback_query(c.id,f"{prices[uc]} so‘m")

        elif c.data=="order":
            msg=bot.send_message(c.message.chat.id,"🗿 ID yubor:")
            bot.register_next_step_handler(msg,get_id)

        elif c.data=="history":
            data=cursor.execute("SELECT * FROM orders WHERE user_id=?",(uid,)).fetchall()
            txt="\n".join([f"{i[3]}UC | {i[5]}" for i in data]) or "Yo‘q"
            bot.edit_message_text(txt,c.message.chat.id,c.message.message_id,reply_markup=menu())

        elif c.data == "profile":
            try:
        bal = cursor.execute(
            "SELECT balance FROM users WHERE id=?",
            (c.from_user.id,)
        ).fetchone()

        if bal:
            balance = bal[0]
        else:
            balance = 0

        bot.edit_message_text(
            f"👤 ID: {c.from_user.id}\n💰 Balans: {balance}",
            c.message.chat.id,
            c.message.message_id
        )

    except Exception as e:
        bot.answer_callback_query(c.id, "Xatolik!")

    except Exception as e:
        bot.answer_callback_query(c.id, "Xatolik!")

    except Exception as e:
        bot.answer_callback_query(c.id, "Xatolik!")

    except:
        bot.answer_callback_query(c.id, "Xatolik!")
    except Exception as e:
        bot.answer_callback_query(c.id, "Xatolik!")

elif c.data=="about":
    text = """ℹ️ Biz haqimizda

🎮 CoMETA UC SHOP
💎 Eng arzon UC narxlar

⚡ Bot qoidasi:
1. Adminga zarurat bo‘lsa yozing
2. Soxta chek yubormang ❌
3. PUBG ID ni to‘g‘ri kiriting
4. Admin tez javob beradi kechroq javob bersa vohima qilmang👌
5. Chek ko‘rib UC tashlanadi
6. Biz sizni aldamaymiz bizga sizni ishonchingiz kerak

🛡 Ishonchli xizmat
📞 Admin: @oybekortiqboyevv
"""
    bot.edit_message_text(
        text,
        c.message.chat.id,
        c.message.message_id,
        reply_markup=menu()
    )
    bot.edit_message_text(
        text,
        c.message.chat.id,
        c.message.message_id,
        reply_markup=menu()
    )
        elif c.data=="find":
            msg=bot.send_message(c.message.chat.id,"ID kiriting:")
            bot.register_next_step_handler(msg,find_user)

        elif c.data=="calc":
            msg=bot.send_message(c.message.chat.id,"UC yoz:")
            bot.register_next_step_handler(msg,calc)

        elif c.data=="stat":
            users=cursor.execute("SELECT COUNT(*) FROM users").fetchone()[0]
            orders=cursor.execute("SELECT COUNT(*) FROM orders").fetchone()[0]
            money=cursor.execute("SELECT SUM(amount) FROM orders WHERE status='done'").fetchone()[0] or 0
            bot.edit_message_text(f"👥 Users: {users}\n📦 Orders: {orders}\n💰 {money} so‘m",
                c.message.chat.id,c.message.message_id,reply_markup=admin_menu())

        elif c.data=="orders":
            data=cursor.execute("SELECT * FROM orders ORDER BY id DESC LIMIT 10").fetchall()
            txt="\n".join([f"{i[0]} | {i[3]}UC | {i[5]}" for i in data]) or "Yo‘q"
            bot.edit_message_text(txt,c.message.chat.id,c.message.message_id,reply_markup=admin_menu())

        elif c.data=="back":
            bot.edit_message_text("🏠 Menu",c.message.chat.id,c.message.message_id,reply_markup=menu())

    except:
        pass

# ===== ORDER =====
def get_id(m):
    if not re.fullmatch(r"\d{6,15}",m.text):
        return bot.send_message(m.chat.id,"❌ ID xato")
    msg=bot.send_message(m.chat.id,"UC yoz:")
    bot.register_next_step_handler(msg,get_uc,m.text)

def get_uc(m,gid):
    if not m.text.isdigit():
        return bot.send_message(m.chat.id,"❌ Son")
    save_order(m.from_user.id,gid,int(m.text))

def save_order(uid,gid,uc):
    amount=prices.get(uc,0)

    cursor.execute("INSERT INTO orders VALUES (NULL,?,?,?,?,?,?)",
                   (uid,gid,uc,amount,"pending",str(datetime.now())))
    conn.commit()

    oid=cursor.lastrowid

    bot.send_message(uid,f"💰 {amount} so‘m\n📸 Chek yubor")

    kb=types.InlineKeyboardMarkup()
    kb.add(
        types.InlineKeyboardButton("✅","ok_"+str(oid)),
        types.InlineKeyboardButton("❌","no_"+str(oid))
    )

    bot.send_message(ADMIN_ID,
        f"📦 Order #{oid}\n👤 {uid}\n🎮 {gid}\n💎 {uc} UC\n💰 {amount}",
        reply_markup=kb)

# ===== ADMIN TASDIQ =====
@bot.callback_query_handler(func=lambda c: c.data.startswith("ok_") or c.data.startswith("no_"))
def admin_order(c):
    if c.from_user.id!=ADMIN_ID: return

    oid=int(c.data.split("_")[1])
    uid=cursor.execute("SELECT user_id FROM orders WHERE id=?",(oid,)).fetchone()[0]

    if "ok_" in c.data:
        cursor.execute("UPDATE orders SET status='done' WHERE id=?",(oid,))
        bot.send_message(uid,"✅ Tasdiqlandi")
    else:
        cursor.execute("UPDATE orders SET status='cancel' WHERE id=?",(oid,))
        bot.send_message(uid,"❌ Rad etildi")

    conn.commit()

# ===== CHEK =====
@bot.message_handler(content_types=['photo'])
def check(m):
    bot.forward_message(ADMIN_ID,m.chat.id,m.message_id)
    bot.send_message(m.chat.id,"✅ Yuborildi")

# ===== CALCULATOR =====
def calc(m):
    try:
        uc=int(m.text)
        total=0
        remain=uc

        text="🧮 Hisob:\n"

        for pack in sorted(prices.keys(),reverse=True):
            count=remain//pack
            if count>0:
                total+=count*prices[pack]
                remain-=count*pack
                text+=f"{pack} UC x{count}\n"

        text+=f"\n💰 Jami: {total} so‘m"

        bot.send_message(m.chat.id,text)
    except:
        bot.send_message(m.chat.id,"❌ Xato")

bot.polling(none_stop=True)
