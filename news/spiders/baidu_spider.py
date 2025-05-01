# -*- coding: utf-8 -*-
import scrapy
# from bs4 import BeautifulSoup # 移除 BeautifulSoup
from news.items import NewsItem # 假设 NewsItem 已经在 news/items.py 中定义

class BaiduSpider(scrapy.Spider):
    name = 'baidu_spider'
    allowed_domains = ['top.baidu.com']
    start_urls = ['https://top.baidu.com/board?tab=realtime']

    custom_settings = {
        'DEFAULT_REQUEST_HEADERS': {
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6',
            'Cache-Control': 'no-cache',
            'Connection': 'keep-alive',
            'Pragma': 'no-cache',
            'Referer': 'https://top.baidu.com/board',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'same-origin',
            'Sec-Fetch-User': '?1',
            'Upgrade-Insecure-Requests': '1',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36 Edg/135.0.0.0', # 保持伪装浏览器
            'sec-ch-ua': '"Microsoft Edge";v="135", "Not-A.Brand";v="8", "Chromium";v="135"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"',
        }
    }

    def parse(self, response):
        self.logger.info(f'Parsing page: {response.url}')

        # 使用 Scrapy 的 CSS 选择器直接获取条目 div
        # 这里的 SelectorList 对象可以直接迭代
        items = response.css('div.category-wrap_iQLoo.horizontal_1eKyQ')

        count = 0
        # 直接遍历 SelectorList，每个 item_div 是一个 Selector 对象
        for item_div in items:
            if count >= 10: # 限制获取前10条新闻
                break

            news_item = NewsItem()

            # 使用 CSS 选择器提取链接
            # 定位到内容区域的标题链接，获取其 href 属性
            url = item_div.css('div.content_1YWBm a.title_dIF3B::attr(href)').get()

            # 使用 CSS 选择器提取标题文本
            # 定位到标题链接内的文本 div
            title = item_div.css('div.content_1YWBm a.title_dIF3B div.c-single-text-ellipsis::text').get()

            # 使用 CSS 选择器提取描述文本
            # 同时匹配 large 或 small 类的描述 div
            description = item_div.css('div.content_1YWBm div.hot-desc_1m_jR.large_nSuFU::text, div.content_1YWBm div.hot-desc_1m_jR.small_Uvkd3::text').get()


            # 检查是否成功提取到关键信息
            if title and url:
                news_item['title'] = title.strip() if title else None # strip() 移除首尾空白
                news_item['link'] = url
                news_item['summary'] = description.strip() if description else None # strip()
                news_item['source'] = self.name # 设置来源为爬虫名称

                # 提交 item 到 pipeline
                yield news_item
                count += 1
            else:
                # 记录未能提取到关键信息的条目（可选，用于调试）
                # item_div.get() 将 Selector 对象转换为其 HTML 字符串
                self.logger.warning(f'Could not extract title or url from item: {item_div.get()}')

        self.logger.info(f'Finished parsing {response.url}. Found {count} items.')

