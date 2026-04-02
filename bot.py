import telebot
from telebot import types
import traceback

TOKEN = "8716951130:AAEiikCG797kjvknQU3YuAFe-cyp5FJ3RFs"
ADMIN_ID = 6394219796

bot = telebot.TeleBot(TOKEN)

users = set()
banned = set()

# ===== UC NARXLAR (15 TA) =====
UC_PRICES = [
"30 UC — 7 000",
"60 UC — 12 000",
"90 UC — 18 000",
"120 UC — 25 000",
"180 UC — 37 000",
"325 UC — 55 000",
"360 UC — 72 000",
"660 UC — 115 000",
"720 UC — 130 000",
"985 UC — 170 000",
"1800 UC — 290 000",
"1920 UC — 305 000",
"1800 UC — 290 000",
"2125 UC — 335 000",
"3850 UC — 630 000",
"8100 UC — 1 120 000"
]

# ===== START =====
@bot.message_handler(commands=['start'])
def start(m):
    if m.chat.id in banned:
        return
    users.add(m.chat.id)

    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("💰 UC Narxlar", callback_data="price"),
               types.InlineKeyboardButton("📦 Buyurtma berish", callback_data="buy"))
    markup.add(types.InlineKeyboardButton("💳 To‘lov", callback_data="pay"),
               types.InlineKeyboardButton("📜 Tarix", callback_data="history"))
    markup.add(types.InlineKeyboardButton("ℹ️ Biz haqimizda", callback_data="about"),
               types.InlineKeyboardButton("📞 Admin", callback_data="admin"))

    bot.send_message(m.chat.id,
"""🎮Assalamu aleykom! CoMETA UC SHOPga xush kebsiz☺️

🔥 Eng ishonchli va tezkor UC xizmat

👇 Quyidagilardan birini tanlang""",
reply_markup=markup)

    bot.send_message(ADMIN_ID, f"👤 Yangi user: {m.chat.id}")

# ===== CALLBACK =====
@bot.callback_query_handler(func=lambda call: True)
def call(c):
    if c.message.chat.id in banned:
        return

    if c.data == "price":
        text = "💎 UC NARXLAR\n\n━━━━━━━━━━━━━━━\n"
        for i in UC_PRICES:
            text += i + "\n"
        text += "━━━━━━━━━━━━━━━"
        bot.send_message(c.message.chat.id, text)

    elif c.data == "buy":
        msg = bot.send_message(c.message.chat.id,"📦 PUBG ID va Nikizni kiriting:")
        bot.register_next_step_handler(msg, order)

    elif c.data == "pay":
        bot.send_message(c.message.chat.id,
"""💳 To‘lov uchun UZCARD VISA:

8600060964894142 
4278320021238612
👤 SATTAROV ISMAILJAN

📸 Chek yuboring""")

    elif c.data == "history":
        bot.send_message(c.message.chat.id,"📜 Tarix hozircha yo‘q")

    elif c.data == "about":
        bot.send_message(c.message.chat.id,
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

📞 Admin: @oybekortiqboyev""")

    elif c.data == "admin":
        msg = bot.send_message(c.message.chat.id,"📞 Xabaringizni yozing:")
        bot.register_next_step_handler(msg, support)

# ===== BUYURTMA =====
def order(m):
    bot.send_message(m.chat.id,"✅ Buyurtma qabul qilindi")
    bot.send_message(ADMIN_ID,f"📦 Buyurtma:\n{m.text}\nUser: {m.chat.id}")

# ===== ADMIN CHAT =====
def support(m):
    bot.send_message(ADMIN_ID,f"📩 Yangi murojat:\n{m.text}\nUser: {m.chat.id}")
    bot.send_message(m.chat.id,"✅ Adminga yuborildi")

# ===== CHEK =====
@bot.message_handler(content_types=['photo'])
def check(m):
    if m.chat.id in banned:
        return
    bot.forward_message(ADMIN_ID, m.chat.id, m.message_id)
    bot.send_message(m.chat.id,"✅ Chek yuborildi")

# ===== ADMIN BUYRUQLAR =====
@bot.message_handler(commands=['admin'])
def panel(m):
    if m.chat.id == ADMIN_ID:
        bot.send_message(m.chat.id,
"""👑 ADMIN PANEL

/send - xabar yuborish
/ban - ban
/unban - unban
/users - userlar soni""")

@bot.message_handler(commands=['users'])
def users_count(m):
    if m.chat.id == ADMIN_ID:
        bot.send_message(m.chat.id,f"👥 Users: {len(users)}")

@bot.message_handler(commands=['send'])
def send_all(m):
    if m.chat.id == ADMIN_ID:
        msg = bot.send_message(m.chat.id,"✉️ Xabar yozing:")
        bot.register_next_step_handler(msg, broadcast)

def broadcast(m):
    for u in users:
        try:
            bot.send_message(u, m.text)
        except:
            pass

@bot.message_handler(commands=['ban'])
def ban_user(m):
    if m.chat.id == ADMIN_ID:
        try:
            uid = int(m.text.split()[1])
            banned.add(uid)
            bot.send_message(m.chat.id,"🚫 Ban qilindi")
        except:
            bot.send_message(m.chat.id,"ID noto‘g‘ri")

@bot.message_handler(commands=['unban'])
def unban_user(m):
    if m.chat.id == ADMIN_ID:
        try:
            uid = int(m.text.split()[1])
            banned.discard(uid)
            bot.send_message(m.chat.id,"✅ Unban qilindi")
        except:
            bot.send_message(m.chat.id,"Xato")

# ===== SMART =====
@bot.message_handler(func=lambda m: True)
def smart(m):
    if m.chat.id in banned:
        return
    t = m.text.lower()

    if "salom" in t:
        bot.send_message(m.chat.id,"Salom 👋")
    elif "narx" in t or "uc" in t:
        text = "\n".join(UC_PRICES)
        bot.send_message(m.chat.id,text)
    elif "tolov" in t:
        bot.send_message(m.chat.id,"💳 To‘lov tugmasini bosing")
    elif "admin" in t:
        bot.send_message(m.chat.id,"📞 Admin tugmasi orqali yozing")
    else:
        pass

# ===== ERROR =====
def handle_error(e):
    bot.send_message(ADMIN_ID,f"❗ Xatolik:\n{e}")

# ===== RUN =====
while True:
    try:
        bot.polling(none_stop=True)
    except Exception as e:
        handle_error(traceback.format_exc())
