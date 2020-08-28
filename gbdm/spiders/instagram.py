import json
import scrapy
from scrapy.http.response import Response


class InstagramSpider(scrapy.Spider):
    name = 'instagram'
    allowed_domains = ['www.instagram.com']
    start_urls = ['https://www.instagram.com/']

    __login_url = 'https://www.instagram.com/accounts/login/ajax/'
    __tag_url = '/explore/tags/наука/'

    __api_tag_url = '/graphql/query/'
    __query_hash = 'c769cb6c71b24c8a86590b22402fda50'

    def __init__(self, *args, **kwargs):
        self.__login = kwargs['login']
        self.__password = kwargs['password']
        super().__init__(*args, **kwargs)

    def parse(self, response: Response, **kwargs):
        try:
            js_data = self.get_js_shared_data(response)

            yield scrapy.FormRequest(self.__login_url,
                                     method='POST',
                                     callback=self.parse,
                                     formdata={
                                         'username': self.__login,
                                         'enc_password': self.__password
                                     },
                                     headers={'X-CSRFToken': js_data['config']['csrf_token']}
                                     )
        except AttributeError as e:
            if response.json().get('authenticated'):
                yield response.follow(self.__tag_url, callback=self.tag_page_parse)

    def tag_page_parse(self, response: Response):
        js_data = self.get_js_shared_data(response)
        hashtag = js_data['entry_data']['TagPage'][0]['graphql']['hashtag']
        variables = {"tag_name": hashtag['name'],
                     "first": 50,
                     "after": hashtag['edge_hashtag_to_media']['page_info']['end_cursor']}

        """https://www.instagram.com/graphql/query/?query_hash=c769cb6c71b24c8a86590b22402fda50&variables={"tag_name":"наука","first":12,"after":"QVFCRTNVSFM1WVFSSFVma3NHTmpNRUNJQ1ZxTTdYcTNieDBnUDJHcFdwVUdYdjBYNi1CdG1aeEdFckNtWjQwMThUZkE4QzdwSVVWTWU1NjAyenVhWnA0LQ=="}"""

        url = f'{self.__api_tag_url}?query_hash={self.__query_hash}&variables={json.dumps(variables)}'
        yield response.follow(url, callback=self.get_api_hastag_posts)

        print(1)

    def get_api_hastag_posts(self, response: Response):
        print(1)

    @staticmethod
    def get_js_shared_data(response):
        marker = "window._sharedData = "
        data = response.xpath(
            f'/html/body/script[@type="text/javascript" and contains(text(), "{marker}")]/text()'
        ).extract_first()
        data = data.replace(marker, '')[:-1]
        return json.loads(data)
