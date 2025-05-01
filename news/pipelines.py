# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html

from itemadapter import ItemAdapter
import pymysql
from twisted.enterprise import adbapi
from scrapy.utils.project import get_project_settings
import logging
import re # Import re for regex operations (e.g., HTML stripping)
# from parsel import Selector # Uncomment if you want to use parsel for HTML stripping
# from datetime import datetime # Uncomment if you need complex date parsing

# Configure logging for pipelines
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class DataCleaningPipeline:
    """
    Pipeline to perform data cleaning on scraped items.
    Should run before the database pipeline.
    """
    def process_item(self, item, spider):
        adapter = ItemAdapter(item)

        # --- Basic Cleaning: Strip Whitespace ---
        # --- 基本清洗：去除空白字符 ---
        for field_name in ['title', 'author', 'summary', 'source', 'link']:
            value = adapter.get(field_name)
            if isinstance(value, str):
                adapter[field_name] = value.strip()

        # --- More Advanced Cleaning Examples ---
        # --- 更高级的清洗示例 ---

        # Clean Summary: Remove HTML tags (using regex - may not be perfect for complex HTML)
        # 清洗摘要：移除 HTML 标签 (使用正则表达式 - 对于复杂的 HTML 可能不完美)
        if adapter.get('summary'):
            # Basic regex to remove HTML tags <...>
            # 移除 HTML 标签 <...> 的基本正则表达式
            clean_summary = re.sub(r'<.*?>', '', adapter['summary'])
            # Optional: Remove common HTML entities like &nbsp; &amp; etc.
            # 可选：移除常见的 HTML 实体，如 &nbsp; &amp; 等。
            # clean_summary = html.unescape(clean_summary) # Requires 'html' module (Python 3.4+)
            adapter['summary'] = clean_summary.strip() # Strip whitespace again after cleaning
            # 清洗后再次去除空白字符

        # Clean Publish Time: Attempt to standardize or parse
        # 清洗发布时间：尝试标准化或解析
        # This is highly dependent on the source format. Example placeholder:
        # 这很大程度上取决于源格式。示例占位符：
        # if adapter.get('publish_time'):
        #     try:
        #         # Example: Assuming 'YYYY-MM-DD HH:MM:SS' or similar
        #         # 示例：假设格式为 'YYYY-MM-DD HH:MM:SS' 或类似
        #         # You'll likely need more robust parsing (e.g., using dateutil)
        #         # 你可能需要更健壮的解析（例如，使用 dateutil 库）
        #         # from dateutil import parser
        #         # parsed_time = parser.parse(adapter['publish_time'])
        #         # adapter['publish_time'] = parsed_time.strftime('%Y-%m-%d %H:%M:%S')
        #         pass # Placeholder - implement your specific parsing here
        #         # 占位符 - 在这里实现你特定的解析逻辑
        #     except Exception as e:
        #         logger.warning(f"Could not parse publish_time '{adapter['publish_time']}' for {adapter.get('link')}: {e}")
        #         adapter['publish_time'] = None # Set to None if parsing fails
        #         # 如果解析失败，设置为 None

        # --- Validation / Filtering ---
        # --- 验证 / 过滤 ---
        # Drop items that are missing essential fields after cleaning
        # 丢弃清洗后缺少必要字段的项目
        if not adapter.get('title') or not adapter.get('link'):
            logger.warning(f"Dropping item due to missing title or link: {adapter.get('link')}")
            from scrapy.exceptions import DropItem
            raise DropItem(f"Missing title or link in {item}")

        return item


