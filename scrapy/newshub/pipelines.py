# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter

from telegraph import Telegraph

from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine

from scrapy.exceptions import DropItem

from .models import Item, create_tables


class TelegraphPipeline:
    def __init__(self):
        self.telegraph = Telegraph(
            '8af84c97c56d3994a35618dee4d5a20c51a395a6b16dfa885d5e5fed936b'
        )
        # self.telegraph.create_account(short_name='ScrapyNews')

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
                f"Успешная публикации статьи в Telegraph: "
                f"{item['telegraph_url']}"
            )
        except Exception as e:
            spider.logger.error(f"Ошибка при публикации в Telegraph: {e}")
            raise DropItem(f"Не удалось опубликовать статью: {item['title']}")
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
            # Если элемент не найден, можно добавить логику для обработки, например, логировать
            spider.logger.warning(
                f"Item with url \'{url}\' not found in the database.")

        '''
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
        try:
            self.session.add(article)
            self.session.commit()
        except Exception as e:
            spider.logger.error(f"Ошибка при сохранении в БД: {e}")
            self.session.rollback()
            raise DropItem(f"Не удалось сохранить статью: {item['title']}")
        '''
        return item