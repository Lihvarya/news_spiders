# -*- coding: utf-8 -*-
import scrapy
import json
from news.items import NewsItem

class ThepaperSpider(scrapy.Spider):
    name = 'thepaper_spider'
    allowed_domains = ['thepaper.cn']
    # API endpoint for hot news (sidebar)
    start_urls = ['https://cache.thepaper.cn/contentapi/wwwIndex/rightSidebar']

    custom_settings = {
        'DEFAULT_REQUEST_HEADERS': {
            'accept': 'application/json, text/plain, */*',
            'accept-language': 'zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6',
            'cache-control': 'no-cache',
            'client-type': '1',
            'origin': 'https://www.thepaper.cn',
            'pragma': 'no-cache',
            'priority': 'u=1, i',
            'referer': 'https://www.thepaper.cn/',
            'sec-ch-ua': '"Microsoft Edge";v="135", "Not-A.Brand";v="8", "Chromium";v="135"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"',
            'sec-fetch-dest': 'empty',
            'sec-fetch-mode': 'cors',
            'sec-fetch-site': 'same-site',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36 Edg/135.0.0.0',
        },
        # Cookies from the original handler might be necessary
        # 'COOKIES_ENABLED': True,
        # 'COOKIES': {
        #     'Hm_lvt_94a1e06bbce219d29285cee2e37d1d26': '1744610629',
        #     'HMACCOUNT': 'A526A7800166442B',
        #     'ariaDefaultTheme': 'undefined',
        #     'Hm_lpvt_94a1e06bbce219d29285cee2e37d1d26': '1744610673',
        #     # 'tfstk': '...' # This cookie looks dynamic, might not be needed or needs generation
        # }
    }

    # Headers for fetching detail pages (HTML)
    detail_headers = {
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
        'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6',
        'Cache-Control': 'no-cache',
        'Connection': 'keep-alive',
        'Pragma': 'no-cache',
        'Referer': 'https://www.thepaper.cn/', # Referer might be important
        'Sec-Fetch-Dest': 'document',
        'Sec-Fetch-Mode': 'navigate',
        'Sec-Fetch-Site': 'same-origin',
        'Sec-Fetch-User': '?1',
        'Upgrade-Insecure-Requests': '1',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36 Edg/135.0.0.0',
    }

    def parse(self, response):
        self.logger.info(f'Parsing hot news API response: {response.url}')
        try:
            json_data = json.loads(response.text)
            news_list = json_data.get('data', {}).get('hotNews', [])
            if not isinstance(news_list, list):
                self.logger.warning(f'API response data format error: hotNews is not a list. Response: {response.text}')
                return

            self.logger.info(f'Found {len(news_list)} items in hot news list.')
            for news_item_data in news_list:
                if not isinstance(news_item_data, dict):
                    self.logger.warning(f'Skipping invalid item in list (not a dict): {news_item_data}')
                    continue

                cont_id = news_item_data.get('contId')
                title = news_item_data.get('name')

                if cont_id and title:
                    # Construct the URL based on contId
                    url = f'https://www.thepaper.cn/newsDetail_forward_{cont_id}'
                    yield scrapy.Request(
                        url,
                        callback=self.parse_news_detail,
                        headers=self.detail_headers,
                        meta={'title_from_list': title}
                    )
                else:
                    self.logger.warning(f'Missing contId or name in hot news item: {news_item_data}')

        except json.JSONDecodeError as e:
            self.logger.error(f"JSON parsing failed for {response.url}: {e}. Response text: {response.text}")
        except Exception as e:
            self.logger.error(f"Error processing hot news list {response.url}: {e}")

    def parse_news_detail(self, response):
        self.logger.info(f'Parsing news detail: {response.url}')
        item = NewsItem()
        title_from_list = response.meta.get('title_from_list')

        # --- Placeholder Selectors for Detail Page --- 
        # **ADJUST THESE BASED ON ACTUAL THEPAPER.CN NEWS PAGE STRUCTURE**
        # ThePaper often uses divs with class 'news_content' or similar

        # Extract Title
        title = response.css('h1.news_title::text').get() or \
                response.css('meta[property="og:title"]::attr(content)').get() or \
                title_from_list
        item['title'] = title.strip() if title else None

        # Extract Author
        # Author might be within the source span or a separate element
        author = response.css('.news_about .news_author::text').get() or \
                 response.css('meta[name="author"]::attr(content)').get()
        item['author'] = author.strip() if author else None

        # Extract Publish Time
        publish_time = response.css('.news_about .news_date::text').get() or \
                       response.css('meta[property="article:published_time"]::attr(content)').get()
        item['publish_time'] = publish_time.strip() if publish_time else None

        # Extract Summary/Description
        summary = response.css('meta[name="description"]::attr(content)').get() or \
                  response.css('.news_content p::text').get() # First paragraph as fallback
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