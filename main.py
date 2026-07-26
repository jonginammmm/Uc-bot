import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("8716951130:AAEKmXgRH-4tiCeyOdO5y8CS6W5pY9HoHTg")
ADMIN_ID = int(os.getenv("6818528455"))

import logging
import time
from aiogram import Bot, Dispatcher, executor, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup

# ==========================================
# 1. SOZLAMALAR (KONFIGURATSIYA)
# ==========================================
BOT_TOKEN = "8716951130:AAEKmXgRH-4tiCeyOdO5y8CS6W5pY9HoHTg"  # BotFather'dan olingan yangi token
ADMIN_ID = 6818528455                             # Sizning Telegram ID'ingiz

# Anti-spam sozlamalari
SPAM_LIMIT = 3        # Ketma-ket ruxsat berilgan xabarlar
SPAM_TIMEOUT = 5      # Oraliq vaqt (soniya)
BAN_TIME = 30         # Vaqtincha bloklash (soniya)

logging.basicConfig(level=logging.INFO)

bot = Bot(token=BOT_TOKEN)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)

# ==========================================
# 2. MALUMOTLAR BAZASI VA ANTI-SPAM
# ==========================================
class Database:
    def __init__(self):
        self.users = {}
        self.banned_users = {}
        self.reports = []

    def add_user(self, user_id, name, username):
        if user_id not in self.users:
            self.users[user_id] = {
                "id": user_id,
                "name": name,
                "username": username or "Mavjud emas",
                "joined": time.strftime("%Y-%m-%d %H:%M:%S")
            }

    def is_banned(self, user_id):
        current = time.time()
        if user_id in self.banned_users:
            if current < self.banned_users[user_id]:
                return True
            else:
                del self.banned_users[user_id]
        return False

    def ban(self, user_id):
        self.banned_users[user_id] = time.time() + BAN_TIME

db = Database()
user_msg_tracker = {}

def check_spam(user_id: int) -> bool:
    """Anti-spam tekshiruvi"""
    if db.is_banned(user_id):
        return True
    
    current = time.time()
    if user_id not in user_msg_tracker:
        user_msg_tracker[user_id] = []
    
    user_msg_tracker[user_id] = [t for t in user_msg_tracker[user_id] if current - t < SPAM_TIMEOUT]
    user_msg_tracker[user_id].append(current)

    if len(user_msg_tracker[user_id]) > SPAM_LIMIT:
        db.ban(user_id)
        user_msg_tracker[user_id] = []
        return True
    return False

# ==========================================
# 3. FSM (HOLATLAR)
# ==========================================
class BotStates(StatesGroup):
    waiting_for_search_id = State()
    waiting_for_report = State()
    waiting_for_broadcast = State()

# ==========================================
# 4. INLINE TUGMALAR (INTERFEYS)
# ==========================================
def main_keyboard(user_id: int):
    kb = types.InlineKeyboardMarkup(row_width=2)
    kb.add(
        types.InlineKeyboardButton("👤 Profilim", callback_data="menu_profile"),
        types.InlineKeyboardButton("📊 Statistika", callback_data="menu_stats"),
        types.InlineKeyboardButton("🔎 ID Qidiruv", callback_data="menu_search"),
        types.InlineKeyboardButton("🚨 Spam Shikoyat", callback_data="menu_report"),
        types.InlineKeyboardButton("📖 Yo'riqnoma", callback_data="guide_page_1")
    )
    if user_id == ADMIN_ID:
        kb.add(types.InlineKeyboardButton("📢 Xabar Yuborish (Admin)", callback_data="admin_broadcast"))
    return kb

def back_keyboard():
    kb = types.InlineKeyboardMarkup()
    kb.add(types.InlineKeyboardButton("⬅️ Bosh Menyuga Qaytish", callback_data="menu_main"))
    return kb

