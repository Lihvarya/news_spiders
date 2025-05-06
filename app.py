from flask import Flask, render_template, request, jsonify, redirect, url_for # Import redirect and url_for
import subprocess
import threading
import os
import pymysql
from dbutils.pooled_db import PooledDB
import logging
from datetime import datetime, timezone, timedelta

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# --- 数据库配置 (从 Scrapy settings 读取或直接配置) ---
# 理想情况下，这些配置应该与 Scrapy settings.py 保持一致或从同一配置文件读取
# 为了简化示例，这里直接硬编码，实际项目中建议使用更健壮的配置管理方式
MYSQL_HOST = '' # 数据库主机
MYSQL_USER = ''      # 数据库用户名 (请根据实际情况修改)
MYSQL_PASSWORD = '' # 数据库密码 (请根据实际情况修改)
MYSQL_DB = ''     # 数据库名称 (请根据实际情况修改)
MYSQL_PORT = 3306

# 创建数据库连接池
try:
    pool = PooledDB(
        creator=pymysql, # 使用 PyMySQL 作为数据库驱动
        maxconnections=6, # 连接池允许的最大连接数
        mincached=2, # 初始化时，连接池中至少创建的空闲的连接
        maxcached=5, # 连接池中最多闲置的连接
        maxshared=3, # 连接池中最多共享的连接
        blocking=True, # 连接池中如果没有可用连接后，是否阻塞等待
        maxusage=None, # 一个连接最多被重复使用的次数
        setsession=[], # 开始会话前执行的命令列表
        ping=0, # ping MySQL 服务端，检查是否服务可用
        host=MYSQL_HOST,
        port=MYSQL_PORT,
        user=MYSQL_USER,
        password=MYSQL_PASSWORD,
        database=MYSQL_DB,
        charset='utf8mb4',
        cursorclass=pymysql.cursors.DictCursor # 返回字典形式的游标
    )
    logging.info("Database connection pool created successfully.")
except Exception as e:
    logging.error(f"Error creating database connection pool: {e}")
    pool = None # 标记连接池创建失败

app = Flask(__name__)

# 全局变量，用于记录最后一次运行爬虫的时间 (UTC)
last_spider_run_time_utc = None

# --- 路由定义 ---

@app.route('/')
def index():
    """首页，展示新闻列表。客户端JS处理按来源筛选。"""
    if not pool:
        return "Database connection pool is not available.", 500

    conn = None
    cursor = None
    try:
        conn = pool.connection() # 从连接池获取连接
        cursor = conn.cursor()

        # For the main index page, fetch a reasonable number of the latest articles
        # from ALL sources. The client-side JS will handle filtering display.
        # Fetching more items here allows the client-side filter to work on more data
        # without another server request. Adjust LIMIT as needed.
        sql = """SELECT title, author, publish_time, summary, source, link
               FROM news_articles
               ORDER BY id DESC LIMIT 300""" # Increased limit to provide more data for client-side grouping/filtering
        params = ()
        cursor.execute(sql, params)
        news_list = cursor.fetchall()
        logging.info(f"Fetched {len(news_list)} latest news articles for index page.")

        # Pass the full list of fetched news to the template.
        # The template will group them by source, and JS will handle which groups are initially visible.
        last_run_beijing_time_str = None
        if last_spider_run_time_utc:
            beijing_tz = timezone(timedelta(hours=8))
            last_run_beijing_time = last_spider_run_time_utc.replace(tzinfo=timezone.utc).astimezone(beijing_tz)
            last_run_beijing_time_str = last_run_beijing_time.strftime('%Y-%m-%d %H:%M:%S')

        return render_template('index.html', news_list=news_list, last_run_time=last_run_beijing_time_str)

    except Exception as e:
        logging.error(f"Error fetching news from database for index page: {e}")
        return f"Error fetching news: {e}", 500
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close() # 将连接放回连接池

@app.route('/search')
def search():
    """处理搜索请求，结果在index模板中展示并按来源分组。"""
    query = request.args.get('q', '')
    if not query:
        # If no search term, redirect to the index page
        return redirect(url_for('index'))

    if not pool:
        return "Database connection pool is not available.", 500

    conn = None
    cursor = None
    try:
        conn = pool.connection()
        cursor = conn.cursor()
        # In title and summary search (using LIKE)
        # Limit search results to a reasonable number
        sql = """SELECT title, author, publish_time, summary, source, link
               FROM news_articles
               WHERE title LIKE %s OR summary LIKE %s
               ORDER BY id DESC LIMIT 100""" # Limit search results
        search_term = f"%{query}%"
        cursor.execute(sql, (search_term, search_term))
        results = cursor.fetchall()
        logging.info(f"Found {len(results)} results for search query: '{query}'")
        # Pass results and query to the template. The template will group results by source.
        last_run_beijing_time_str = None
        if last_spider_run_time_utc:
            beijing_tz = timezone(timedelta(hours=8))
            last_run_beijing_time = last_spider_run_time_utc.replace(tzinfo=timezone.utc).astimezone(beijing_tz)
            last_run_beijing_time_str = last_run_beijing_time.strftime('%Y-%m-%d %H:%M:%S')

        return render_template('index.html', results=results, query=query, last_run_time=last_run_beijing_time_str)
    except Exception as e:
        logging.error(f"Error searching news in database: {e}")
        return f"Error searching news: {e}", 500
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

