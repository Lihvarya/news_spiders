# -*- coding: utf-8 -*-
import scrapy
from news.items import NewsItem

class FenghuangSpider(scrapy.Spider):
    name = 'fenghuang_spider'
    allowed_domains = ['ifeng.com']
    start_urls = ['https://www.ifeng.com/'] # Target the homepage for hot news

    custom_settings = {
        'DEFAULT_REQUEST_HEADERS': {
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6',
            'Cache-Control': 'no-cache',
            'Connection': 'keep-alive',
            'Pragma': 'no-cache',
            # 'Referer': 'https://cn.bing.com/', # Referer might need adjustment or removal depending on site behavior
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'cross-site', # Changed from same-origin based on original handler
            'Sec-Fetch-User': '?1',
            'Upgrade-Insecure-Requests': '1',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36 Edg/135.0.0.0',
            'sec-ch-ua': '"Microsoft Edge";v="135", "Not-A.Brand";v="8", "Chromium";v="135"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"',
        }
    }

    def parse(self, response):
        self.logger.info(f'Parsing homepage: {response.url}')

        # --- Placeholder Selectors --- 
        # These selectors need to be identified by inspecting www.ifeng.com
        # Example: Find main news blocks/links
        news_links = response.css('a[href*="news.ifeng.com/c/"]::attr(href)').getall() # Example selector, **NEEDS VERIFICATION**
        news_blocks = response.css('.news-item-class') # Example selector, **NEEDS VERIFICATION**

        self.logger.info(f'Found potential {len(news_links)} links and {len(news_blocks)} blocks (using placeholders).')

        # Process links found directly
        for link in news_links:
            yield response.follow(link, self.parse_news_detail)

        # Process news blocks if links aren't direct
        for block in news_blocks:
            # Extract link and title from the block
            link = block.css('a::attr(href)').get() # Example
            title = block.css('.title-class::text').get() # Example

            if link:
                # Pass title if available, helps if detail page lacks it
                yield response.follow(link, self.parse_news_detail, meta={'title_from_list': title})
            else:
                self.logger.warning(f'Could not find link in block: {block.get()}')

        # Add logic for pagination if necessary
        # next_page = response.css('a.next-page::attr(href)').get()
        # if next_page:
        #     yield response.follow(next_page, self.parse)

    def parse_news_detail(self, response):
        self.logger.info(f'Parsing news detail: {response.url}')
        item = NewsItem()

        # --- Placeholder Selectors for Detail Page --- 
        # **ADJUST THESE BASED ON ACTUAL IFENG NEWS PAGE STRUCTURE**

        title_from_list = response.meta.get('title_from_list')

        # Extract Title
        title = response.css('h1::text').get() or \
                response.css('.title-class-detail ::text').get() or \
                response.css('meta[property="og:title"]::attr(content)').get() or \
                title_from_list # Fallback to title from list page
        item['title'] = title.strip() if title else None

        # Extract Author
        author = response.css('.author-class ::text').get() or \
                 response.css('.editor-class ::text').get()
        item['author'] = author.strip() if author else None

        # Extract Publish Time
        publish_time = response.css('.time-class ::text').get() or \
                       response.css('.pubtime-class ::text').get() or \
                       response.css('meta[property="article:published_time"]::attr(content)').get()
        item['publish_time'] = publish_time.strip() if publish_time else None

        # Extract Summary/Description
        summary = response.css('meta[name="description"]::attr(content)').get() or \
                  response.css('.summary-class ::text').get() or \
                  response.css('.abstract-class ::text').get()
        # Often the first paragraph can serve as a summary
        # summary = summary or response.css('div.content-class > p::text').get()
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