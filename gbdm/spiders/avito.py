from typing import List, Dict
import scrapy
from scrapy.loader import ItemLoader
from gbdm.items import AvitoItem


class AvitoSpider(scrapy.Spider):
    name = 'avito'
    allowed_domains = ['www.avito.ru']
    start_urls = ['https://www.avito.ru/novorossiysk/kvartiry/prodam']

    __xpath_query = {
        'pagination': '//div[@class="index-content-2lnSO"]//'
                      'div[contains(@data-marker, "pagination-button")]/'
                      'span[@class="pagination-item-1WyVp"]/@data-marker',

        'ads': '//h3[@class="snippet-title"]/a[@class="snippet-link"][@itemprop="url"]/@href',

        'title': '//h1[@class="title-info-title"]/span[@itemprop="name"]/text()',

        'images': '//div[contains(@class, "gallery-imgs-container")]'
                  '/div[contains(@class, "gallery-img-wrapper")]'
                  '/div[contains(@class, "gallery-img-frame")]/@data-url',

        'prices': '//div[contains(@class, "price-value-prices-wrapper")]'
                  '/ul[contains(@class, "price-value-prices-list")]'
                  '/li[contains(@class, "price-value-prices-list-item_size-normal")]',

        'address': '//div[@itemprop="address"]/span/text()',

        'params': '//div[@class="item-params"]/ul[@class="item-params-list"]/li[@class="item-params-list-item"]'

    }

    def parse(self, response, start=True):
        if start:
            pages_count = int(
                response.xpath(self.__xpath_query['pagination']).extract()[-1].split('(')[-1].replace(')', ''))

            for num in range(2, pages_count + 1):
                yield response.follow(
                    f'?p={num}',
                    callback=self.parse,
                    cb_kwargs={'start': False}
                )

        for link in response.xpath(self.__xpath_query['ads']):
            yield response.follow(
                link,
                callback=self.ads_parse

            )

    def ads_parse(self, response):

        item_loader = ItemLoader(AvitoItem(), response)
        for key, value in self.__xpath_query.items():
            if key in ('pagination', 'ads'):
                continue
            item_loader.add_xpath(key, value)
        item_loader.add_value('url', response.url)

        yield item_loader.load_item()
        # TODO ТУТ подключить MONGO и Сохранить
