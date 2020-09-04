import time
import scrapy
from selenium.common.exceptions import NoSuchElementException
from selenium import webdriver
from selenium.webdriver.common.keys import Keys


class ZillowSpider(scrapy.Spider):
    name = 'zillow'
    allowed_domains = ['www.zillow.com']
    start_urls = ['https://www.zillow.com/homes/for_sale/California,-MD_rb/']
    browser = webdriver.Firefox()
    __xpath = {
        'pagination': '//div[@class="search-pagination"]'
                      '/nav[@role="navigation"]'
                      '/ul[contains(@class, "PaginationList")]'
                      '/li[contains(@class, "PaginationJumpItem")]'
                      '/a/@href',

        'adv': '//div[@id="grid-search-results"]/ul[contains(@class, "photo-cards")]/li//a[@class="list-card-link"]',
        'images_source': '//ul[@class="media-stream"]'
                         '/li[contains(@class, "media-stream-tile")]'
                         '//picture/source[@type="image/jpeg"]',
        'images_li': '//ul[@class="media-stream"]/li[contains(@class, "media-stream-tile")]',
    }

    def parse(self, response):
        for pag_page in response.xpath(self.__xpath['pagination']):
            yield response.follow(pag_page, callback=self.parse)

        for adv_url in response.xpath(self.__xpath['adv']):
            yield response.follow(adv_url, callback=self.adv_parse)


    def adv_parse(self, response):
        self.browser.get(response.url)
        images_len = len(self.browser.find_elements_by_xpath(self.__xpath['images_source']))

        media_coll = self.browser.find_element_by_xpath('//div[contains(@class, "ds-media-col")]')
        while True:
            for _ in range(10):
                media_coll.send_keys(Keys.PAGE_DOWN)
            time.sleep(0.2)

            tmp_len = len(self.browser.find_elements_by_xpath(self.__xpath['images_source']))
            if tmp_len == images_len:
                break
            images_len = tmp_len

        print(1)
