# -*- coding: utf-8 -*-
import scrapy
import json
from news.items import NewsItem
from urllib.parse import urlencode

class WeiboSpider(scrapy.Spider):
    name = 'weibo_spider'
    allowed_domains = ['m.weibo.cn', 'weibo.cn'] # Mobile domain for API
    # API endpoint for hot search
    hot_search_url = "https://m.weibo.cn/api/container/getIndex"

    custom_settings = {
        'DEFAULT_REQUEST_HEADERS': {
            'accept': 'application/json, text/plain, */*',
            'accept-language': 'zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6',
            'cache-control': 'no-cache',
            'mweibo-pwa': '1',
            'pragma': 'no-cache',
            'priority': 'u=1, i',
            'referer': 'https://m.weibo.cn/p/index?containerid=106003type%3D25%26t%3D3%26disable_hot%3D1%26filter_type%3Drealtimehot', # Referer from original handler
            'sec-ch-ua': '"Microsoft Edge";v="135", "Not-A.Brand";v="8", "Chromium";v="135"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"',
            'sec-fetch-dest': 'empty',
            'sec-fetch-mode': 'cors',
            'sec-fetch-site': 'same-origin',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36 Edg/135.0.0.0',
            'x-requested-with': 'XMLHttpRequest',
            # 'x-xsrf-token': 'fecb39', # XSRF token might be dynamic, handle if needed
        },
        'COOKIES_ENABLED': True,
        # Cookies from the original handler, might need refreshing or dynamic handling
        'COOKIES': {
            # '_T_WM': '28666720942',
            # 'XSRF-TOKEN': 'fecb39',
            # 'WEIBOCN_FROM': '1110006030',
            # 'MLOGIN': '0',
            # 'M_WEIBOCN_PARAMS': 'luicode%3D20000061%26lfid%3D5070140584495876%26fid%3D106003type%253D25%2526t%253D3%2526disable_hot%253D1%2526filter_type%253Drealtimehot%26uicode%3D10000011',
            # 'mweibo_short_token': 'f5feecf312',
        }
    }

    def start_requests(self):
        # Parameters for the hot search API
        params = {
            'containerid': '106003type=25&t=3&disable_hot=1&filter_type=realtimehot',
            # 'luicode': '20000061', # Optional?
            # 'lfid': '5070140584495876', # Optional?
        }
        url = f"{self.hot_search_url}?{urlencode(params)}"
        yield scrapy.Request(url, callback=self.parse_hot_search)

    def parse_hot_search(self, response):
        self.logger.info(f'Parsing Weibo hot search API response: {response.url}')
        try:
            json_data = json.loads(response.text)
            # Navigate through the nested structure to get the list
            card_group = []
            cards = json_data.get('data', {}).get('cards', [])
            if cards and isinstance(cards, list) and cards[0].get('card_group') and isinstance(cards[0]['card_group'], list):
                card_group = cards[0]['card_group']
            else:
                self.logger.warning(f'Could not find card_group in the expected structure. Response: {response.text}')
                return

            self.logger.info(f'Found {len(card_group)} items in Weibo hot search.')
            count = 0
            for item_data in card_group:
                if not isinstance(item_data, dict):
                    self.logger.warning(f'Skipping invalid item in list (not a dict): {item_data}')
                    continue

                desc = item_data.get('desc') # Title of the hot topic
                scheme = item_data.get('scheme') # URL (often internal m.weibo.cn link)

                if desc and scheme:
                    item = NewsItem()
                    item['title'] = desc
                    item['link'] = scheme # Use the scheme directly as the link
                    item['source'] = self.name
                    # Other fields like summary, author, publish_time are usually not applicable here
                    item['summary'] = item_data.get('desc_extr', None) # Sometimes extra description is here

                    yield item
                    count += 1
                else:
                    self.logger.warning(f'Missing desc or scheme in hot search item: {item_data}')
            self.logger.info(f'Successfully yielded {count} items from Weibo hot search.')

        except json.JSONDecodeError as e:
            self.logger.error(f"JSON parsing failed for {response.url}: {e}. Response text: {response.text}")
        except Exception as e:
            self.logger.error(f"Error processing Weibo hot search list {response.url}: {e}")