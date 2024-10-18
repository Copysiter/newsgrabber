# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
# from itemadapter import ItemAdapter
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from scrapy.exceptions import DropItem

from .models import Item, create_tables


class NewsPipeline:
    def process_item(self, item, spider):
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

        # Создаем объект статьи из item
        article = Item(
            url=item['url'],
            job_id=item['job_id'],
            title=item['title'],
            text=item['text'],
            html=item['html'],
            tags=item.get('tags'),
            telegraph_url=item.get('telegraph_url'),
        )

        # Добавляем и сохраняем объект в базе данных
        self.session.add(article)
        self.session.commit()

        return item