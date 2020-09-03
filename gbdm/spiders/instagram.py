import json
import scrapy
from scrapy.http.response import Response
from gbdm.items import InstaHashTagItem, InstaPostItem, InstaUserItem


class InstagramSpider(scrapy.Spider):
    name = 'instagram'
    allowed_domains = ['www.instagram.com']
    start_urls = ['https://www.instagram.com/']

    __login_url = 'https://www.instagram.com/accounts/login/ajax/'
    __tag_url = '/explore/tags/наука/'

    __api_tag_url = '/graphql/query/'
    __query_hash = '9b498c08113f1e09617a1703c22b2f32'

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
        hashtag: dict = js_data['entry_data']['TagPage'][0]['graphql']['hashtag']

        #todo блок дублируется, и его надо бы вынести в метод
        if hashtag['edge_hashtag_to_media']['page_info']['has_next_page']:
            variables = {"tag_name": hashtag['name'],
                         "first": 50,
                         "after": hashtag['edge_hashtag_to_media']['page_info']['end_cursor']}

            url = f'{self.__api_tag_url}?query_hash={self.__query_hash}&variables={json.dumps(variables, ensure_ascii=False)}'
            yield response.follow(url, callback=self.get_api_hastag_posts)

        hashtag['posts_count'] = hashtag['edge_hashtag_to_media']['count']
        posts: list = hashtag.pop('edge_hashtag_to_media')['edges']

        yield InstaHashTagItem(data=hashtag)

        for post in posts:
            yield InstaPostItem(data=post['node'])
            if post['node']['edge_media_to_comment']['count'] > 30 or post['node']['edge_liked_by']['count'] > 100:
                yield response.follow(f'/p/{post["node"]["shortcode"]}/',
                                      callback=self.post_page_parse)

    def post_page_parse(self, response):
        data = self.get_js_shared_data(response)
        yield InstaUserItem(data=data['entry_data']['PostPage'][0]['graphql']['shortcode_media']['owner'])

    def get_api_hastag_posts(self, response: Response):
        hashtag = response.json()['data']['hashtag']
        if hashtag['edge_hashtag_to_media']['page_info']['has_next_page']:
            variables = {"tag_name": hashtag['name'],
                         "first": 50,
                         "after": hashtag['edge_hashtag_to_media']['page_info']['end_cursor']}

            url = f'{self.__api_tag_url}?query_hash={self.__query_hash}&variables={json.dumps(variables, ensure_ascii=False)}'
            yield response.follow(url, callback=self.get_api_hastag_posts)
        posts: list = hashtag['edge_hashtag_to_media']['edges']

        for post in posts:
            yield InstaPostItem(data=post['node'])
            if post['node']['edge_media_to_comment']['count'] > 30 or post['node']['edge_liked_by']['count'] > 100:
                yield response.follow(f'/p/{post["node"]["shortcode"]}/',
                                      callback=self.post_page_parse)

    @staticmethod
    def get_js_shared_data(response):
        marker = "window._sharedData = "
        data = response.xpath(
            f'/html/body/script[@type="text/javascript" and contains(text(), "{marker}")]/text()'
        ).extract_first()
        data = data.replace(marker, '')[:-1]
        return json.loads(data)
