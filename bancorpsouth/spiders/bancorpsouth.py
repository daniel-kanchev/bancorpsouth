import scrapy
from scrapy.loader import ItemLoader
from itemloaders.processors import TakeFirst
from datetime import datetime
from bancorpsouth.items import Article


class bancorpsouthSpider(scrapy.Spider):
    name = 'bancorpsouth'
    start_urls = ['http://bancorpsouth.investorroom.com/press-releases']

    def parse(self, response):
        articles = response.xpath('//li[@class="wd_item"]')
        for article in articles:
            link = article.xpath('.//div[@class="wd_more"]/a/@href').get()
            date = " ".join(article.xpath('./div[@class="wd_date"]/*/text()').getall())

            yield response.follow(link, self.parse_article, cb_kwargs=dict(date=date))

        next_page = response.xpath('//a[@aria-label="Show next page"]/@href').get()
        if next_page:
            yield response.follow(next_page, self.parse)

    def parse_article(self, response, date):
        if 'pdf' in response.url:
            return

        item = ItemLoader(Article())
        item.default_output_processor = TakeFirst()

        title = response.xpath('//div[@class="wd_title wd_language_left"]/text()').get()
        if title:
            title = title.strip()

        content = response.xpath('//div[@class="wd_body wd_news_body"]//text()').getall()
        content = [text for text in content if text.strip() and '{' not in text]
        content = " ".join(content[5:]).strip()

        item.add_value('title', title)
        item.add_value('date', date)
        item.add_value('link', response.url)
        item.add_value('content', content)

        return item.load_item()
