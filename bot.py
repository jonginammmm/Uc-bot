
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
