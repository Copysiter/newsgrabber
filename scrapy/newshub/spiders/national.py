import re
import json

from fake_useragent import UserAgent

from scrapy import Spider, Request
from scrapy.crawler import CrawlerProcess

from ..items import NewsItem
from ..utils.html_cleaner import clean_html

from ..settings import OPENAI_MAX_TOKENS


class NationalSpider(Spider):
    name = "national_spider"
    allowed_domains = ["thenationalnews.com"]
    ua = UserAgent()

    def __init__(self, url: str = None, *args, **kwargs):
        super(NationalSpider, self).__init__(*args, **kwargs)
        self.start_urls = [url] if url else []

    def start_requests(self):
        for url in self.start_urls:
            yield Request(
                url=url,
                # meta={'proxy': 'http://tcytqdjj:gs1dm8etd6yo@94.154.170.243:6165'},
                headers={
                    'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9;v=b3;q=0.7',
                    'accept-language': 'ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7',
                    'cache-control': 'no-cache',
                    'pragma': 'no-cache',
                    'priority': 'u=0, i',
                    # 'sec-ch-ua': '"Google Chrome";v="131", "Chromium";v="131", "Not_A Brand";v="24"',
                    # 'sec-ch-ua-mobile': '?0',
                    # 'sec-ch-ua-platform': '"macOS"',
                    # 'sec-fetch-dest': 'document',
                    # 'sec-fetch-mode': 'navigate',
                    # 'sec-fetch-site': 'same-origin',
                    # 'sec-fetch-user': '?1',
                    'upgrade-insecure-requests': '1',
                    'user-agent': self.ua.random
                },
                callback=self.parse
            )

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

        self.log(OPENAI_MAX_TOKENS)
        return item


# Настройка процесса для локального запуска
if __name__ == "__main__":
    process = CrawlerProcess()
    process.crawl(NationalSpider)
    process.start()