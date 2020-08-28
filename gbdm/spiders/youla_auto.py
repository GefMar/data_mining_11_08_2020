import scrapy
from ..loaders import YoulaAutoLoader, YoulaAutoAdsLoader


class YoulaAutoSpider(scrapy.Spider):
    name = 'youla_auto'
    allowed_domains = ['auto.youla.ru']
    start_urls = ['https://auto.youla.ru/cars/used/bmw/']
    __row_xpath = {
        'ads': '//article[@data-target="serp-snippet"]//a[@data-target="serp-snippet-title"]/@href',
        'pagination': '//div[contains(@class, "Paginator_block")]/a[@data-target="button-link"]/@href'
    }

    __ads_xpath = {
        'author_url': '/html/body/script[contains(text(), "window.transitState = decodeURIComponent")]/text()',

        'title': '//div[contains(@class, "AdvertCard_pageContent")]'
                 '//div[contains(@class, "AdvertCard_advertTitle")]/text()',

        'images': '//div[contains(@class, "AdvertCard_pageContent")]'
                  '//div[contains(@class, "PhotoGallery_photoWrapper")]//picture/source/@srcset',
        # 'specifications': '',
        # 'descriptions': '',
    }

    def parse(self, response, **kwargs):
        loader = YoulaAutoLoader(response=response)
        for name, selector in self.__row_xpath.items():
            loader.add_xpath(name, selector)
        # item = loader.load_item()

        # for field in item:
        #     for url in item[field]:
        #         yield response.follow(url, callback=self.parse)

        for url in loader._values['pagination']:
            yield response.follow(url, callback=self.parse)
        for url in loader._values['ads']:
            yield response.follow(url, callback=self.ads_parse)

    def ads_parse(self, response):
        loader = YoulaAutoAdsLoader(response=response)
        loader.add_value('url', response.url)
        for name, selector in self.__ads_xpath.items():
            loader.add_xpath(name, selector)
        yield loader.load_item()
