# -*- coding: utf-8 -*-
import scrapy
import json
import re
# Assuming NewsItem is defined in news/items.py
# from news.items import NewsItem

# Placeholder for NewsItem definition for completeness if not available
# In a real Scrapy project, you would import it from news.items
class NewsItem(scrapy.Item):
    title = scrapy.Field()
    author = scrapy.Field()
    publish_time = scrapy.Field()
    summary = scrapy.Field()
    source = scrapy.Field()
    link = scrapy.Field()


class CctvSpider(scrapy.Spider):
    name = 'cctv_spider'
    allowed_domains = ['news.cctv.com']
    start_urls = ['https://news.cctv.com/2019/07/gaiban/cmsdatainterface/page/china_1.jsonp']

    custom_settings = {
        'DEFAULT_REQUEST_HEADERS': {
            'Accept': 'text/javascript, application/javascript, application/ecmascript, application/x-ecmascript, */*; q=0.01',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6',
            'Cache-Control': 'no-cache',
            'Connection': 'keep-alive',
            'Pragma': 'no-cache',
            'Referer': 'https://news.cctv.com/china/?spm=C94212.P4YnMod9m2uD.EWZW7h07k3Vs.2',
            'Sec-Fetch-Dest': 'empty',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Site': 'same-origin',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/132.0.0.0 Safari/537.36 Edg/132.0.0.0',
            'X-Requested-With': 'XMLHttpRequest',
            'sec-ch-ua': '"Not A(Brand";v="8", "Chromium";v="132", "Microsoft Edge";v="132"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"',
        }
    }

    def parse(self, response):
        self.logger.info(f'Parsing initial list: {response.url}')

        # --- Modified Parsing Logic to handle potential HTML wrapper ---
        # Attempt to extract the text content from the body, which should contain the JSONP call
        # This is more robust if the JSONP is not the sole content of the response
        body_text = "".join(response.css('body ::text').getall())

        # Extract JSON from the 'china(...)' callback wrapper within the body text
        # Look for {.*?} explicitly to be slightly more specific
        json_pattern = r"china\(\s*(\{.*?\})\s*\)"
        match = re.search(json_pattern, body_text, re.DOTALL)

        if match:
            json_str = match.group(1)
            self.logger.info(f"Successfully extracted JSON string from body text.")
            # Optional: Log the start/end of the extracted string for verification
            # self.logger.debug(f"Extracted JSON string (first 200 chars): {json_str[:200]}...")
            # self.logger.debug(f"Extracted JSON string (last 200 chars): {json_str[-200:]}")


            try:
                json_data = json.loads(json_str)
                news_list = json_data.get('data', {}).get('list', [])
                self.logger.info(f'Found {len(news_list)} news items in the list.')
                for news_item_data in news_list:
                    url = news_item_data.get('url')
                    if url:
                        yield scrapy.Request(url, callback=self.parse_news_detail, meta={'original_data': news_item_data})
                    else:
                        self.logger.warning(f'No URL found in news item data: {news_item_data}')
            except json.JSONDecodeError as e:
                self.logger.error(f"JSON parsing failed for {response.url}: {e}")
                self.logger.error(f"Error details: {e}")
                # Log the malformed json_str to help debug truncation/encoding issues
                self.logger.error(f"Malformed JSON string (first 500 chars): {json_str[:500]}...")
                self.logger.error(f"Malformed JSON string (last 500 chars): {json_str[-500:]}")
            except Exception as e:
                self.logger.error(f"Error processing initial list {response.url}: {e}")
        else:
            self.logger.error(f"Could not extract JSON data from {response.url}.")
            self.logger.error(f"Body text starts with: {body_text[:500]}...") # Log start of body text

        # --- End Modified Parsing Logic ---


    def parse_news_detail(self, response):
        self.logger.info(f'Parsing news detail: {response.url}')
        original_data = response.meta.get('original_data', {})
        item = NewsItem()

        # --- Data Extraction Logic ---
        # The original code used a generic 'get_news_content'.
        # We need specific selectors for CCTV news pages.
        # These are common placeholders - **ADJUST THEM BASED ON ACTUAL CCTV PAGE STRUCTURE**

        # Extract Title (Try common tags/classes)
        title = response.css('h1::text').get() or \
                response.css('.title ::text').get() or \
                response.css('meta[property="og:title"]::attr(content)').get() or \
                original_data.get('title') # Fallback to list data
        item['title'] = title.strip() if title else None

        # Extract Author (Try common patterns)
        author = response.css('.author::text').get() or \
                 response.css('.editor ::text').get() or \
                 response.css('meta[name="author"]::attr(content)').get()
        item['author'] = author.strip() if author else None

        # Extract Publish Time (Try common patterns)
        publish_time = response.css('.time::text').get() or \
                       response.css('.pubtime ::text').get() or \
                       response.css('meta[property="article:published_time"]::attr(content)').get() or \
                       original_data.get('focus_date') # Fallback to list data
        item['publish_time'] = publish_time.strip() if publish_time else None

        # Extract Summary/Description (Try common patterns)
        summary = response.css('meta[name="description"]::attr(content)').get() or \
                  response.css('.summary ::text').get() or \
                  response.css('.abstract ::text').get() or \
                  original_data.get('brief') # Fallback to list data
        item['summary'] = summary.strip() if summary else None

        # --- FORCED SOURCE VALUE ---
        # As per requirement, force the source to match the spider name.
        item['source'] = self.name # This will always be 'cctv_spider'
        # --- END FORCED SOURCE VALUE ---

        # Link is always the response URL
        item['link'] = response.url

        # --- End Data Extraction ---

        # Basic validation: Ensure at least title and link are present
        if item['title'] and item['link']:
            self.logger.debug(f'Yielding item: {item["title"]}')
            yield item
        else:
            self.logger.warning(f'Failed to extract essential data (title/link) from {response.url}')

