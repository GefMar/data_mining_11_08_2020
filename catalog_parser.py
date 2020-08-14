from typing import List, Dict
import datetime as dt
import os
from pathlib import Path
import json

import requests


class Catalog5Ka:
    __urls = {
        'categories': 'https://5ka.ru/api/v2/categories/',
        'products': 'https://5ka.ru/api/v2/special_offers/'
    }

    __params = {
        'records_per_page': 50,
        'categories': '',
    }

    __headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:78.0) Gecko/20100101 Firefox/78.0",
    }

    __replaces = (',', '-', '/', '\\', '.', '"', "'", '*', '#',)

    def __init__(self, folder_name='data'):
        self.category = self.__get_categories()
        self.folder_data = Path(os.path.dirname(__file__)).join(folder_name)

    def __get_categories(self) -> List[Dict[str, str]]:
        response = requests.get(self.__urls['categories'])
        return response.json()

    def parse(self):
        for category in self.category:
            self.get_products(category)

    def get_products(self, category=None):
        url = self.__urls['products']
        params = self.__params
        params['categories'] = category['parent_group_code']

        while url:
            response = requests.get(url, params=params, headers=self.__headers)
            data = response.json()
            url = data['next']
            params = {}

            if category.get('products'):
                category['products'].extend(data['results'])
            else:
                category['products'] = data['results']
        category['parse_date'] = dt.datetime.now().timestamp()

    def save_to_file(self, category):
        name = category['parent_group_name']
        for itm in self.__replaces:
            name = name.replace(itm, '')
        name = '_'.join(name.split()).lower()

        file_path = os.path.join(self.folder_data, f'{name}.json')

        with open(file_path, 'w', encoding='UTF-8') as file:
            json.dump(category, file, ensure_ascii=False)


if __name__ == '__main__':
    parser = Catalog5Ka()
    parser.parse()
    print(1)