# Example detail route (optional - implement if needed)
# @app.route('/detail/<source_name>')
# def detail_source(source_name):
#     """Placeholder route to show all news from a specific source (optional)."""
#     # You would fetch all news for source_name_spider here
#     # and render a dedicated template or list them on a single page
#     return f"Showing all news for source: {source_name}"

# Function to run spiders in a separate thread
def run_spiders_background():
    # List of spider names based on index.html buttons (adjust if needed)
    spider_names = [
        'weibo_spider', 'baidu_spider', 'sina_spider', 'tencent_spider',
        'netease_spider', 'thepaper_spider', 'cctv_spider', 'fenghuang_spider'
        # Add other spider names if they exist (e.g., 'ithome_spider', 'toutiao_spider', etc.)
    ]
    # Determine the Scrapy project directory (assuming app.py is in the root with scrapy.cfg)
    scrapy_project_dir = os.path.dirname(os.path.abspath(__file__))

    # Verify scrapy.cfg exists in the determined directory
    scrapy_cfg_path = os.path.join(scrapy_project_dir, 'scrapy.cfg')
    if not os.path.exists(scrapy_cfg_path):
        logging.error(f"Scrapy configuration file 'scrapy.cfg' not found in '{scrapy_project_dir}'. Cannot run spiders.")
        return

    logging.info(f"Starting spider execution in background from directory: {scrapy_project_dir}")
    for spider_name in spider_names:
        command = ['scrapy', 'crawl', spider_name]
        try:
            # Run each crawl command sequentially within the background thread
            logging.info(f"Running command: {' '.join(command)} in {scrapy_project_dir}")
            # Use subprocess.run and wait for completion. Capture output.
            # Set check=False to manually check return code and log errors.
            process = subprocess.run(command, cwd=scrapy_project_dir, capture_output=True, text=True, check=False, encoding='utf-8') # Specify encoding

            if process.returncode == 0:
                logging.info(f"Successfully ran spider: {spider_name}")
                # Log stdout only if needed and not too verbose
                # logging.debug(f"Output for {spider_name}:\n{process.stdout}")
            else:
                logging.error(f"Error running spider {spider_name}. Return code: {process.returncode}")
                logging.error(f"Stderr for {spider_name}:\n{process.stderr}")
                logging.error(f"Stdout for {spider_name}:\n{process.stdout}")

        except FileNotFoundError:
            logging.error(f"Error: 'scrapy' command not found. Make sure Scrapy is installed, activated in the environment, and accessible in the system's PATH.")
            # Stop trying if scrapy command is not found
            break
        except Exception as e:
            logging.error(f"An unexpected error occurred while running spider {spider_name}: {e}")
            # Optionally log stdout/stderr on unexpected errors too
            # if 'process' in locals():
            #     logging.error(f"Stderr: {getattr(process, 'stderr', 'N/A')}")
            #     logging.error(f"Stdout: {getattr(process, 'stdout', 'N/A')}")

    global last_spider_run_time_utc
    last_spider_run_time_utc = datetime.utcnow()
    logging.info(f"Finished background spider execution process. Last run time UTC: {last_spider_run_time_utc}")

@app.route('/run-all-spiders', methods=['POST'])
def run_all_spiders():
    """Endpoint to trigger running all spiders in a background thread."""
    logging.info("Received request to run all spiders.")
    try:
        # Start the spider execution in a background thread
        thread = threading.Thread(target=run_spiders_background, daemon=True) # Use daemon thread
        thread.start()
        logging.info("Background thread started for spider execution.")
        return jsonify({'message': '所有爬虫已开始后台运行。请稍后刷新页面查看最新数据。'}), 202 # 202 Accepted
    except Exception as e:
        logging.error(f"Failed to start background thread for spiders: {e}")
        return jsonify({'message': '启动爬虫后台任务失败。'}), 500


# --- 运行 Flask 应用 ---
# --- 运行 Flask 应用 ---
if __name__ == '__main__':
    # 注意：在生产环境中，不应使用 Flask 自带的开发服务器
    # 应使用 Gunicorn 或 uWSGI 等 WSGI 服务器部署
    # debug=True should be False in production
    app.run(debug=True, host='0.0.0.0', port=5000)
