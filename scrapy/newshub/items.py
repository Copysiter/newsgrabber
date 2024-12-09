# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class NewshubItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    pass

class NewsItem(scrapy.Item):
    # ID статьи
    id = scrapy.Field()

    # URL статьи
    url = scrapy.Field()

    # Заголовок статьи
    title = scrapy.Field()

    # Текст статьи (без HTML)
    text = scrapy.Field()

    # Полный HTML-контент статьи
    html = scrapy.Field()

    # URL публикации на Telegraph (заполняется после публикации)
    telegraph_url = scrapy.Field()

    # Теги статьи
    tags = scrapy.Field()

    # ID задания парсинга (Scrapy Job ID)
    job_id = scrapy.Field()
