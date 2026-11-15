import asyncio
import logging
import os
from aiohttp import web
from aiogram import Bot, Dispatcher, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup

# ============================================================
#  НАСТРОЙКИ
# ============================================================
TOKEN = os.getenv("TOKEN", "8799427639:AAGEjYP6CKdSPKBaDArpvE6g1XasvUoODDk")

_admin_ids_env = os.getenv("ADMIN_IDS", "8864442941,8822149359")
ADMIN_IDS = [int(x.strip()) for x in _admin_ids_env.split(",") if x.strip()]

PORT = int(os.getenv("PORT", 10000))

processed_requests: set[int] = set()

# Хранилище ID медиа-групп (чтобы не спамить при отправке альбомов)
processed_media_groups = set()

def is_duplicate_media_group(message: types.Message) -> bool:
    """Проверяет, обрабатывали ли мы уже это сообщение из медиа-группы."""
    if message.media_group_id:
        if message.media_group_id in processed_media_groups:
            return True
        processed_media_groups.add(message.media_group_id)
        # Очистка, чтобы не забивать память
        if len(processed_media_groups) > 2000:
            processed_media_groups.clear()
    return False

# ============================================================
#  ИНИЦИАЛИЗАЦИЯ
# ============================================================
bot = Bot(token=TOKEN)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)


class Form(StatesGroup):
    age = State()
    nickname = State()
    plans = State()
    experience = State()
    strengths = State()
    screenshots = State()
    about_self = State()
    adequacy = State()
    conflicts = State()
    usefulness = State()
    rules_agreement = State()


def get_admin_keyboard(user_id: int):
    keyboard = types.InlineKeyboardMarkup(row_width=2)
    keyboard.add(
        types.InlineKeyboardButton(text="Одобрить", callback_data=f"approve_{user_id}"),
        types.InlineKeyboardButton(text="Отклонить", callback_data=f"reject_{user_id}")
    )
    return keyboard


async def send_long_text(chat_id: int, text: str, reply_markup=None):
    """Отправляет длинный текст несколькими сообщениями."""
    if len(text) <= 4000:
        await bot.send_message(chat_id, text, reply_markup=reply_markup)
        return

    chunks = []
    remaining = text
    while remaining:
        if len(remaining) <= 4000:
            chunks.append(remaining)
            break
        split_at = remaining.rfind('\n', 0, 4000)
        if split_at == -1:
            split_at = 4000
        chunks.append(remaining[:split_at])
        remaining = remaining[split_at:].lstrip('\n')

    for i, chunk in enumerate(chunks):
        is_last = (i == len(chunks) - 1)
        await bot.send_message(
            chat_id,
            chunk,
            reply_markup=reply_markup if is_last else None
        )


# ============================================================
#  АНКЕТА
# ============================================================
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
        "1. Возраст: Сколько тебе лет?"
    )

    await message.answer(welcome_text)
    await Form.age.set()


@dp.message_handler(content_types=['text', 'photo', 'document'], state=Form.age)
async def process_age(message: types.Message, state: FSMContext):
    if is_duplicate_media_group(message): return
    text_content = message.text or message.caption or "[Прикреплен медиа-файл]"
    async with state.proxy() as data:
        data['age'] = text_content
    await message.answer("2. Никнейм: Напиши свой точный ник в Minecraft (для вайтлиста).")
    await Form.next()


@dp.message_handler(content_types=['text', 'photo', 'document'], state=Form.nickname)
async def process_nickname(message: types.Message, state: FSMContext):
    if is_duplicate_media_group(message): return
    text_content = message.text or message.caption or "[Прикреплен медиа-файл]"
    async with state.proxy() as data:
        data['nickname'] = text_content
    await message.answer("3. Чем планируете заниматься на сервере?")
    await Form.next()


@dp.message_handler(content_types=['text', 'photo', 'document'], state=Form.plans)
async def process_plans(message: types.Message, state: FSMContext):
    if is_duplicate_media_group(message): return
    text_content = message.text or message.caption or "[Прикреплен медиа-файл]"
    async with state.proxy() as data:
        data['plans'] = text_content
    await message.answer("4. Был ли у вас опыт игры на приватных серверах?")
    await Form.next()


