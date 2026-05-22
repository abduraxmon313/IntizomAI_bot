from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton, WebAppInfo
from aiogram.filters import CommandStart, Command

from sqlalchemy.ext.asyncio import AsyncSession

from bot.services.user_service import get_or_create_user, get_user_by_telegram_id
from bot.keyboards.main_menu import main_menu_keyboard
from bot.keyboards.reply_keys import main_reply_keyboard
from bot.config import WEBAPP_URL

router = Router()


@router.message(CommandStart())
async def start_handler(message: Message, session: AsyncSession):
    user = await get_or_create_user(
        session=session,
        telegram_id=message.from_user.id,
        full_name=message.from_user.full_name,
        username=message.from_user.username or ""
    )

    await message.answer(
        "🎯 <b>Intizom AI</b> ga xush kelibsiz!\n\n"
        "Men sizning shaxsiy intizom yordamchingizman.\n\n"
        "📌 <b>Nima qila olaman:</b>\n"
        "• Ovoz yoki matn orqali reja tuzish\n"
        "• Vaqti kelganda eslatish\n"
        "• Bajargan ishlar uchun ball berish\n"
        "• Kunlik hisobot tayyorlash\n\n"
        "💡 <b>Boshlash uchun</b> — bugun nima qilmoqchi ekanligingizni "
        "ovozli xabar yoki matn yuboring!\n\n"
        "<i>Masalan: 'Soat 6 da turaman, 9 da kitob o'qiyman'</i>",
        parse_mode="HTML",
        reply_markup=main_reply_keyboard()
    )

    if WEBAPP_URL:
        dashboard_keyboard = InlineKeyboardMarkup(
            inline_keyboard=[[InlineKeyboardButton(text="📊 Dashboard", web_app=WebAppInfo(url=WEBAPP_URL))]]
        )
        await message.answer(
            "Web dashboardni ochish uchun tugmani bosing 👇",
            reply_markup=dashboard_keyboard
        )


@router.message(Command("help"))
async def help_handler(message: Message):
    await message.answer(
        "ℹ️ <b>Yordam</b>\n\n"
        "Mavjud buyruqlar:\n"
        "/start - botni qayta ishga tushirish\n"
        "/help - yordam oynasi\n"
        "/dashboard - web dashboard havolasi\n\n"
        "Reja qo'shish uchun matn yoki ovozli xabar yuboring.",
        parse_mode="HTML",
    )


@router.message(Command("dashboard"))
async def dashboard_handler(message: Message):
    if not WEBAPP_URL:
        await message.answer("⚠️ WEBAPP_URL sozlanmagan. Admin bilan bog'laning.")
        return

    dashboard_keyboard = InlineKeyboardMarkup(
        inline_keyboard=[[InlineKeyboardButton(text="📊 Dashboardni ochish", web_app=WebAppInfo(url=WEBAPP_URL))]]
    )
    await message.answer("Dashboardga o'tish uchun tugmani bosing 👇", reply_markup=dashboard_keyboard)


@router.callback_query(F.data == "home")
async def home_handler(callback: CallbackQuery, session: AsyncSession):
    user = await get_user_by_telegram_id(session, callback.from_user.id)

    await callback.message.edit_text(
        f"🏠 <b>Bosh sahifa</b>\n\n"
        f"👤 {user.full_name}\n"
        f"🏆 Ball: <b>{user.total_score}</b>\n"
        f"🔥 Streak: <b>{user.streak} kun</b>",
        parse_mode="HTML",
        reply_markup=main_menu_keyboard()
    )
    await callback.answer()