def guide_keyboard(page: int):
    kb = types.InlineKeyboardMarkup(row_width=3)
    nav_buttons = []
    
    if page > 1:
        nav_buttons.append(types.InlineKeyboardButton("⬅️ Orqaga", callback_data=f"guide_page_{page-1}"))
    
    nav_buttons.append(types.InlineKeyboardButton(f"📄 {page}/3", callback_data="noop"))
    
    if page < 3:
        nav_buttons.append(types.InlineKeyboardButton("Oldinga ➡️", callback_data=f"guide_page_{page+1}"))
        
    kb.row(*nav_buttons)
    kb.add(types.InlineKeyboardButton("🏠 Bosh Menyu", callback_data="menu_main"))
    return kb

# ==========================================
# 5. HANDLERLAR (BUYRUKLAR VA TUGMALAR)
# ==========================================

# --- /start Buyrug'i ---
@dp.message_handler(commands=['start'], state="*")
async def cmd_start(message: types.Message, state: FSMContext):
    await state.finish()
    user = message.from_user
    
    if check_spam(user.id):
        await message.answer("⚠️ Siz spam sababli 30 soniyaga bloklandingiz!")
        return

    db.add_user(user.id, user.full_name, user.username)
    text = f"👋 **Salom, {user.first_name}!**\n\nInteraktiv va xavfsiz botimizga xush kelibsiz. Kerakli bo'limni tanlang:"
    await message.answer(text, reply_markup=main_keyboard(user.id), parse_mode="Markdown")

# --- Inline Tugmalar Boshqaruvi ---
@dp.callback_query_handler(lambda c: True, state="*")
async def process_callbacks(call: types.CallbackQuery, state: FSMContext):
    user_id = call.from_user.id

    if check_spam(user_id):
        await call.answer("⚠️ Siz vaqtincha bloklangansiz!", show_alert=True)
        return

    data = call.data

    # Bosh menyu
    if data == "menu_main":
        await state.finish()
        await call.message.edit_text("🏠 **Bosh Menyu:**", reply_markup=main_keyboard(user_id), parse_mode="Markdown")

    # Profil
    elif data == "menu_profile":
        u = db.users.get(user_id, {})
        text = (
            f"👤 **Sizning Profilingiz:**\n\n"
            f"🆔 **ID:** `{user_id}`\n"
            f"📝 **Ism:** {u.get('name', 'Noma\'lum')}\n"
            f"🏷 **Username:** @{u.get('username', 'Mavjud emas')}\n"
            f"📅 **Qo'shilgan vaqti:** {u.get('joined', 'Noma\'lum')}"
        )
        await call.message.edit_text(text, reply_markup=back_keyboard(), parse_mode="Markdown")

    # Statistika
    elif data == "menu_stats":
        text = (
            f"📊 **Bot Statistikasi:**\n\n"
            f"👥 Jami foydalanuvchilar: **{len(db.users)}** ta\n"
            f"🟢 Bot holati: **A'lo (Faol)**\n"
            f"🛡 Anti-spam tizimi: **Yoqilgan**"
        )
        await call.message.edit_text(text, reply_markup=back_keyboard(), parse_mode="Markdown")

    # ID Qidiruv
    elif data == "menu_search":
        await BotStates.waiting_for_search_id.set()
        await call.message.edit_text("🔎 Tekshirmoqchi bo'lgan foydalanuvchining **Telegram ID** raqamini yuboring:", reply_markup=back_keyboard(), parse_mode="Markdown")

    # Spam Shikoyat
    elif data == "menu_report":
        await BotStates.waiting_for_report.set()
        await call.message.edit_text("🚨 Sizga spam berayotgan foydalanuvchi haqida ma'lumot va sababini yozib qoldiring:", reply_markup=back_keyboard(), parse_mode="Markdown")

    # Yo'riqnoma (Oldinga/Orqaga paginatsiya)
    elif data.startswith("guide_page_"):
        page = int(data.split("_")[-1])
        pages = {
            1: "📖 **Yo'riqnoma - 1-qism:**\n\nBot orqali Telegram API taqdim etadigan ochiq ma'lumotlarni tekshirishingiz va statistikani kuzatishingiz mumkin.",
            2: "📖 **Yo'riqnoma - 2-qism:**\n\nTelegram xavfsizlik va daxlsizlik siyosati tufayli foydalanuvchilarning yashirin telefon raqamlari ko'rinmaydi.",
            3: "📖 **Yo'riqnoma - 3-qism:**\n\nKetma-ket 3 tadan ko'p xabar yuborsangiz, anti-spam tizimi sizni avtomatik ravishda 30 soniyaga bloklaydi."
        }
        await call.message.edit_text(pages.get(page, "Topilmadi"), reply_markup=guide_keyboard(page), parse_mode="Markdown")

    # Admin Broadcast
    elif data == "admin_broadcast":
        if user_id != ADMIN_ID:
            await call.answer("🚫 Siz admin emassiz!", show_alert=True)
            return
        await BotStates.waiting_for_broadcast.set()
        await call.message.edit_text("📢 Barcha foydalanuvchilarga yuboriladigan xabar matnini kiriting:", reply_markup=back_keyboard(), parse_mode="Markdown")

    await call.answer()

