# 新闻爬虫与展示项目

这是一个使用 Scrapy 框架构建的新闻爬虫项目，并将抓取到的数据通过 Flask Web 应用进行展示。

## 功能

*   **多源新闻爬取**: 包含多个爬虫，用于从不同新闻网站抓取信息。
*   **Web 界面**: 使用 Flask 构建了一个简单的 Web 应用，用于浏览和搜索抓取到的新闻。
*   **数据库存储**: 将抓取到的新闻数据存储在 MySQL 数据库中。

## 已包含的爬虫

本项目目前包含以下新闻源的爬虫：

*   百度 (`baidu_spider`)
*   央视 (`cctv_spider`)
*   凤凰网 (`fenghuang_spider`)
*   网易 (`netease_spider`)
*   新浪 (`sina_spider`)
*   腾讯 (`tencent_spider`)
*   澎湃新闻 (`thepaper_spider`)
*   微博热搜 (`weibo_spider`)
*   知乎 (`zhihu_spider`)

## 技术栈

*   **爬虫**: Scrapy
*   **Web 框架**: Flask
*   **数据库**: MySQL
*   **数据库驱动**: PyMySQL
*   **数据库连接池**: DBUtils

## 环境要求

*   Python 3.x
*   pip (Python 包管理器)
*   MySQL 数据库服务

## 安装与设置

1.  **克隆仓库**:
    ```bash
    git clone <your-repository-url>
    cd news
    ```

2.  **安装依赖**: 
    本项目缺少 `requirements.txt` 文件。请根据需要手动安装以下主要依赖：
    ```bash
    pip install scrapy flask pymysql dbutils
    # 可能还需要安装其他 Scrapy 或 Flask 相关的依赖
    ```
    *建议创建一个 `requirements.txt` 文件以方便管理依赖。*

3.  **数据库配置**:
    *   确保你的 MySQL 服务正在运行。
    *   在 MySQL 中创建一个数据库 (例如 `news_db`)。
    *   修改 `app.py` 文件中的数据库连接信息 (HOST, USER, PASSWORD, DB)。
        ```python
        # app.py
        MYSQL_HOST = 'your_mysql_host' # 数据库主机
        MYSQL_USER = 'your_mysql_user'      # 数据库用户名
        MYSQL_PASSWORD = 'your_mysql_password' # 数据库密码
        MYSQL_DB = 'your_database_name'     # 数据库名称
        MYSQL_PORT = 3306 # 数据库端口 (通常是 3306)
        ```
    *   **重要**: Scrapy 的数据库配置通常在 `news/settings.py` 文件中。请确保 `settings.py` 中的数据库配置 (`ITEM_PIPELINES` 中启用的 Pipeline 所使用的配置) 与 `app.py` 一致，以便爬虫能正确写入数据。

## 如何运行

1.  **运行爬虫**:
    在项目根目录 (`news/`) 下执行以下命令来运行指定的爬虫：
    ```bash
    # 进入 Scrapy 项目目录 (如果不在根目录运行)
    # cd news 

    # 运行单个爬虫，例如微博爬虫
    scrapy crawl weibo_spider

    # 运行所有爬虫 (如果 run.py 脚本支持)
    # python run.py 
    ```
    *注意: `run.py` 的具体功能取决于其实现。*

2.  **运行 Web 应用**:
    在项目根目录 (`news/`) 下执行：
    ```bash
    python app.py
    ```
    应用默认会在 `http://0.0.0.0:5000` 或 `http://127.0.0.1:5000` 启动。在浏览器中打开此地址即可访问。

## 项目结构

```
news/
├── app.py             # Flask Web 应用入口
├── news/              # Scrapy 项目目录
│   ├── __init__.py
│   ├── items.py         # Scrapy Item 定义
│   ├── middlewares.py   # Scrapy 中间件
│   ├── pipelines.py     # Scrapy Pipeline (数据处理与存储)
│   ├── settings.py      # Scrapy 项目配置
│   └── spiders/         # 爬虫目录
│       ├── __init__.py
│       ├── baidu_spider.py
│       ├── ... (其他爬虫)
│       └── zhihu_spider.py
├── run.py             # (可能存在的) 运行爬虫的脚本
├── scrapy.cfg         # Scrapy 部署配置文件
├── templates/         # Flask HTML 模板目录
│   └── index.html
└── README.md          # 本文档
```

## 贡献

欢迎提交 Pull Requests 或报告 Issues。

## 许可证

Apache-2.0 license
