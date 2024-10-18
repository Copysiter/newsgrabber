import re
import json
import logging
import scrapy
from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import CrawlSpider, Rule
from scrapy.crawler import CrawlerProcess
# from w3lib.html import remove_tags


py_log = logging.getLogger()


class NationalSpider(CrawlSpider):
    name = "national_ald"
    allowed_domains = ["thenationalnews.com"]
    start_urls = [
        "https://www.thenationalnews.com/business/economy/2024/09/13/"
        "malaysia-on-track-to-sign-trade-treaty-with-uae-by-end-of-year/"
    ]

    # rules = (Rule(LinkExtractor(allow=r"Items/"),
    #               callback="parse_item", follow=True),)

    def parse(self, response):
        py_log.info('-----------------------------------------------------------------------------');
        # Извлекаем заголовок из тега <h1>
        title = response.xpath('//h1/text()').get()
        logging.info(title)

        # Извлекаем содержимое тега <article>
        # article_html = response.xpath('//article').get()

        # Оставляем только <p> и заголовки (h1-h6)
        # allowed_tags = ['p', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6']
        # cleaned_article = remove_tags(article_html, which_ones=[tag for tag in allowed_tags if tag not in ['p', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6']])

        # pattern = re.compile(
        #     r"KBB\.Vehicle\.Pages\.PricingOverview\.Buyers\.setup\(.*?data: ({.*?}),\W+adPriceRanges",
        #     re.MULTILINE | re.DOTALL)
        data = response.xpath(
            "//script[contains(., '\"@type\": \"NewsArticle\",')]/text()").get()
        # json_data = json.load(data)
        # logging.info(json_data)

        result = {
            'title': title,
            'text': data
        }
        with open('article_data.txt', 'w', encoding='utf-8') as f:
            f.write(f"Title: {result['title']}\n\n")
            f.write(f"Text:\n{result['text']}\n")

        logging.debug(result)
        # Выводим результат в консоль
        # yield result

        # item = {}
        # item["title"] = response.xpath('//h1/@text').get()
        # print()
        # print(item["title"])
        # print()
        #item["domain_id"] = response.xpath('//input[@id="sid"]/@value').get()
        #item["name"] = response.xpath('//div[@id="name"]').get()
        #item["description"] = response.xpath('//div[@id="description"]').get()
        # return item


# Настройка процесса для локального запуска
if __name__ == "__main__":
    process = CrawlerProcess()
    process.crawl(NationalSpider)
    process.start()