"""
Источник habr.ru
задача обойти ленту статей (лучшее за сутки)
извлеч данные
заголовок
url статьи
имя автора
ссылка на автора
список тегов ( имя тега и url)
список хабов (имя и url)
спроектировать sql базу данных таким образом что-бы данные о тегах хабах и авторах были атомарны,
и не дублировались в БД
"""

import random
import asyncio

import re
import requests
import aiohttp
from bs4 import BeautifulSoup
from pymongo import MongoClient

from habro_db import HabroDB
from habro_models import Writer, Tag, Post


class HabrParser:
    domain = 'https://habr.com'
    start_url = 'https://habr.com/ru/top/'
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_6) "
                      "AppleWebKit/605.1.15 "
                      "(KHTML, like Gecko) Version/13.1.2 Safari/605.1.15"
    }

    def __init__(self, db):
        self.db: HabroDB = db
        self.timeout = aiohttp.ClientTimeout(total=120.0)

    async def request(self, url) -> BeautifulSoup:
        while True:
            # с таймингом можно играть, но вас забанят сразу если убрать этот sleep()
            await asyncio.sleep(random.randint(1, 2) / random.randint(2, 4))
            try:
                async with aiohttp.ClientSession(timeout=self.timeout) as session:
                    async with session.get(url, headers=self.headers) as response:
                        if response.status == 200:
                            soap = BeautifulSoup(await response.text(), 'lxml')
                            break
                        elif response.status >= 500:
                            await asyncio.sleep(1.3)
                            continue
            except aiohttp.ServerDisconnectedError:
                await asyncio.sleep(0.3)
                continue
            except aiohttp.ClientPayloadError:
                await asyncio.sleep(0.3)
                continue
        return soap

    async def parse(self, url=start_url):
        while url:
            soap = await self.request(url)
            url = self.get_next_page(soap)
            await asyncio.wait([self.posts_parse(url) for url in self.search_post_links(soap)])

    async def posts_parse(self, url):
        soap = await self.request(url)
        await self.get_post_data(soap, url)

    def get_next_page(self, soap: BeautifulSoup) -> str:
        a = soap.find('a', attrs={'id': 'next_page'})
        return f'{self.domain}{a.get("href")}' if a and a.get("href") else None

    def search_post_links(self, soap: BeautifulSoup):
        posts_list = soap.find('div', attrs={'class': 'posts_list'})
        posts_a = posts_list.find_all('a', attrs={'class': 'post__title_link'})
        return {f'{itm.get("href")}' for itm in posts_a}

    # todo Извлечение данных из страницы материала
    async def get_post_data(self, soap: BeautifulSoup, url: str):
        result = {'url': url,
                  'title': soap.find('span', attrs={'class': 'post__title-text'}).text,
                  'writer': await self.get_writer(soap),
                  'tags': self.get_tags(soap)
                  }
        print(1)
        self.db.add_post(Post(**result))
        # await self.save_to_mongo(result)

    async def get_writer(self, soap: BeautifulSoup):
        author_block = soap.find('div', attrs={'class': 'author-panel'})
        user_info = author_block.find('div', attrs={'class': 'user-info'})
        writer_soap = await self.request(user_info.find('a').get('href'))
        writer = {
            'name': writer_soap.find('h1').find('a').text,
            'url': user_info.find('a').get('href'),
            'username': user_info.get('data-user-login')
        }
        result = Writer(**writer)

        return result

    def get_tags(self, soap: BeautifulSoup):
        tag_list = soap.find('dl', attrs={'class': 'post__tags'}).find('ul').find_all('a', attrs={'class': 'post__tag'})
        return [Tag(name=itm.text, url=itm.get('href')) for itm in tag_list]

    def get_habs(self, soap: BeautifulSoup):
        pass


if __name__ == '__main__':
    db = HabroDB('sqlite:///habro_blog.db')
    parser = HabrParser(db)
    asyncio.run(parser.parse())
