import re
import json

from scrapy import Spider
from scrapy.crawler import CrawlerProcess
from telegraph import Telegraph

from ..items import NewsItem
from ..utils.html_cleaner import clean_html


class NationalSpider(Spider):
    name = "national_spider"
    allowed_domains = ["thenationalnews.com"]
    # start_urls = [
    #     'https://www.thenationalnews.com/business/economy/2024/09/12/hong-kong-in-talks-with-uae-and-saudi-sovereign-wealth-funds-for-asia-investments/'
    # ]

    def __init__(self, url: str = None, *args, **kwargs):
        super(NationalSpider, self).__init__(*args, **kwargs)
        self.start_urls = [url] if url else []

    def parse(self, response):
        item = NewsItem()
        item['url'] = response.url
        item['job_id'] = self._job

        # Получаем заголовок статьи
        item['title'] = response.xpath('//h1/text()').get()

        # Найти нужный тег <script> с id="fusion-metadata"
        script = response.xpath(
            '//script[@id="fusion-metadata"]/text()').get()

        # Используем регулярное выражение для поиска блока с window.Fusion
        data = re.search(
            r'Fusion\.globalContent=([\s\S]*?);Fusion\.',
            script, re.DOTALL)

        if data:
            # Преобразуем найденный блок текста в JSON
            json_data = json.loads(data.group(1))

            # Теперь у вас есть доступ к данным из Fusion.globalContent
            # Выведем, например, content_elements
            elements = json_data.get('content_elements', [])

            html = []
            for e in elements:
                if e['type'] == 'text':
                    html.append(f'<p>{e["content"]}</p>')
                elif e['type'] == 'header':
                    html.append(f'<h{e["level"]}>{e["content"]}</h{e["level"]}>')

            item['html'] = clean_html(
                ''.join(html),
                ['p', 'h2', 'h3', 'h4', 'i', 'b'],
                {'h2': 'h3'}
            )
            item['text'] = clean_html(item['html'])

        # self.log('Article data has been saved to article_data.txt')
        return item


# Настройка процесса для локального запуска
if __name__ == "__main__":
    process = CrawlerProcess()
    process.crawl(NationalSpider)
    process.start()