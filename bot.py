import asyncio
import logging
from aiohttp import web
from aiogram import Bot, Dispatcher, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup

TOKEN = "8799427639:AAGEjYP6CKdSPKBaDArpvE6g1XasvUoODDk"
ADMIN_ID = 8864442941  

bot = Bot(token=TOKEN)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)

class Form(StatesGroup):
    license = State()
    nickname = State()
    age = State()
    plans = State()
    experience_and_skill = State()
    rules_agreement = State()

def get_admin_keyboard(user_id: int):
    keyboard = types.InlineKeyboardMarkup(row_width=2)
    keyboard.add(
        types.InlineKeyboardButton(text="Одобрить", callback_data=f"approve_{user_id}"),
        types.InlineKeyboardButton(text="Отклонить", callback_data=f"reject_{user_id}")
    )
    return keyboard

@dp.message_handler(commands=['start'], state='*')
async def cmd_start(message: types.Message, state: FSMContext):
    await state.finish()
    
    welcome_text = (
        "Привет! Рад, что ты решил подать заявку. У нас — закрытое ванильное комьюнити с миром без вайпов в радиусе 11к блоков, а всё, что дальше, вайпается каждую новую версию.\n\n"
        "Важный нюанс мира: из-за откатов старых заброшенных территорий с помощью CoreProtect (/co i) в мире могут встречаться естественные нестыковки генерации между версиями и отсутствие новых предметов на старых территориях — это нормальная техническая особенность.\n\n"
        "Мы ценим стабильность и творческий подход, поэтому отбор в команду проходит в формате небольшого интервью.\n\n"
        "Важные детали о сервере:\n"
        "• Техническая часть: Версия 26.3, ядро Purpur.\n"
        "• Честная игра: Чистая ванилла. Никаких донатов, креатива, админок, сохранения инвентаря, /tpa, аукционов и прочей «мишуры». Только ты и классическое выживание.\n"
        "• Экономика: Взаимодействие и торговля строятся напрямую между игроками.\n"
        "• Атмосфера: Строго следим за отсутствием токсичности и гриферов. Есть VoiceChat, Emotecraft и защита.\n\n"
        "Начнем анкету!\n\n"
        "1. Лицензия: Есть ли она у тебя? (Напиши свой ответ)"
    )
    
    await message.answer(welcome_text)
    await Form.license.set()

@dp.message_handler(content_types=['text', 'photo', 'document'], state=Form.license)
async def process_license(message: types.Message, state: FSMContext):
    text_content = message.text or message.caption or "[Прикреплен медиа-файл]"
    async with state.proxy() as data:
        data['license'] = text_content
    await message.answer("2. Ник в Minecraft: (Напиши свой точный ник для добавления в вайтлист)")
    await Form.next()

@dp.message_handler(content_types=['text', 'photo', 'document'], state=Form.nickname)
async def process_nickname(message: types.Message, state: FSMContext):
    text_content = message.text or message.caption or "[Прикреплен медиа-файл]"
    async with state.proxy() as data:
        data['nickname'] = text_content
    await message.answer("3. Возраст: (Сколько тебе лет?)")
    await Form.next()

@dp.message_handler(content_types=['text', 'photo', 'document'], state=Form.age)
async def process_age(message: types.Message, state: FSMContext):
    text_content = message.text or message.caption or "[Прикреплен медиа-файл]"
    async with state.proxy() as data:
        data['age'] = text_content
    await message.answer("4. Планы: Что именно ты хочешь построить или чем планируешь заниматься на сервере?")
    await Form.next()

@dp.message_handler(content_types=['text', 'photo', 'document'], state=Form.plans)
async def process_plans(message: types.Message, state: FSMContext):
    text_content = message.text or message.caption or "[Прикреплен медиа-файл]"
    async with state.proxy() as data:
        data['plans'] = text_content
    await message.answer(
        "5. Опыт и навыки: Играл ли ты раньше на других приватных серверах?\n"
        "Какая твоя сильная сторона (что умеешь делать лучше всего)?\n"
        "Прикрепи ссылки на скриншоты твоих достижений/построек (или можешь скинуть сам скриншот сюда):"
    )
    await Form.next()

