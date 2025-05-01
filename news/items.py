# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class NewsItem(scrapy.Item):
    # define the fields for your item here like:
    title = scrapy.Field()         # 标题
    author = scrapy.Field()        # 作者
    publish_time = scrapy.Field()  # 发布时间
    summary = scrapy.Field()       # 摘要
    source = scrapy.Field()        # 来源
    link = scrapy.Field()          # 全文链接
    # content = scrapy.Field()     # 可选：全文内容
    # content_hash = scrapy.Field() # 可选：用于去重的内容哈希值
