from fake_useragent import UserAgent
from bs4 import BeautifulSoup

from scrapy import Spider, Request
from scrapy.crawler import CrawlerProcess

from ..items import NewsItem
from ..utils.html_cleaner import clean_html


class SemaforSpider(Spider):
    name = "semafor_spider"
    allowed_domains = ["semafor.com"]
    ua = UserAgent()

    def __init__(self, url: str = None, *args, **kwargs):
        super(SemaforSpider, self).__init__(*args, **kwargs)
        self.start_urls = [url] if url else []

    def start_requests(self):
        for url in self.start_urls:
            yield Request(
                url=url,
                # meta={'proxy': 'http://tcytqdjj:gs1dm8etd6yo@94.154.170.243:6165'},
                headers={
                    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                    'Sec-Fetch-Site': 'none',
                    'Accept-Encoding': 'gzip, deflate, br',
                    'Sec-Fetch-Mode': 'navigate',
                    'Host': 'www.semafor.com',
                    'User-Agent': self.ua.random,
                    'Accept-Language': 'en',
                    'Sec-Fetch-Dest': 'document',
                    'Connection': 'keep-alive',
                },
                callback=self.parse
            )

    def parse(self, response):
        item = NewsItem()
        item['url'] = response.url
        item['job_id'] = self._job

        # Получаем заголовок статьи с помощью XPath
        item['title'] = (response.xpath(
            '//main//h1[contains(@class, "suppress-rss")]/text()'
        ).get() or '').strip()

        # Извлечение HTML содержимого статьи
        html = response.xpath(
            '//main//div[contains(@class, "article-content")]'
        ).get()

        # Создаем объект BeautifulSoup
        soup = BeautifulSoup(html, 'html.parser')

        # Удаляем элементы с атрибутом data-testid="body-ad-post-message"
        for tag in soup.find_all(attrs={"data-testid": "ad-body"}):
            tag.decompose()

        # Удаляем элементы, у которых class начинается с "styles_indexMenu_"
        for tag in soup.find_all(class_=lambda c: c and c.startswith("styles_indexMenu_")):
            tag.decompose()

        html = str(soup)

        # Очистка HTML, оставляя только определенные теги и заменяя <h2> на <h3>
        item['html'] = clean_html(
            ''.join(html),
            ['p', 'h2', 'h3', 'h4', 'i', 'b'],
            {'h2': 'h3'}
        )

        # Извлечение чистого текста из очищенного HTML
        item['text'] = clean_html(item['html'])
        return item


if __name__ == "__main__":
    process = CrawlerProcess()
    process.crawl(SemaforSpider)
    process.start()
