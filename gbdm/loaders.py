import re
from itemloaders.processors import TakeFirst, MapCompose, Join
from scrapy.loader import ItemLoader

from .items import YoulaAutoItem, YoulaAdsAutoItem


def search_author_id(itm):
    re_str = re.compile(r'youlaId%22%2C%22([0-9|a-zA-Z]+)%22%2C%22avatar')
    result = re.findall(re_str, itm)
    return result


def create_user_url(itm):
    base_url = "https://youla.ru/user/"
    result = base_url + itm
    return result


def clear_photo(itm):
    result = dict(reversed(line.split()) for line in itm.split(','))
    return result.get('2x') or result.get('1x')


class YoulaAutoLoader(ItemLoader):
    default_item_class = YoulaAutoItem


class YoulaAutoAdsLoader(ItemLoader):
    default_item_class = YoulaAdsAutoItem
    url_out = TakeFirst()
    author_url_in = MapCompose(search_author_id, create_user_url)
    author_url_out = TakeFirst()
    images_in = MapCompose(clear_photo)

