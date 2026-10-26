import logging
import asyncio
from aiohttp import web
from aiogram import Bot, Dispatcher, executor, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup

API_TOKEN = '8799427639:AAGEjYP6CKdSPKBaDArpvE6g1XasvUoODDk'
ADMIN_IDS = [8864442941, 8822149359]

logging.basicConfig(level=logging.INFO)

bot = Bot(token=API_TOKEN)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)

pending_users = set()

class Form(StatesGroup):
    game_nick = State()
    age = State()
    about = State()

@dp.message_handler(commands=['start'])
async def cmd_start(message: types.Message):
    user_id = message.from_user.id
    if user_id in pending_users:
        await message.reply("⏳ Ваша заявка уже находится на рассмотрении у администрации. Пожалуйста, дождитесь ответа!")
        return

    await message.reply("Привет! Добро пожаловать на ванильный майнкрафт-сервер **GreenWay**.\n\nДавай заполним заявку на вход. Напиши свой **игровой ник**:")
    await Form.game_nick.set()

@dp.message_handler(state=Form.game_nick)
async def process_nick(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['game_nick'] = message.text
    await message.reply("Сколько тебе лет?")
    await Form.next()

@dp.message_handler(state=Form.age)
async def process_age(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['age'] = message.text
    await message.reply("Расскажи немного о себе (почему хочешь играть у нас, планы):")
    await Form.next()

@dp.message_handler(state=Form.about)
async def process_about(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    if user_id in pending_users:
        await state.finish()
        return

    async with state.proxy() as data:
        data['about'] = message.text

    pending_users.add(user_id)
    user = message.from_user
    username_str = f"@{user.username}" if user.username else "нет юзернейма"

    admin_text = (
        f"🚨 **Новая заявка на сервер GreenWay!**\n\n"
        f"👤 **От:** {user.get_mention()} ({username_str})\n"
        f"🆔 **ID:** `{user.id}`\n"
        f"🎮 **Ник:** `{data['game_nick']}`\n"
        f"📅 **Возраст:** `{data['age']}`\n"
        f"📝 **О себе:** {data['about']}"
    )

    keyboard = types.InlineKeyboardMarkup(row_width=2)
    keyboard.add(
        types.InlineKeyboardButton("✅ Одобрить", callback_data=f"accept_{user.id}"),
        types.InlineKeyboardButton("❌ Отклонить", callback_data=f"decline_{user.id}")
    )

    for admin_id in ADMIN_IDS:
        try:
            await bot.send_message(admin_id, admin_text, reply_markup=keyboard, parse_mode="Markdown")
        except Exception as e:
            logging.error(f"Не удалось отправить админу {admin_id}: {e}")

    await message.reply("✅ Спасибо! Твоя заявка отправлена администрации на рассмотрение. Ожидай ответа.")
    await state.finish()

@dp.callback_query_handler(lambda c: c.data.startswith(('accept_', 'decline_')))
async def process_admin_decision(callback_query: types.CallbackQuery):
    admin_id = callback_query.from_user.id
    if admin_id not in ADMIN_IDS:
        await callback_query.answer("⚠️ Вы не являетесь администратором этого бота!", show_alert=True)
        return

    action, target_user_id_str = callback_query.data.split('_')
    target_user_id = int(target_user_id_str)

    if target_user_id in pending_users:
        pending_users.remove(target_user_id)

    if action == 'accept':
        try:
            await bot.send_message(target_user_id, "🎉 **Поздравляем!** Ваша заявка на сервер GreenWay успешно **одобрена** администратором! Добро пожаловать!")
        except:
            pass
        await callback_query.message.edit_text(callback_query.message.text + "\n\n✅ **Статус:** Одобрено ✅")
        await callback_query.answer("Вы одобрили заявку!")

    elif action == 'decline':
        try:
            await bot.send_message(target_user_id, "😔 К сожалению, ваша заявка на сервер GreenWay была **отклонена** администрацией.")
        except:
            pass
        await callback_query.message.edit_text(callback_query.message.text + "\n\n❌ **Статус:** Отклонено ❌")
        await callback_query.answer("Вы отклонили заявку.")

# --- ЗАГЛУШКА ВЕБ-СЕРВЕРА ДЛЯ RENDER ---
async def handle(request):
    return web.Response(text="GreenWay Bot is running!")

async def web_server():
    app = web.Application()
    app.add_routes([web.get('/', handle)])
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, '0.0.0.0', 10000)
    await site.start()

async def main():
    # Запускаем веб-сервер и телеграм-бота одновременно
    await web_server()
    await dp.start_polling()

if __name__ == '__main__':
    asyncio.run(main())
