# -*- coding: utf-8 -*-
import scrapy
import json
from news.items import NewsItem

class TencentSpider(scrapy.Spider):
    name = 'tencent_spider'
    allowed_domains = ['qq.com']
    # API endpoint for hot news
    hot_news_url = "https://i.news.qq.com/web_feed/getHotModuleList"

    custom_settings = {
        'DEFAULT_REQUEST_HEADERS': {
            # Headers for the initial POST request to the API
            'accept': 'application/json, text/plain, */*',
            'accept-language': 'zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6',
            'cache-control': 'no-cache',
            'content-type': 'application/json;charset=UTF-8',
            'origin': 'https://news.qq.com',
            'pragma': 'no-cache',
            'priority': 'u=1, i',
            'referer': 'https://news.qq.com/',
            'sec-ch-ua': '"Not A(Brand";v="8", "Chromium";v="132", "Microsoft Edge";v="132"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"',
            'sec-fetch-dest': 'empty',
            'sec-fetch-mode': 'cors',
            'sec-fetch-site': 'same-site',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/132.0.0.0 Safari/537.36 Edg/132.0.0.0',
        },
        # Consider adding cookies from the original request_handler if needed
        # 'COOKIES_ENABLED': True,
    }

    # Headers specifically for fetching the detail HTML pages (GET requests)
    detail_headers = {
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
        'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6',
        'Cache-Control': 'no-cache',
        'Connection': 'keep-alive',
        'Pragma': 'no-cache',
        'Sec-Fetch-Dest': 'document',
        'Sec-Fetch-Mode': 'navigate',
        'Sec-Fetch-Site': 'none',
        'Sec-Fetch-User': '?1',
        'Upgrade-Insecure-Requests': '1',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/132.0.0.0 Safari/537.36 Edg/132.0.0.0',
        'sec-ch-ua': '"Not A(Brand";v="8", "Chromium";v="132", "Microsoft Edge";v="132"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"',
    }

    def start_requests(self):
        # Data payload for the POST request
        # qimei36 and device_id might need to be dynamic or obtained differently
        post_data = {
            "base_req": {"from": "pc"},
            "forward": "2",
            "qimei36": "0_placeholder_qimei36", # Placeholder
            "device_id": "0_placeholder_device_id", # Placeholder
            "flush_num": 1,
            "channel_id": "news_news_top",
            "item_count": 20,
        }
        yield scrapy.Request(
            self.hot_news_url,
            method='POST',
            body=json.dumps(post_data),
            headers=self.settings.get('DEFAULT_REQUEST_HEADERS'), # Use headers from settings
            callback=self.parse_hot_list
        )

    def parse_hot_list(self, response):
        self.logger.info(f'Parsing hot news list API response: {response.url}')
        try:
            json_data = json.loads(response.text)
            news_list = json_data.get('data', [])
            if not isinstance(news_list, list):
                self.logger.warning(f'API response data format error: data is not a list. Response: {response.text}')
                return

            self.logger.info(f'Found {len(news_list)} items in hot news list.')
            for news_item_data in news_list:
                if not isinstance(news_item_data, dict):
                    self.logger.warning(f'Skipping invalid item in list (not a dict): {news_item_data}')
                    continue

                link_info = news_item_data.get('link_info', {})
                url = link_info.get('url')
                title = news_item_data.get('title')
                intro = news_item_data.get('intro') # Description from list

                if url and title:
                    # Use detail_headers for the GET request to the article page
                    yield scrapy.Request(
                        url,
                        callback=self.parse_news_detail,
                        headers=self.detail_headers,
                        meta={'title_from_list': title, 'summary_from_list': intro}
                    )
                else:
                    self.logger.warning(f'Missing url or title in hot news item: {news_item_data}')

        except json.JSONDecodeError as e:
            self.logger.error(f"JSON parsing failed for {response.url}: {e}. Response text: {response.text}")
        except Exception as e:
            self.logger.error(f"Error processing hot news list {response.url}: {e}")

    def parse_news_detail(self, response):
        self.logger.info(f'Parsing news detail: {response.url}')
        item = NewsItem()
        title_from_list = response.meta.get('title_from_list')
        summary_from_list = response.meta.get('summary_from_list')

        # --- Placeholder Selectors for Detail Page --- 
        # **ADJUST THESE BASED ON ACTUAL TENCENT NEWS PAGE STRUCTURE (e.g., new.qq.com/...)**
        # Tencent pages often use complex JS rendering, direct scraping might be hard.
        # Look for data embedded in <script> tags or specific divs like 'content-article'

        # Extract Title
        title = response.css('h1::text').get() or \
                response.css('.title ::text').get() or \
                response.css('.LEFT h1::text').get() or \
                response.css('meta[property="og:title"]::attr(content)').get() or \
                title_from_list
        item['title'] = title.strip() if title else None

        # Extract Author
        # Often inside a source span or div
        author = response.css('.author::text').get() or \
                 response.css('.color-a-1 span::text').get() or \
                 response.css('meta[name="author"]::attr(content)').get()
        item['author'] = author.strip() if author else None

        # Extract Publish Time
        publish_time = response.css('.time::text').get() or \
                       response.css('.pubTime ::text').get() or \
                       response.css('.a_time ::text').get() or \
                       response.css('meta[property="article:published_time"]::attr(content)').get()
        item['publish_time'] = publish_time.strip() if publish_time else None

        # Extract Summary/Description
        summary = response.css('meta[name="description"]::attr(content)').get() or \
                  summary_from_list # Fallback to summary from list API
        # summary = summary or response.css('.content-article > p::text').get() # First paragraph as fallback
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