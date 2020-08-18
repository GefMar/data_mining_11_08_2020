from typing import Dict
import asyncio

import re
import requests
import aiohttp
from bs4 import BeautifulSoup
from pymongo import MongoClient


class GbBlogParser:
    domain = 'https://geekbrains.ru'
    start_url = 'https://geekbrains.ru/posts'

    def __init__(self, mongo_collection):
        self.collection = mongo_collection
        self.timeout = aiohttp.ClientTimeout(total=60.0)

    async def parse(self, url=start_url):

        async with aiohttp.ClientSession(timeout=self.timeout) as session:
            while url:
                async with session.get(url) as response:
                    soap = BeautifulSoup(await response.text(), 'lxml')
                url = self.get_next_page(soap)
                await asyncio.create_task(self.posts_parse(soap))

    async def posts_parse(self, soap: BeautifulSoup):
        async with aiohttp.ClientSession(timeout=self.timeout) as session:
            links = self.search_post_links(soap)
            tasks = []
            async for url in links:
                async with session.get(url) as response:
                    soap = BeautifulSoup(await response.text(), 'lxml')
                tasks.append(self.get_post_data(soap))
            await asyncio.wait(tasks)

    def get_next_page(self, soap: BeautifulSoup) -> str:
        ul = soap.find('ul', attrs={'class': 'gb__pagination'})
        a = ul.find('a', text=re.compile('›'))
        return f'{self.domain}{a.get("href")}' if a and a.get("href") else None

    async def search_post_links(self, soap: BeautifulSoup):
        wrapper = soap.find('div', attrs={'class': "post-items-wrapper"})
        posts = wrapper.find_all('div', attrs={'class': 'post-item'})
        for itm in {f'{self.domain}{itm.find("a").get("href")}' for itm in posts}:
            yield itm

    # todo Извлечение данных из страницы материала
    async def get_post_data(self, soap: BeautifulSoup):
        result = {}
        result['title'] = soap.find('h1', attrs={'class': 'blogpost-title'}).text
        content = soap.find('div', attrs={'class': 'blogpost-content', 'itemprop': 'articleBody'})
        img = content.find('img')
        result['image'] = img.get('src') if img else None
        await self.save_to_mongo(result)

    async def save_to_mongo(self, data: dict):
        print(data)
        self.collection.insert_one(data)


if __name__ == '__main__':
    m_coll = MongoClient()['parse_gb_blog']['posts']
    parser = GbBlogParser(m_coll)
    asyncio.run(parser.parse())
