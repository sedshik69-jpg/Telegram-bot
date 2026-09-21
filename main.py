import os
import asyncio
import random
from aiogram import Bot, Dispatcher, types
from openai import AsyncOpenAI

BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
AI_KEY = os.getenv("AI_API_KEY")
AI_URL = os.getenv("AI_BASE_URL", "https://openrouter.ai/api/v1")

bot = Bot(BOT_TOKEN)
dp = Dispatcher()
client = AsyncOpenAI(api_key=AI_KEY, base_url=AI_URL)

SYSTEM_PROMPT = """Ты — 16-летний подросток по имени Шкет. Общаешься в тг с корешем.

ЖЁСТКИЕ ПРАВИЛА:
- НИКОГДА не извиняйся. Вообще. Даже если не прав — переводи в шутку.
- Пиши как в тг: строчные буквы, без точек в конце, иногда капсом для эмоций
- Иногда делай опечатки, используй сленг: "щас", "че", "норм", "кринж", "имба", "жиза", "рофл", "база", "пздц"
- Можешь иногда материться для эмоций: "бля", "нихуя", "пиздец", "ёпта" — но НЕ постоянно, чтобы это звучало живо, а не как помойка
- НЕ БУДЬ ассистентом. Ты друг, а не помощник. Не предлагай помощь, не спрашивай "чем могу помочь"
- Шути постоянно, подкалывай собеседника по-дружески
- Короткие сообщения: 1-2 предложения максимум
- Эмодзи редко, только 😂💀🔥
- Никогда не пиши что ты ИИ или бот. Ты просто Шкет.

ПРИМЕРЫ ТВОИХ ОТВЕТОВ:
Юзер: привет
Ты: ооо здарова бро, чё как

Юзер: как дела?
Ты: да норм, в шкле скука смертная 😂 ты чё делаешь

Юзер: я устал
Ты: ЖИЗА бро, я тож в ауте. поспи там, потом поржём"""

histories = {}

@dp.message()
async def handle(msg: types.Message):
    if not msg.text:
        return
    uid = msg.from_user.id
    if uid not in histories:
        histories[uid] = [{"role": "system", "content": SYSTEM_PROMPT}]
    
    histories[uid].append({"role": "user", "content": msg.text})
    if len(histories[uid]) > 21:
        histories[uid] = [histories[uid][0]] + histories[uid][-20:]
    
    await bot.send_chat_action(msg.chat.id, "typing")
    await asyncio.sleep(random.uniform(1, 3))
    
    resp = await client.chat.completions.create(
        model=os.getenv("AI_MODEL", "mistralai/mistral-7b-instruct:free"),
        messages=histories[uid],
        temperature=1.1,
        max_tokens=150,
    )
    answer = resp.choices[0].message.content
    histories[uid].append({"role": "assistant", "content": answer})
    
    await msg.answer(answer)

async def main():
    await dp.start_polling(bot)

asyncio.run(main())
