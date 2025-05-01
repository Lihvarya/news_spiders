import scrapy
from bs4 import BeautifulSoup
from news.items import NewsItem
import re
import json

class NeteaseSpider(scrapy.Spider):
    name = 'netease_spider'
    # MODIFICATION 1: Add www.163.com to allowed_domains
    allowed_domains = ['news.163.com', 'www.163.com']
    # Start with the hot news page (HTML)
    start_urls = ['https://news.163.com/domestic/']
    # URL for latest china news (JSONP)
    latest_china_news_url = 'https://news.163.com/special/cm_guonei/' # Not used in start_urls initially

    custom_settings = {
        'DEFAULT_REQUEST_HEADERS': {
            'accept': '*/*',
            'accept-language': 'zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6',
            'cache-control': 'no-cache',
            'pragma': 'no-cache',
            'referer': 'https://news.163.com/domestic/',
            'sec-ch-ua': '"Not A(Brand";v="8", "Chromium";v="132", "Microsoft Edge";v="132"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"',
            'sec-fetch-dest': 'document', # Changed to document for initial HTML page load
            'sec-fetch-mode': 'navigate', # Changed for initial page load
            'sec-fetch-site': 'same-origin',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/132.0.0.0 Safari/537.36 Edg/132.0.0.0',
            'Upgrade-Insecure-Requests': '1' # Added for initial page load
        }
    }

    def start_requests(self):
        # Request the hot news page first
        yield scrapy.Request(self.start_urls[0], callback=self.parse_hot_news)
        # Optionally, request the latest news JSONP URL
        # yield scrapy.Request(self.latest_china_news_url, callback=self.parse_latest_news, headers={'Accept': 'text/javascript'}) # Adjust headers if needed

    def parse_hot_news(self, response):
        self.logger.info(f'Parsing hot news page: {response.url}')
        soup = BeautifulSoup(response.text, "html.parser")
        recommendations = []

        # Find the div with class="mt15 mod_jrtj"
        div = soup.find("div", class_="mt15 mod_jrtj")
        if div:
            # Find all <li> tags under this div
            list_items = div.find_all("li")
            self.logger.info(f'Found {len(list_items)} items in hot news section.')
            for li in list_items:
                a_tag = li.find("a")
                if a_tag and a_tag.has_attr('href') and a_tag.has_attr('title'):
                    title = a_tag['title']
                    href = a_tag['href']
                    # MODIFICATION 2: Relax the filtering condition
                    # Allow links starting with http/https and containing either news.163.com or www.163.com
                    if href.startswith('http') and ('news.163.com' in href or 'www.163.com' in href):
                        self.logger.debug(f'Found hot news link: {href}')
                        # Scrapy's OffsiteMiddleware will handle further filtering based on allowed_domains
                        yield scrapy.Request(href, callback=self.parse_news_detail, meta={'title_from_list': title})
                    else:
                         # This warning will still appear for truly non-news links (e.g., links to other sections)
                         self.logger.warning(f'Skipping potentially non-news or offsite link: {href}')
                else:
                    self.logger.warning(f'Could not extract link or title from list item: {li}')
        else:
            self.logger.warning(f'Could not find hot news section (div.mt15.mod_jrtj) on {response.url}')

    # ... rest of the code (parse_latest_news and parse_news_detail) remains the same ...

    def parse_news_detail(self, response):
        self.logger.info(f'Parsing news detail: {response.url}')
        item = NewsItem()
        title_from_list = response.meta.get('title_from_list')

        # --- Placeholder Selectors for Detail Page ---
        # **ADJUST THESE BASED ON ACTUAL NETEASE NEWS PAGE STRUCTURE**
        # Netease pages often have complex structures (e.g., post_body div)

        # Extract Title
        title = response.css('h1::text').get() or \
                response.css('.post_title::text').get() or \
                response.css('meta[property="og:title"]::attr(content)').get() or \
                title_from_list
        item['title'] = title.strip() if title else None

        # Extract Author (Often tricky, might be in source info)
        # Look within source info spans/divs
        author = response.css('.post_info .author::text').get() or \
                 response.css('#ne_article_source::text').get() # Sometimes source contains author implicitly
        item['author'] = author.strip() if author else None

        # Extract Publish Time
        publish_time = response.css('.post_info .pub_time::text').get() or \
                       response.css('.post_time_source::text').re_first(r'\d{4}-\d{2}-\d{2}\s\d{2}:\d{2}:\d{2}') or \
                       response.css('meta[property="article:published_time"]::attr(content)').get()
        item['publish_time'] = publish_time.strip() if publish_time else None

        # Extract Summary/Description
        summary = response.css('meta[name="description"]::attr(content)').get() or \
                  response.css('.post_body > p::text').get() # First paragraph as fallback
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

