# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy
from scrapy.loader.processors import MapCompose, TakeFirst
from scrapy import Selector


def validate_photo(value):
    if value[:2] == '//':
        return f'https:{value}'
    return value


def get_prices(value):
    tag = Selector(text=value)
    result = {'name': tag.xpath('.//span//text()').extract_first(),
              'value': tag.xpath('//text()').extract_first().split()
              }
    result['value'] = float(''.join(result['value']))
    return result


def get_params(value):
    param_tag = Selector(text=value)
    key = param_tag.xpath('.//span[@class="item-params-label"]/text()').extract_first().split(':')[0]

    value = ' '.join(
        [itm for itm in param_tag.xpath('//li/text()').extract()
         if not itm.isspace()]
    )

    return key, value


class AvitoItem(scrapy.Item):
    _id = scrapy.Field()
    title = scrapy.Field(output_processor=TakeFirst())
    url = scrapy.Field(output_processor=TakeFirst())
    images = scrapy.Field(input_processor=MapCompose(validate_photo))
    prices = scrapy.Field(input_processor=MapCompose(get_prices))
    address = scrapy.Field(output_processor=TakeFirst())
    params = scrapy.Field(output_processor=lambda x: dict(get_params(itm) for itm in x))


class YoulaAutoItem(scrapy.Item):
    _id = scrapy.Field()
    pagination = scrapy.Field()
    ads = scrapy.Field()


class YoulaAdsAutoItem(scrapy.Item):
    _id = scrapy.Field()
    title = scrapy.Field()
    url = scrapy.Field()
    images = scrapy.Field()
    specifications = scrapy.Field()
    descriptions = scrapy.Field()
    author_url = scrapy.Field()
