# -*- coding: utf-8 -*-
import scrapy
from bs4 import BeautifulSoup
from news.items import NewsItem

class ZhihuSpider(scrapy.Spider):
    name = 'zhihu_spider'
    allowed_domains = ['zhihu.com']
    start_urls = ['https://www.zhihu.com/hot'] # Zhihu hot list page

    custom_settings = {
        'DEFAULT_REQUEST_HEADERS': {
            'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
            'accept-language': 'zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6',
            'cache-control': 'no-cache',
            'pragma': 'no-cache',
            'priority': 'u=0, i',
            'sec-ch-ua': '"Microsoft Edge";v="135", "Not-A.Brand";v="8", "Chromium";v="135"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"',
            'sec-fetch-dest': 'document',
            'sec-fetch-mode': 'navigate',
            'sec-fetch-site': 'same-origin', # Changed from none based on original handler
            'sec-fetch-user': '?1',
            'upgrade-insecure-requests': '1',
            # User agent from original handler, removed Safari part as it was likely a copy-paste error
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Edg/135.0.0.0',
        },
        'COOKIES_ENABLED': True,
        # Cookies from original handler - IMPORTANT: These might expire or be tied to a specific login.
        # Consider implementing proper login or using fresh cookies.
        # 'COOKIES': {
        #     'q_c1': '68e3a76b187540c0879dbafd315ebad8|1718820150000|1693300214000',
        #     '_zap': 'df87f5b7-785e-4222-b9c0-0ccff97423c4',
        #     'd_c0': 'ADDS2be5ohmPTivBF6K_oX-8FajxozYS_MM=|1733197050',
        #     '_xsrf': 'xGAE4IvHlxmuOR2YmQcp4THTGvteYPMh',
        #     # ... other cookies ...
        #     # 'z_c0': '...' # This looks like a session/auth token, likely needed
        # }
    }

    def parse(self, response):
        self.logger.info(f'Parsing Zhihu hot list page: {response.url}')
        # Use BeautifulSoup as per the original parser
        soup = BeautifulSoup(response.text, "html.parser")
        items_divs = soup.find_all("div", class_="HotItem-content")
        self.logger.info(f'Found {len(items_divs)} potential items on the page.')
        count = 0

        for item_div in items_divs:
            news_item = NewsItem()

            # Extract link
            a_tag = item_div.find("a")
            url = a_tag['href'] if a_tag and a_tag.has_attr('href') else None

            # Extract title
            title_tag = item_div.find("h2", class_="HotItem-title")
            title = title_tag.text.strip() if title_tag else None

            # Extract description/excerpt
            desc_tag = item_div.find("p", class_="HotItem-excerpt")
            description = desc_tag.text.strip() if desc_tag else None

            if title and url:
                # Ensure URL is absolute
                if not url.startswith('http'):
                    url = response.urljoin(url)

                news_item['title'] = title
                news_item['link'] = url
                news_item['summary'] = description
                news_item['source'] = self.name
                # Author and publish time are not directly available in the hot list item structure

                yield news_item
                count += 1
            else:
                self.logger.warning(f'Could not extract title or url from item: {item_div}')

        self.logger.info(f'Finished parsing {response.url}. Yielded {count} items.')

        # Note: Zhihu hot list is usually a single page, no pagination needed typically.
        # If pagination exists, add logic here.