@dp.message_handler(content_types=['text', 'photo', 'document'], state=Form.experience)
async def process_experience(message: types.Message, state: FSMContext):
    if is_duplicate_media_group(message): return
    text_content = message.text or message.caption or "[Прикреплен медиа-файл]"
    async with state.proxy() as data:
        data['experience'] = text_content
    await message.answer("5. Какие сильные стороны у вас есть?")
    await Form.next()


@dp.message_handler(content_types=['text', 'photo', 'document'], state=Form.strengths)
async def process_strengths(message: types.Message, state: FSMContext):
    if is_duplicate_media_group(message): return
    text_content = message.text or message.caption or "[Прикреплен медиа-файл]"
    async with state.proxy() as data:
        data['strengths'] = text_content

    await message.answer(
        "6. Если у вас есть скриншоты ваших построек/проектов — пришлите их сюда.\n\n"
        "Вы можете отправить несколько фото или файлов (png, jpg) за раз (альбомом).\n"
        "Когда закончите — напишите «готово» (или любой текст), чтобы перейти к следующему вопросу.\n"
        "Если нечего показать — просто напишите «нет»."
    )
    await Form.next()


# --- Сбор скриншотов: обрабатываем и фото, и файлы ---
@dp.message_handler(content_types=['photo', 'document'], state=Form.screenshots)
async def collect_screenshots(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data.setdefault('photos', [])
        data.setdefault('documents', [])
        
        if message.photo:
            data['photos'].append(message.photo[-1].file_id)
        elif message.document:
            # Если прислали PNG/JPG файлом, чтобы не сжалось
            data['documents'].append(message.document.file_id)
            
        total = len(data['photos']) + len(data['documents'])

    # Отвечаем только на одиночное фото/файл, чтобы не спамить при отправке альбома
    if not message.media_group_id:
        await message.answer(f"✅ Принято! Всего файлов: {total}.\nПришлите ещё или напишите «готово», чтобы продолжить.")
    elif not is_duplicate_media_group(message):
        # Отвечаем один раз на начало медиа-группы
        await message.answer(f"✅ Группа файлов принимается...\nПришлите ещё или напишите «готово», чтобы продолжить.")


@dp.message_handler(content_types=['text'], state=Form.screenshots)
async def finish_screenshots(message: types.Message, state: FSMContext):
    text_content = (message.text or "").strip()
    async with state.proxy() as data:
        data.setdefault('photos', [])
        data.setdefault('documents', [])
        data['screenshots_text'] = text_content

    await message.answer("7. Опишите себя как человека.")
    await Form.next()


@dp.message_handler(content_types=['text', 'photo', 'document'], state=Form.about_self)
async def process_about_self(message: types.Message, state: FSMContext):
    if is_duplicate_media_group(message): return
    text_content = message.text or message.caption or "[Прикреплен медиа-файл]"
    async with state.proxy() as data:
        data['about_self'] = text_content
    await message.answer(
        "8. Что для вас значит «адекватность»? Дайте развёрнутый, аргументированный ответ."
    )
    await Form.next()


@dp.message_handler(content_types=['text', 'photo', 'document'], state=Form.adequacy)
async def process_adequacy(message: types.Message, state: FSMContext):
    if is_duplicate_media_group(message): return
    text_content = message.text or message.caption or "[Прикреплен медиа-файл]"
    async with state.proxy() as data:
        data['adequacy'] = text_content

    conflicts_text = (
        "9. Ниже перечислены конфликтные ситуации. Дайте краткий ответ по каждой "
        "(пишите по номерам: 1)… 2)… и т.д.):\n\n"
        "1) Кто-то сломал часть твоей фермы, сказав, что «тут будет лучше дорога». "
        "Какие твои первые шаги?\n\n"
        "2) Два игрока спорят, чья идея для ивента лучше, и втягивают тебя в конфликт. "
        "Что ты делаешь?\n\n"
        "3) Новичок злится, потому что у него ничего не получается, и срывается на тебе. "
        "Как ты отвечаешь?\n\n"
        "4) Ты придумал крутую редстоун-схему, но другой игрок говорит, что она «бесполезная». "
        "Что ты почувствуешь и как ответишь?\n\n"
        "5) Ты долго и аккуратно строил общественный рынок, вложил много редкого декора и "
        "продумал логистику. Другой игрок, у которого больше влияния в сообществе, просит "
        "полностью переделать центральную площадь под свой стиль, потому что «так будет лучше "
        "для сервера». Ты уверен, что его вариант хуже по функциональности и эстетике, но отказ "
        "может испортить отношения. Как ты поступишь?\n\n"
        "6) Тебе отказали в доступе к общей зоне, потому что там уже есть план застройки. "
        "Как ты реагируешь?"
    )
    await message.answer(conflicts_text)
    await Form.next()


@dp.message_handler(content_types=['text', 'photo', 'document'], state=Form.conflicts)
async def process_conflicts(message: types.Message, state: FSMContext):
    if is_duplicate_media_group(message): return
    text_content = message.text or message.caption or "[Прикреплен медиа-файл]"
    async with state.proxy() as data:
        data['conflicts'] = text_content
    await message.answer(
        "10. Чем именно вы будете полезны серверу? Почему именно вас мы должны взять?"
    )
    await Form.next()


@dp.message_handler(content_types=['text', 'photo', 'document'], state=Form.usefulness)
async def process_usefulness(message: types.Message, state: FSMContext):
    if is_duplicate_media_group(message): return
    text_content = message.text or message.caption or "[Прикреплен медиа-файл]"
    async with state.proxy() as data:
        data['usefulness'] = text_content

    rules_preview = (
        "Перед отправкой заявки — ознакомься со сводом правил GreenWay:\n\n"
        "1. Фундаментальные запреты:\n"
        "• Запрещено воровство из сундуков/печек/инвентарей мобов и жителей на чужих базах, "
        "гриферство, поджоги и разлитие лавы/воды.\n"
        "• Читы запрещены (исключение: Litematica, MiniHUD, Freecam для стройки, ReplayMod, "
        "гамма и миникарты).\n"
        "• Дюп запрещен (разрешены только TNT, ковры и рельсы для ферм).\n"
        "• Соучастие наказывается наравне с нарушением.\n\n"
        "2. Строительство и экология:\n"
        "• Дистанция между базами — 500–800 блоков. Убирайте за собой листву, закапывайте ямы.\n"
        "• Обязательно ставьте таблички с никами по периметру базы (приватов нет!).\n"
        "• Не портите ландшафт гигантскими карьерами возле жилых зон.\n\n"
        "3. Общение и чат:\n"
        "• Запрещена токсичность, оскорбления, политика, религия и RMT.\n"
        "• Локальный чат — 150 блоков. Глобальный — через знак ! в начале.\n"
        "• В VoiceChat запрещены крики, спам звуками и программы для изменения голоса.\n\n"
        "Последний шаг: напиши «Да», если ознакомился(-ась) с правилами и согласен(-на) "
        "с ними. Или задай уточняющий вопрос."
    )
    await message.answer(rules_preview)
    await Form.next()


@dp.message_handler(content_types=['text', 'photo', 'document'], state=Form.rules_agreement)
async def process_final(message: types.Message, state: FSMContext):
    if is_duplicate_media_group(message): return
    text_content = message.text or message.caption or "[Согласие подтверждено]"

    async with state.proxy() as data:
        data['rules_agreement'] = text_content
        form_data = dict(data)
    await state.finish()

    user = message.from_user
    user_id = user.id
    username = f"@{user.username}" if user.username else "скрыт"

    photos = form_data.get('photos', [])
    documents = form_data.get('documents', [])
    screenshots_text = form_data.get('screenshots_text', '').strip()

    # Формируем строку про скриншоты для текста заявки
    files_count = len(photos) + len(documents)
    if files_count:
        screenshots_line = f"прикреплено файлов: {files_count}"
        if screenshots_text and screenshots_text.lower() not in ('готово', 'готов', 'done', 'хватит', 'всё', 'все'):
            screenshots_line += f" (комментарий: {screenshots_text})"
    else:
        screenshots_line = screenshots_text or "нет"

    admin_text = (
        f"📝 Новая заявка на сервер GreenWay!\n\n"
        f"👤 {user.full_name} ({username})\n"
        f"🆔 ID: {user_id}\n\n"
        f"1) Возраст: {form_data['age']}\n\n"
        f"2) Никнейм: {form_data['nickname']}\n\n"
        f"3) Чем планирует заниматься: {form_data['plans']}\n\n"
        f"4) Опыт на приватных серверах: {form_data['experience']}\n\n"
        f"5) Сильные стороны: {form_data['strengths']}\n\n"
        f"6) Скриншоты: {screenshots_line}\n\n"
        f"7) О себе: {form_data['about_self']}\n\n"
        f"8) Что значит адекватность: {form_data['adequacy']}\n\n"
        f"9) Ответы на конфликтные ситуации:\n{form_data['conflicts']}\n\n"
        f"10) Чем полезен серверу: {form_data['usefulness']}\n\n"
        f"Согласие с правилами: {form_data['rules_agreement']}"
    )

    keyboard = get_admin_keyboard(user_id)

    for admin_id in ADMIN_IDS:
        try:
            # 1. Отправляем фото по одному
            total = len(photos)
            for i, photo_id in enumerate(photos, 1):
                caption = f"🖼 Скриншот {i}/{total} от {user.full_name}" if total > 1 else f"🖼 Скриншот от {user.full_name}"
                try:
                    await bot.send_photo(admin_id, photo=photo_id, caption=caption)
                except Exception as e:
                    logging.error(f"Не удалось отправить фото {i} админу {admin_id}: {e}")

            # 2. Отправляем документы (если были PNG/JPG файлом)
            for i, doc_id in enumerate(documents, 1):
                try:
                    await bot.send_document(admin_id, document=doc_id, caption=f"📎 Файл {i} от {user.full_name}")
                except Exception as e:
                    logging.error(f"Не удалось отправить документ {i} админу {admin_id}: {e}")

            # 3. Отправляем текст заявки с кнопками
            await send_long_text(admin_id, admin_text, reply_markup=keyboard)

        except Exception as e:
            logging.error(f"Не удалось отправить заявку админу {admin_id}: {e}")

    thanks_text = (
        "Спасибо! Твоя заявка успешно отправлена администрации. "
        "Мы свяжемся с тобой в ближайшее время."
    )
    try:
        await message.answer(thanks_text)
    except Exception:
        pass


# ============================================================
#  РЕШЕНИЕ АДМИНА
# ============================================================
@dp.callback_query_handler(lambda c: c.data and c.data.startswith(('approve_', 'reject_')))
async def process_decision(callback: types.CallbackQuery):
    await callback.answer()

    action, user_id_str = callback.data.split("_")
    target_user_id = int(user_id_str)

    if target_user_id in processed_requests:
        try:
            await callback.message.edit_reply_markup(reply_markup=None)
        except Exception:
            pass
        return

    processed_requests.add(target_user_id)

    if action == "approve":
        status_text = "Поздравляем! Твоя заявка на сервер GreenWay одобрена! Добро пожаловать в комьюнити."
        admin_status = "Заявка одобрена."
        try:
            await bot.send_message(target_user_id, status_text)
            await bot.send_message(
                target_user_id,
                "Вот ссылка для доступа к нашему комьюнити и информации: https://t.me/+2mPMUjSMu0xmYmQy"
            )
        except Exception as e:
            logging.error(f"Не удалось написать пользователю {target_user_id}: {e}")
    else:
        status_text = "К сожалению, твоя заявка на сервер GreenWay была отклонена."
        admin_status = "Заявка отклонена."
        try:
            await bot.send_message(target_user_id, status_text)
        except Exception as e:
            logging.error(f"Не удалось написать пользователю {target_user_id}: {e}")

    try:
        msg = callback.message
        suffix = f"\n\n━━━━━━━━━━━━━━━\nСтатус: {admin_status}"
        if msg.photo:
            new_caption = (msg.caption or "") + suffix
            await msg.edit_caption(caption=new_caption, reply_markup=None)
        else:
            new_text = (msg.text or "") + suffix
            await msg.edit_text(text=new_text, reply_markup=None)
    except Exception as e:
        logging.error(f"Не удалось обновить сообщение админа: {e}")


# ============================================================
#  ВЕБ-СЕРВЕР ДЛЯ RENDER
# ============================================================
async def handle(request):
    return web.Response(text="GreenWay Bot is running!")


async def web_server():
    app = web.Application()
    app.add_routes([web.get('/', handle)])
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, '0.0.0.0', PORT)
    await site.start()


async def main():
    logging.basicConfig(level=logging.INFO)
    await bot.delete_webhook(drop_pending_updates=True)
    await web_server()
    await dp.start_polling()


if __name__ == "__main__":
    asyncio.run(main())
