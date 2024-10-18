import re
import asyncio
import aiohttp

from aiogram import Bot, Dispatcher, types, F
from aiogram.types import ContentType, InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.filters import CommandStart, Command
from aiogram.enums.parse_mode import ParseMode

from urllib.parse import urlparse


API_TOKEN = '5809025995:AAGurQ4i-Y8OdParI5xDjGaxCe3ghfOFAlQ'
AUTHORIZED_PASSWORD = 'Start123'
FASTAPI_URL = 'http://api:8000/api/v1/scrapyd'

# Регулярное выражение для проверки домена
DOMAIN_REGEX = re.compile(r'https?://(www\.)?([^/]+)')

# Список разрешенных доменов
ALLOWED_DOMAINS = ['reuters.com', 'ft.com', 'thenationalnews.com', 'wsj.com']

# Список разрешенных доменов
DOMAIN_SPIDER_MAP = {
    'reuters.com': 'reuters_spider',
    'ft.com': 'ft_spider',
    'thenationalnews.com': 'national_spider',
    'wsj.com': 'wsj_spider'
}

# Инициализация бота и диспетчера
bot = Bot(token=API_TOKEN)
dp = Dispatcher()

# Временное хранилище авторизованных пользователей
authorized_users = set()


# Определяем функцию для запуска парсинга страницы через FastAPI
async def trigger_scrapy_spider(spider_name, url):
    async with aiohttp.ClientSession() as session:
        async with session.post(f'{FASTAPI_URL}/schedule/', json={'spider': spider_name, 'url': url}) as response:
            if response.status == 200:
                data = await response.json()
                return data.get('jobid')
            return 'Error: Failed to start scraping.' # !!!!!!!

# Определяем паука в зависимости от домена
def get_spider_name_by_domain(url):
    domain = urlparse(url).netloc
    if 'reuters.com' in domain:
        return 'reuters_spider'
    elif 'ft.com' in domain:
        return 'ft_spider'
    elif 'thenationalnews.com' in domain:
        return 'national_spider'
    elif 'wsj.com' in domain:
        return 'wsj_spider'
    return None


# Клавиатура с опциями для получения текста статьи или ссылки на Telegraph
def item_options_markup(job_id: str):
    return InlineKeyboardMarkup(inline_keyboard=[[
        InlineKeyboardButton(
            text='📰 Показать текст статьи',
            callback_data=f'get_text:{job_id}'
        )
    ], [
        InlineKeyboardButton(
            text='🔗 Получить ссылка на статью',
            callback_data=f'get_link:{job_id}'
        )
    ]])


# Обработчик команды /start
@dp.message(CommandStart())
async def start(message: types.Message):
    await message.answer(
        'Привет! 👋 Для работы с ботом необходимо '
        'авторизоаться с помощью команды /login <пароль>'
    )


# Обработчик команды /login
@dp.message(Command('login'))
async def login_command(message: types.Message):
    try:
        password = message.text.split()[1]
    except IndexError:
        await message.answer(
            '⚠️ Пожалуйста, введите команду в формате /login <пароль>.'
        )
        return

    if password == AUTHORIZED_PASSWORD:
        authorized_users.add(message.from_user.id)
        await message.answer(
            'Вы успешно авторизованы! 👍\n'
            'Теперь Вы можете отправлять ссылки '
            'для извлечения содержимого статей.'
        )
    else:
        await message.answer('⛔ Неверный пароль.')


# Обработка ссылки на статью
@dp.message()
async def handle_message(message: types.Message):
    if message.from_user.id not in authorized_users:
        await message.answer(
            '⚠️ Пожалуйста, авторизуйтесь с помощью команды /login.'
        )
        return

    url = message.text
    domain_match = DOMAIN_REGEX.search(url)
    if not domain_match:
        await message.answer(
            '⚠️ Это не похоже на ссылку.\n\n'
            'Пожалуйста, отправьте корректную ссылку.'
        )
        return

    domain = domain_match.group(2)
    if domain not in ALLOWED_DOMAINS or not DOMAIN_SPIDER_MAP.get(domain):
        await message.answer(
            f'⚠️ Домен {domain} не поддерживается.\n\n'
            f'Введите ссылку на статью с одного из сайтов: {", ".join(ALLOWED_DOMAINS)}.'
        )
        return

    spider_name = DOMAIN_SPIDER_MAP.get(domain)

    # Отправляем запрос в сторонний сервис для парсинга
    async with aiohttp.ClientSession() as session:
        async with session.post(
            f'{FASTAPI_URL}/schedule/',
            json={'spider_name': spider_name, 'url': url}
        ) as response:
            if response.status == 200:
                data = await response.json()
                return await message.answer(
                    'Процесс извлечения содержимого статьи запущен.\n'
                    '⏱️ Пожалуйста, подождите...',
                    reply_markup=item_options_markup(data['job_id']),
                    parse_mode=ParseMode.HTML
                )
            return await message.answer(
                '‼️ Ошибка при запуске парсера. Попробуйте позже.'
            )


# Обработка нажатий на кнопки
@dp.callback_query()
async def callback_query_handler(call: types.CallbackQuery):
    action, job_id = call.data.split(':')
    if action == 'get_text':
        async with aiohttp.ClientSession() as session:
            async with session.get(
                    f'{FASTAPI_URL}/status/{job_id}') as response:
                if response.status == 200:
                    data = await response.json()
                    message = (f'<b>{data.get("title")}</b>\n\n'
                               f'{data.get("text")}')
                else:
                    message = '⏱️ Новость в процессе извлечения'
        await call.message.answer(message, parse_mode=ParseMode.HTML)
    elif action == 'get_link':
        async with aiohttp.ClientSession() as session:
            async with session.get(f'{FASTAPI_URL}/status/{job_id}') as response:
                if response.status == 200:
                    data = await response.json()
                    message = (f'<b>{data.get("title")}</b>\n\n'
                               f'{data.get("telegraph_url")}')
                else:
                    message = '⏱️ Новость в процессе обработки'
        await call.message.answer(message, parse_mode=ParseMode.HTML)


async def main():
    # Запуск бота
    await dp.start_polling(bot)


if __name__ == '__main__':
    asyncio.run(main())
