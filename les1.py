import requests
import time


class Parser5ka:
    _domain = 'https://5ka.ru'
    _api_path = '/api/v2/special_offers/'
    params = {
        'records_per_page': 20,
    }
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:78.0) Gecko/20100101 Firefox/78.0",
    }

    def __init__(self):
        self.products = []

    def download(self):
        params = self.params
        url = self._domain + self._api_path

        while url:
            response = requests.get(url, headers=self.headers, params=params)
            # todo сделать проверку что прилетел json
            data = response.json()
            params = {}
            url = data['next']
            self.products.extend(data['results'])
            time.sleep(0.1)


if __name__ == '__main__':
    parser = Parser5ka()
    parser.download()
    print(1)