class NewsPipeline:
    """
    Pipeline to handle database storage and link-based deduplication.
    Requires a UNIQUE constraint on the 'link' column in the database.
    """
    def __init__(self):
        settings = get_project_settings()
        db_params = dict(
            host=settings['MYSQL_HOST'],
            user=settings['MYSQL_USER'],
            password=settings['MYSQL_PASSWORD'],
            db=settings['MYSQL_DB'],
            port=settings['MYSQL_PORT'],
            charset='utf8mb4',
            cursorclass=pymysql.cursors.DictCursor, # Use DictCursor for easy access
            # 使用 DictCursor 方便访问
            use_unicode=True,
        )
        # Use Twisted's adbapi to create a connection pool for asynchronous database operations
        # 使用 Twisted 的 adbapi 创建连接池，用于异步数据库操作
        try:
            self.dbpool = adbapi.ConnectionPool('pymysql', **db_params)
            logger.info("Database connection pool initialized.")
            # 数据库连接池已初始化。
        except Exception as e:
            logger.error(f"Failed to initialize database connection pool: {e}")
            # 初始化数据库连接池失败：
            self.dbpool = None # Ensure dbpool is None if connection fails
            # 如果连接失败，确保 dbpool 为 None

    def close_spider(self, spider):
        # Close the connection pool when the spider closes
        # 当爬虫关闭时，关闭连接池
        if self.dbpool:
            self.dbpool.close()
            logger.info("Database connection pool closed.")
            # 数据库连接池已关闭。

    def process_item(self, item, spider):
        """
        Process the item and store it in the database using the connection pool.
        Handles link-based deduplication via ON DUPLICATE KEY UPDATE.
        """
        if not self.dbpool:
            logger.error("Database pool is not initialized. Cannot process item.")
            # 数据库连接池未初始化。无法处理项目。
            from scrapy.exceptions import DropItem
            raise DropItem("Database connection failed.")
            # 数据库连接失败。

        # Use the connection pool to run the database interaction asynchronously
        # 使用连接池异步运行数据库交互
        # self.do_insert will be called within a database transaction
        # self.do_insert 将在数据库事务中被调用
        query = self.dbpool.runInteraction(self.do_insert, item)
        # Add an errback to handle potential database errors
        # 添加一个错误回调函数来处理潜在的数据库错误
        query.addErrback(self.handle_error, item, spider)
        return item

    def handle_error(self, failure, item, spider):
        # Log database insertion errors
        # 记录数据库插入错误
        logger.error(f"Database error for item {ItemAdapter(item).get('link')}: {failure.getErrorMessage()}")
        # Optionally re-raise the exception if you want Scrapy to handle it further
        # 如果你想让 Scrapy 进一步处理，可以选择重新抛出异常
        # return failure # Uncomment this line if needed
        # 如果需要，取消此行的注释

    def do_insert(self, cursor, item):
        """
        Execute the SQL INSERT or UPDATE statement.
        This method runs within a database transaction.
        """
        adapter = ItemAdapter(item)

        # SQL statement for inserting or updating data
        # 用于插入或更新数据的 SQL 语句
        # Requires a UNIQUE constraint on the `link` column for ON DUPLICATE KEY UPDATE to work as deduplication
        # 需要在 `link` 列上有一个 UNIQUE 约束，以便 ON DUPLICATE KEY UPDATE 起作用进行去重
        insert_sql = """
            INSERT INTO news_articles (title, author, publish_time, summary, source, link)
            VALUES (%s, %s, %s, %s, %s, %s)
            ON DUPLICATE KEY UPDATE
                title=VALUES(title),
                author=VALUES(author),
                publish_time=VALUES(publish_time),
                summary=VALUES(summary),
                source=VALUES(source);
        """
        # ON DUPLICATE KEY UPDATE: If a row with the same 'link' already exists,
        # 如果存在具有相同 'link' 的行，则更新现有记录。
        # update the specified columns with the values from the new item.
        # 使用新项目的值更新指定列。
        # If no row exists, perform a standard INSERT.
        # 如果不存在行，则执行标准插入。

        params = (
            adapter.get('title'),
            adapter.get('author'),
            adapter.get('publish_time'),
            adapter.get('summary'),
            adapter.get('source'), # This should be the spider name
            # 这应该是爬虫名称
            adapter.get('link')
        )

        try:
            cursor.execute(insert_sql, params)
            # Note: cursor.rowcount will be 1 for an insert, 2 for an update
            # 注意：对于插入，cursor.rowcount 将为 1；对于更新，将为 2
            if cursor.rowcount == 1:
                 logger.debug(f"Inserted new item: {adapter.get('link')}")
                 # 插入新项目：
            elif cursor.rowcount == 2:
                 logger.debug(f"Updated existing item: {adapter.get('link')}")
                 # 更新现有项目：
            else:
                 logger.warning(f"Unexpected rowcount ({cursor.rowcount}) for {adapter.get('link')}")
                 # 对于 {adapter.get('link')}，意外的行数 ({cursor.rowcount})

        except Exception as e:
             logger.error(f"SQL execution error for {adapter.get('link')}: {e}")
             # {adapter.get('link')} 的 SQL 执行错误：
             # Re-raise the exception so adbapi can handle it in the errback
             # 重新抛出异常，以便 adbapi 可以在错误回调函数中处理它
             raise


# --- Important: Configuration in settings.py ---
# --- 重要：在 settings.py 中的配置 ---
# To enable these pipelines, you must add them to your project's settings.py
# 要启用这些管道，你必须将它们添加到你的项目的 settings.py 中
# Ensure the order is correct: cleaning first, then database storage/deduplication.
# 确保顺序正确：先清洗，然后是数据库存储/去重。

# Example settings.py configuration:
# settings.py 配置示例：
# ITEM_PIPELINES = {
#    'your_project_name.pipelines.DataCleaningPipeline': 300, # Lower number runs first
#    '你的项目名称.pipelines.DataCleaningPipeline': 300, # 数字越小越先运行
#    'your_project_name.pipelines.NewsPipeline': 400,       # Higher number runs later
#    '你的项目名称.pipelines.NewsPipeline': 400,       # 数字越大越后运行
# }
# Make sure to replace 'your_project_name' with your actual project name.
# 确保将 'your_project_name' 替换为你实际的 Scrapy 项目名称。