# --- ID bo'yicha qidiruv natijasi ---
@dp.message_handler(state=BotStates.waiting_for_search_id)
async def process_search(message: types.Message, state: FSMContext):
    if check_spam(message.from_user.id):
        return
        
    await state.finish()
    search_id = message.text.strip()

    if not search_id.isdigit():
        await message.answer("❌ Fikr bildirish va qidirish uchun faqat raqamli ID kiriting!", reply_markup=back_keyboard())
        return

    try:
        chat = await bot.get_chat(int(search_id))
        text = (
            f"🔍 **Topilgan Profil Ma'lumotlari:**\n\n"
            f"🆔 **ID:** `{chat.id}`\n"
            f"👤 **Ism:** {chat.first_name or 'Mavjud emas'}\n"
            f"🏷 **Username:** @{chat.username or 'Mavjud emas'}\n"
            f"📝 **Bio:** {chat.bio or 'Mavjud emas'}"
        )
        await message.answer(text, reply_markup=back_keyboard(), parse_mode="Markdown")
    except Exception:
        await message.answer("❌ Ushbu ID ga ega foydalanuvchi topilmadi yoki bot bilan muloqot qilmagan.", reply_markup=back_keyboard())

# --- Shikoyatni saqlash ---
@dp.message_handler(state=BotStates.waiting_for_report)
async def process_report(message: types.Message, state: FSMContext):
    if check_spam(message.from_user.id):
        return

    await state.finish()
    db.reports.append({"from": message.from_user.id, "text": message.text})
    
    # Adminga xabar yuborish
    try:
        await bot.send_message(ADMIN_ID, f"🚨 **Yangi Shikoyat!**\n\nKimdan: `{message.from_user.id}`\nXabar: {message.text}", parse_mode="Markdown")
    except Exception:
        pass

    await message.answer("✅ Shikoyatingiz adminga yetkazildi!", reply_markup=main_keyboard(message.from_user.id))

# --- Admin xabar tarqatishi ---
@dp.message_handler(state=BotStates.waiting_for_broadcast)
async def process_broadcast(message: types.Message, state: FSMContext):
    if message.from_user.id != ADMIN_ID:
        return
        
    await state.finish()
    count = 0
    await message.answer("⏳ Xabarlar tarqatilmoqda...")

    for u_id in list(db.users.keys()):
        try:
            await bot.send_message(u_id, message.text)
            count += 1
        except Exception:
            pass

    await message.answer(f"✅ Xabar **{count}** ta foydalanuvchiga yuborildi!", reply_markup=main_keyboard(message.from_user.id), parse_mode="Markdown")

# ==========================================
# 6. ISHGA TUSHIRESH
# ==========================================
if __name__ == '__main__':
    print("🚀 Bot muvaffaqiyatli ishga tushdi!")
    executor.start_polling(dp, skip_updates=True)
