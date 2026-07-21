import os
import logging
import sys
from fastapi import FastAPI, Request
from aiogram import Bot, Dispatcher, F
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.types import Update, ReplyKeyboardMarkup, KeyboardButton
from aiogram.filters import CommandStart
from google import genai

# ВСТАВЬ СЮДА СВОЙ НАСТОЯЩИЙ ТОКЕН ВМЕСТО ТЕКСТА
TOKEN = "8918473663:AAE2-XXtYLOnZ-oiQ7txlaPxyYnA3FD8t-Q"
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")

client = genai.Client(api_key=GEMINI_API_KEY)
bot = Bot(token=TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
dp = Dispatcher()
app = FastAPI()

# Создаем удобное меню с кнопками
main_menu = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="🚀 Начать аудит")],
        [KeyboardButton(text="💡 Пример запроса"), KeyboardButton(text="ℹ️ О боте")]
    ],
    resize_keyboard=True
)

@dp.message(CommandStart())
async def command_start_handler(message) -> None:
    welcome_text = (
        "Привет! Я <b>ИИ-аудитор бизнес-проектов</b>.\n\n"
        "Я помогу найти слабые места в твоей модели, подсвечу неочевидные риски и предложу точки роста. "
        "Всё четко, по делу и без воды.\n\n"
        "Выбери действие в меню ниже 👇"
    )
    await message.answer(welcome_text, reply_markup=main_menu)

@dp.message(F.text == "🚀 Начать аудит")
async def btn_start_audit(message):
    await message.answer("Опиши свой бизнес или идею. Укажи нишу, целевую аудиторию и текущие результаты (если есть). Чем больше цифр, тем точнее разбор!")

@dp.message(F.text == "💡 Пример запроса")
async def btn_example(message):
    await message.answer(
        "<b>Пример хорошего запроса:</b>\n"
        "<i>«Я продаю свечи ручной работы через Instagram. Выручка 50к в месяц, но вся уходит на материалы и рекламу. Как масштабироваться и поднять маржу?»</i>"
    )

@dp.message(F.text == "ℹ️ О боте")
async def btn_about(message):
    await message.answer("Я работаю на базе нейросети Google Gemini. Моя задача — давать объективные и профессиональные консультации для предпринимателей.")

@dp.message()
async def echo_handler(message) -> None:
    try:
        # Уведомляем пользователя, что процесс пошел
        wait_msg = await message.answer("⏳ <i>Анализирую вводные данные...</i>")

        # Настраиваем промпт для адекватного и профессионального ответа
        prompt = (
            "Ты профессиональный, опытный бизнес-аудитор. Твоя задача — дать четкий, прагматичный и объективный разбор ситуации клиента. "
            "Пиши прямо и по делу, без лишних комплиментов, но уважительно. Структурируй ответ. "
            "ВАЖНО: Не используй Markdown-разметку (звездочки **). Для выделения жирным используй только HTML теги <b>текст</b>. "
            f"Запрос клиента: {message.text}"
        )
        
        response = client.models.generate_content(
            model='gemini-3.5-flash',
            contents=prompt
        )
        
        # Редактируем сообщение с ожиданием на готовый ответ
        await wait_msg.edit_text(response.text)
    except Exception as e:
        await message.answer(f"Ошибка аудита: {e}")

@app.on_event("startup")
async def on_startup():
    webhook_url = f"https://felix-32cx.onrender.com/{TOKEN}"
    await bot.set_webhook(webhook_url)
    logging.info(f"Webhook set to {webhook_url}")

@app.post("/{token}")
async def bot_webhook(token: str, request: Request):
    if token == TOKEN:
        update_data = await request.json()
        update = Update(**update_data)
        await dp.feed_update(bot, update)
        return {"status": "ok"}
    return {"status": "unauthorized"}