@dp.message_handler(content_types=['text', 'photo', 'document'], state=Form.experience_and_skill)
async def process_experience(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        if message.photo:
            data['experience_and_skill'] = message.caption or "Скриншот без подписи"
            data['photo_id'] = message.photo[-1].file_id
        elif message.document:
            data['experience_and_skill'] = f"Файл-скриншот: {message.document.file_name}"
            data['photo_id'] = None 
        else:
            data['experience_and_skill'] = message.text or "[Текст отсутствует]"
            data['photo_id'] = None
        
    rules_preview = (
        "Философия проекта и основные правила GreenWay:\n\n"
        "1. Запреты: Гриферство, воровство чужих вещей, читы и дюпы (кроме TNT, ковров и рельс для ферм) караются перманентным баном.\n"
        "2. Этика: Дистанция между базами — 500-800 блоков. Не оставляйте висящие деревья. Уважайте чужие границы (ставьте таблички с никами).\n"
        "3. Атмосфера: Никакой токсичности, политики и RMT.\n\n"
        "6. Ознакомился(-ась) ли ты со сводом правил и готов(-а) к взрослому самостоятельному выживанию? (Напиши «Да» или свой ответ)"
    )
    await message.answer(rules_preview)
    await Form.next()

@dp.message_handler(content_types=['text', 'photo', 'document'], state=Form.rules_agreement)
async def process_final(message: types.Message, state: FSMContext):
    text_content = message.text or message.caption or "[Согласие подтверждено]"

    async with state.proxy() as data:
        data['rules_agreement'] = text_content
        
    user = message.from_user
    user_id = user.id
    username = f"@{user.username}" if user.username else "скрыт"

    admin_text = (
        f"Новая заявка на сервер GreenWay!\n\n"
        f"Пользователь: {user.full_name} ({username})\n"
        f"ID: {user_id}\n\n"
        f"Лицензия: {data['license']}\n"
        f"Ник: {data['nickname']}\n"
        f"Возраст: {data['age']}\n"
        f"Планы: {data['plans']}\n"
        f"Опыт / Навыки / Скрины: {data['experience_and_skill']}\n"
        f"Готовность / Правила: {data['rules_agreement']}"
    )

    photo_to_send = data.get('photo_id')
    await state.finish()

    try:
        if photo_to_send:
            await bot.send_photo(
                ADMIN_ID,
                photo=photo_to_send,
                caption=admin_text,
                reply_markup=get_admin_keyboard(user_id)
            )
        else:
            await bot.send_message(
                ADMIN_ID,
                admin_text,
                reply_markup=get_admin_keyboard(user_id)
            )
    except Exception as e:
        logging.error(f"Не удалось отправить админу: {e}")

    full_rules_reminder = (
        "Спасибо! Твоя заявка успешно отправлена администрации.\n\n"
        "Пока мы рассматриваем твою анкету, внимательно изучи полный свод правил нашего сервера:\n\n"
        "1. Фундаментальные запреты:\n"
        "• Запрещено воровство из сундуков/печек/инвентарей мобов и жителей на чужих базах, гриферство, поджоги и разлитие лавы/воды.\n"
        "• Читы запрещены (исключение: Litematica, MiniHUD, Freecam для стройки, ReplayMod, гамма и миникарты).\n"
        "• Дюп запрещен (разрешены только TNT, ковры и рельсы для ферм).\n"
        "• Соучастие наказывается наравне с нарушением.\n\n"
        "2. Строительство и экология:\n"
        "• Дистанция между базами — 500–800 блоков. Убирайте за собой листву, закапывайте ямы от криперов.\n"
        "• Обязательно ставьте таблички с никами по периметру базы (приватов нет!).\n"
        "• Не портите ландшафт гигантскими карьерами возле жилых зон.\n\n"
        "3. Общение и чат:\n"
        "• Запрещена токсичность, оскорбления, политика, религия и RMT (реальные деньги).\n"
        "• Локальный чат — 150 блоков. Глобальный — через знак ! в начале.\n"
        "• В VoiceChat запрещены крики, спам звуками и программы для изменения голоса.\n\n"
        "Мы свяжемся с тобой в ближайшее время!"
    )
    
    try:
        await message.answer(full_rules_reminder)
    except Exception:
        pass

@dp.callback_query_handler(lambda c: c.data and c.data.startswith(('approve_', 'reject_')))
async def process_decision(callback: types.CallbackQuery):
    action, user_id_str = callback.data.split("_")
    target_user_id = int(user_id_str)

    if action == "approve":
        status_text = "Поздравляем! Твоя заявка на сервер GreenWay одобрена! Добро пожаловать в комьюнити."
        admin_status = "Заявка одобрена."
        
        try:
            await bot.send_message(target_user_id, status_text)
            await bot.send_message(
                target_user_id, 
                "Вот ссылка для доступа к нашему комьюнити и информации: https://t.me/c/4367347450/271"
            )
        except Exception:
            pass
            
    else:
        status_text = "К сожалению, твоя заявка на сервер GreenWay была отклонена."
        admin_status = "Заявка отклонена."
        
        try:
            await bot.send_message(target_user_id, status_text)
        except Exception:
            pass

    try:
        new_text = f"{callback.message.text}\n\n━━━━━━━━━━━━━━━\nСтатус: {admin_status}"
        await callback.message.edit_text(text=new_text, reply_markup=None)
    except Exception:
        pass

    try:
        await callback.answer("Готово!")
    except Exception:
        pass

# --- ВЕБ-СЕРВЕР ДЛЯ РАБОТЫ НА RENDER 24/7 ---
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
    logging.basicConfig(level=logging.INFO)
    await bot.delete_webhook(drop_pending_updates=True)
    
    # Запускаем одновременно веб-сервер и самого телеграм-бота
    await web_server()
    await dp.start_polling()

if __name__ == "__main__":
    asyncio.run(main())
