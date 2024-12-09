# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter

import lxml.html
import requests
import aiohttp

from deep_translator import GoogleTranslator
from telegraph import Telegraph

from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine

from scrapy.exceptions import DropItem

from .models import Item, create_tables


class TranslationPipeline:
    def __init__(self):
        # Инициализируем переводчик один раз при создании объекта
        self.translator = GoogleTranslator(source='auto', target='ru')

    def process_item(self, item, spider):
        # Предполагаем, что HTML-контент статьи хранится в item['text']
        html_content = item['text']

        # Парсим HTML-контент
        doc = lxml.html.fromstring(html_content)

        # Рекурсивная функция для перевода текстовых узлов
        def translate_element(element):
            # Переводим текст внутри тега
            if element.text and element.text.strip():
                translated_text = self.translator.translate(element.text)
                element.text = translated_text

            # Рекурсивно обрабатываем дочерние элементы
            for child in element:
                translate_element(child)
                # Переводим текст после дочернего тега (tail)
                if child.tail and child.tail.strip():
                    translated_tail = self.translator.translate(child.tail)
                    child.tail = translated_tail

        # Запускаем перевод начиная с корневого элемента
        translate_element(doc)

        # Преобразуем обратно в строку HTML
        translated_html = lxml.html.tostring(doc, encoding='unicode')

        # Сохраняем переведённый HTML обратно в item
        item['text'] = translated_html

        return item


class WebhookPipeline:
    def __init__(self):
        # Инициализация Telegraph клиента
        self.webhook_url = 'http://api:8000/api/v1/scrapyd/webhook/'

    async def process_item(self, item, spider):
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(
                        f'{self.webhook_url}{item["id"]}') as response:
                    if response.status == 200:
                        pass
            # response = requests.get(f'{self.webhook_url}{item["id"]}')
            # if response.status_code == 200:
            #     pass
        except Exception as e:
            spider.logger.error(f"Webhook Error: {e}")
        return item


class TelegraphPipeline:
    def __init__(self, telegraph_token):
        # Инициализация Telegraph клиента
        self.telegraph = Telegraph(telegraph_token)

    @classmethod
    def from_crawler(cls, crawler):
        # Получаем Telegraph токен из настроек Scrapy (settings.py)
        telegraph_token = crawler.settings.get('TELEGRAPH_TOKEN')
        # Инициализация Telegraph клиента
        return cls(telegraph_token)


    def process_item(self, item, spider):
        try:
            html = '{}<p>Источник: <a href="{}">{}</a></p>'.format(
                item['html'], item['url'], item['url']
            )
            response = self.telegraph.create_page(
                title=item['title'],
                html_content=html,
            )
            item['telegraph_url'] = 'https://telegra.ph/' + response['path']
            spider.logger.info(
                f"Publish Telegraph successful: "
                f"{item['telegraph_url']}"
            )
        except Exception as e:
            spider.logger.error(f"Error publish to Telegraph: {e}")
            raise DropItem(f"Error publish to Telegraph: {item['title']}")
        return item


class DatabasePipeline:
    def __init__(self, db_url):
        # Подключение к базе данных
        self.engine = create_engine(db_url)
        # Создание таблиц, если их нет
        create_tables(self.engine)
        # Создание фабрики сессий для взаимодействия с базой данных
        self.Session = sessionmaker(bind=self.engine)

    @classmethod
    def from_crawler(cls, crawler):
        # Получаем строку подключения из настроек Scrapy (settings.py)
        db_url = crawler.settings.get('DATABASE_URL')
        return cls(db_url)

    def open_spider(self, spider):
        # Открываем сессию при запуске паука
        self.session = self.Session()

    def close_spider(self, spider):
        # Закрываем сессию после завершения паука
        self.session.close()

    def process_item(self, item, spider):
        # Проверка на наличие необходимых полей
        if not all([item.get('url'), item.get('job_id'), item.get('title'),
                    item.get('text'), item.get('html')]):
            raise DropItem(f"Missing required fields in {item}")

        url = item.get('url')

        # Попытка найти существующий элемент по job_id
        db_item = self.session.query(Item).filter_by(url=url).first()

        if db_item:
            item['id'] = db_item.id

            # Обновление существующей записи
            db_item.job_id = item.get('job_id')
            db_item.title = item.get('title')
            db_item.text = item.get('text')
            db_item.html = item.get('html')
            db_item.telegraph_url = item.get('telegraph_url')
            db_item.tags = item.get('tags')
            db_item.status = 'DONE'

            self.session.add(db_item)
            self.session.commit()  # Сохраняем изменения в базе данных
        else:
            # Если элемент не найден, можно добавить логику для обработки
            spider.logger.warning(
                f"Item with url \'{url}\' not found in the database.")
        return item