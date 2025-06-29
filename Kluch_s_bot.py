import asyncio
from aiogram import Bot, Dispatcher, F
from aiogram.enums import ParseMode
from aiogram.types import (
    Message,
    ReplyKeyboardMarkup,
    KeyboardButton,
    ReplyKeyboardRemove
)
from aiogram.client.default import DefaultBotProperties
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

# 🔑 ВСТАВЬ СЮДА СВОЙ ТОКЕН
TOKEN = "7961914536:AAEel5xAHwY3vMghfw66jbYixbVyNVhw1qQ"

# Создаем бота и диспетчер
bot = Bot(token=TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
dp = Dispatcher()

# -------- FSM СОСТОЯНИЯ --------
class BookOrder(StatesGroup):
    type = State()
    cover = State()
    pages = State()
    color = State()
    cover_type = State()
    quantity = State()

# -------- КОМАНДА /START --------
@dp.message(Command("start"))
async def start(message: Message, state: FSMContext):
    await message.answer(
        "📦 Что будем печатать?",
        reply_markup=ReplyKeyboardMarkup(
            keyboard=[
                [KeyboardButton(text="📖 Книга")],
                [KeyboardButton(text="📄 Буклет"), KeyboardButton(text="📇 Визитки")]
            ],
            resize_keyboard=True
        )
    )
    await state.set_state(BookOrder.type)

# -------- ВЫБОР ТИПА --------
@dp.message(BookOrder.type)
async def process_type(message: Message, state: FSMContext):
    await state.update_data(type=message.text)
    if message.text == "📖 Книга":
        await message.answer(
            "📚 Какой переплет?",
            reply_markup=ReplyKeyboardMarkup(
                keyboard=[
                    [KeyboardButton(text="Скрепка")],
                    [KeyboardButton(text="Клей")],
                    [KeyboardButton(text="Клей с тиснением")]
                ],
                resize_keyboard=True
            )
        )
        await state.set_state(BookOrder.cover)
    else:
        await message.answer("❗ Пока поддерживается только расчет книги.")
        await state.clear()

# -------- ПЕРЕПЛЕТ --------
@dp.message(BookOrder.cover)
async def process_cover(message: Message, state: FSMContext):
    await state.update_data(cover=message.text)
    await message.answer(
        "📄 Сколько страниц?",
        reply_markup=ReplyKeyboardMarkup(
            keyboard=[
                [KeyboardButton(text="50-100")],
                [KeyboardButton(text="100-200")],
                [KeyboardButton(text="200-300")]
            ],
            resize_keyboard=True
        )
    )
    await state.set_state(BookOrder.pages)

# -------- КОЛ-ВО СТРАНИЦ --------
@dp.message(BookOrder.pages)
async def process_pages(message: Message, state: FSMContext):
    await state.update_data(pages=message.text)
    await message.answer(
        "🎨 Цветность книги?",
        reply_markup=ReplyKeyboardMarkup(
            keyboard=[
                [KeyboardButton(text="Черно-белая (текст)")],
                [KeyboardButton(text="Черно-белая с картинками")],
                [KeyboardButton(text="Цветные картинки 10% страниц")]
            ],
            resize_keyboard=True
        )
    )
    await state.set_state(BookOrder.color)

# -------- ЦВЕТ --------
@dp.message(BookOrder.color)
async def process_color(message: Message, state: FSMContext):
    await state.update_data(color=message.text)
    await message.answer(
        "🧾 Какая обложка?",
        reply_markup=ReplyKeyboardMarkup(
            keyboard=[
                [KeyboardButton(text="Мягкая ч/б")],
                [KeyboardButton(text="Мягкая цветная")],
                [KeyboardButton(text="Жесткая цветная")]
            ],
            resize_keyboard=True
        )
    )
    await state.set_state(BookOrder.cover_type)

# -------- ОБЛОЖКА --------
@dp.message(BookOrder.cover_type)
async def process_cover_type(message: Message, state: FSMContext):
    await state.update_data(cover_type=message.text)
    await message.answer(
        "📦 Какой тираж?",
        reply_markup=ReplyKeyboardMarkup(
            keyboard=[
                [KeyboardButton(text="100"), KeyboardButton(text="200")],
                [KeyboardButton(text="300"), KeyboardButton(text="500")]
            ],
            resize_keyboard=True
        )
    )
    await state.set_state(BookOrder.quantity)

# -------- ТИРАЖ И РАСЧЕТ --------
@dp.message(BookOrder.quantity)
async def process_quantity(message: Message, state: FSMContext):
    await state.update_data(quantity=message.text)
    data = await state.get_data()

    # -------- ЦЕНОВЫЕ КОЭФФИЦИЕНТЫ --------
    base_price = 50  # базовая цена за книгу в рублях

    cover_type_coef = {
        "Скрепка": 1.0,
        "Клей": 1.2,
        "Клей с тиснением": 1.5
    }

    pages_coef = {
        "50-100": 1.0,
        "100-200": 1.4,
        "200-300": 1.8
    }

    color_coef = {
        "Черно-белая (текст)": 1.0,
        "Черно-белая с картинками": 1.3,
        "Цветные картинки 10% страниц": 1.6
    }

    cover_design_coef = {
        "Мягкая ч/б": 1.0,
        "Мягкая цветная": 1.2,
        "Жесткая цветная": 1.6
    }

    qty = int(data["quantity"])
    price_per_book = (
        base_price *
        cover_type_coef.get(data["cover"], 1.0) *
        pages_coef.get(data["pages"], 1.0) *
        color_coef.get(data["color"], 1.0) *
        cover_design_coef.get(data["cover_type"], 1.0)
    )

    total_price = int(price_per_book * qty)

    # -------- СООБЩЕНИЕ С ИТОГОМ --------
    await message.answer(
        f"📘 <b>Ваш выбор:</b>\n"
        f"Тип: {data['type']}\n"
        f"Переплет: {data['cover']}\n"
        f"Страниц: {data['pages']}\n"
        f"Цветность: {data['color']}\n"
        f"Обложка: {data['cover_type']}\n"
        f"Тираж: {qty} шт.\n\n"
        f"💰 <b>Примерная стоимость: {total_price} руб.</b>\n\n"
        f"ℹ️ Для точного расчета свяжитесь с менеджером.",
        reply_markup=ReplyKeyboardMarkup(
            keyboard=[
                [KeyboardButton(text="🔁 Повторить расчет")]
            ],
            resize_keyboard=True
        )
    )
    await state.clear()

# -------- ПОВТОРИТЬ РАСЧЕТ --------
@dp.message(F.text == "🔁 Повторить расчет")
async def repeat(message: Message, state: FSMContext):
    await start(message, state)

# -------- ЗАПУСК --------
async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())