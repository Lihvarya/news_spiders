# -*- coding: utf-8 -*-
import scrapy
import json
import re
import time
from news.items import NewsItem

def generate_timestamp():
    return int(time.time() * 1000)

class SinaSpider(scrapy.Spider):
    name = 'sina_spider'
    allowed_domains = ['sina.com.cn', 'sina.com']
    # URLs for latest and hot news (JSONP)
    latest_china_news_url = "https://feed.sina.com.cn/api/roll/get"
    hot_news_url = "https://top.news.sina.com.cn/ws/GetTopDataList.php"

    custom_settings = {
        'DEFAULT_REQUEST_HEADERS': {
            'accept': '*/*',
            'accept-language': 'zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6',
            'cache-control': 'no-cache',
            'pragma': 'no-cache',
            'referer': 'https://news.sina.com.cn/china/',
            'sec-ch-ua': '"Not A(Brand";v="8", "Chromium";v="132", "Microsoft Edge";v="132"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"',
            'sec-fetch-dest': 'script',
            'sec-fetch-mode': 'no-cors',
            'sec-fetch-site': 'same-site',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/132.0.0.0 Safari/537.36 Edg/132.0.0.0',
        },
        # Cookies might be necessary, consider adding them if requests fail
        # 'COOKIES_ENABLED': True,
        # 'COOKIES_DEBUG': True, # For debugging
    }

    def start_requests(self):
        # Request latest china news
        latest_params = {
            'pageid': '121',
            'lid': '1356',       # Lid for China news
            'num': '20',         # Number of items
            'versionNumber': '1.2.4',
            'page': '1',
            'encode': 'utf-8',
            'callback': 'feedCardJsonpCallback', # JSONP callback function name
            '_': str(generate_timestamp()),
        }
        latest_url = f"{self.latest_china_news_url}?{'&'.join([f'{k}={v}' for k, v in latest_params.items()])}"
        yield scrapy.Request(latest_url, callback=self.parse_latest_news)

        # Request hot news
        # Note: 'top_time' might need dynamic date generation
        hot_params = {
            'callback': 'jQuery111_callback', # Generic callback name, adjust if needed
            'top_type': 'day', # Or 'week', 'month'
            'top_cat': 'news_china_suda', # Category for China hot news
            # 'top_time': '20250122', # Example date, might need current date
            'top_show_num': '20',
            'top_order': 'DESC',
            'short_title': '1',
            'js_var': 'hotNewsData', # Variable name in JSONP response
            '_': str(generate_timestamp()),
        }
        hot_url = f"{self.hot_news_url}?{'&'.join([f'{k}={v}' for k, v in hot_params.items()])}"
        yield scrapy.Request(hot_url, callback=self.parse_hot_news)

    def parse_latest_news(self, response):
        self.logger.info(f'Parsing latest news JSONP: {response.url}')
        # Extract JSON from the 'feedCardJsonpCallback(...)' wrapper
        jsonp_pattern = r"try\{feedCardJsonpCallback\((\{.*?\})\);\}catch\(e\)\{\};"
        match = re.search(jsonp_pattern, response.text, re.DOTALL)

        if match:
            try:
                json_str = match.group(1)
                data = json.loads(json_str)
                news_list = data.get('result', {}).get('data', [])
                self.logger.info(f'Found {len(news_list)} items in latest news.')
                for news_item_data in news_list:
                    url = news_item_data.get('url')
                    title = news_item_data.get('title')
                    if url and title:
                        yield scrapy.Request(url, callback=self.parse_news_detail, meta={'title_from_list': title})
                    else:
                        self.logger.warning(f'Missing url or title in latest news item: {news_item_data}')
            except json.JSONDecodeError as e:
                self.logger.error(f"JSON parsing failed for {response.url}: {e}")
            except Exception as e:
                self.logger.error(f"Error processing latest news {response.url}: {e}")
        else:
            self.logger.error(f"Could not extract JSON data from {response.url}")

    def parse_hot_news(self, response):
        self.logger.info(f'Parsing hot news JSONP: {response.url}')
        # Extract JSON from the 'var hotNewsData = {...};' wrapper
        jsonp_pattern = r"var\s+hotNewsData\s*=\s*(\{.*?\});"
        match = re.search(jsonp_pattern, response.text, re.DOTALL)

        if match:
            try:
                json_str = match.group(1)
                data = json.loads(json_str)
                news_list = data.get('data', [])
                self.logger.info(f'Found {len(news_list)} items in hot news.')
                for news_item_data in news_list:
                    url = news_item_data.get('url')
                    title = news_item_data.get('title')
                    if url and title:
                        yield scrapy.Request(url, callback=self.parse_news_detail, meta={'title_from_list': title})
                    else:
                        self.logger.warning(f'Missing url or title in hot news item: {news_item_data}')
            except json.JSONDecodeError as e:
                self.logger.error(f"JSON parsing failed for {response.url}: {e}")
            except Exception as e:
                self.logger.error(f"Error processing hot news {response.url}: {e}")
        else:
            self.logger.error(f"Could not extract JSON data from {response.url}")

    def parse_news_detail(self, response):
        self.logger.info(f'Parsing news detail: {response.url}')
        item = NewsItem()
        title_from_list = response.meta.get('title_from_list')

        # --- Placeholder Selectors for Detail Page --- 
        # **ADJUST THESE BASED ON ACTUAL SINA NEWS PAGE STRUCTURE**
        # Sina pages can vary (e.g., news.sina.com.cn, k.sina.com.cn, finance.sina.com.cn)

        # Extract Title
        title = response.css('h1.main-title::text').get() or \
                response.css('h1.title::text').get() or \
                response.css('.art_tit_h1::text').get() or \
                response.css('meta[property="og:title"]::attr(content)').get() or \
                title_from_list
        item['title'] = title.strip() if title else None

        # Extract Author
        author = response.css('.source-author .author::text').get() or \
                 response.css('meta[name="author"]::attr(content)').get()
        item['author'] = author.strip() if author else None

        # Extract Publish Time
        publish_time = response.css('.date::text').get() or \
                       response.css('.time-source span::text').get() or \
                       response.css('#pub_date::text').get() or \
                       response.css('.art_time::text').get() or \
                       response.css('meta[property="article:published_time"]::attr(content)').get()
        item['publish_time'] = publish_time.strip() if publish_time else None

        # Extract Summary/Description
        summary = response.css('meta[name="description"]::attr(content)').get() or \
                  response.css('.article-summary p::text').get() or \
                  response.css('#article p::text').get() # First paragraph as fallback
        item['summary'] = summary.strip() if summary else None

        # 强制设置来源为爬虫名称
        item['source'] = self.name

        # Link
        item['link'] = response.url

        # --- End Placeholder Selectors ---

        if item['title'] and item['link']:
            self.logger.debug(f'Yielding item: {item["title"]}')
            yield item
        else:
            self.logger.warning(f'Failed to extract essential data (title/link) from {response.url}')