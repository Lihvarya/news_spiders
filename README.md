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
*   Docker (如果选择使用 Docker 部署)

## 安装与设置 (非 Docker)

1.  **克隆仓库**:
    ```bash
    git clone <your-repository-url> # 请替换为实际的仓库 URL
    cd news
    ```

2.  **安装依赖**:
    建议在虚拟环境中安装依赖：
    ```bash
    python -m venv venv
    source venv/bin/activate # Linux/macOS
    # venv\Scripts\activate # Windows
    pip install -r requirements.txt
    ```

3.  **数据库配置**:
    *   确保你的 MySQL 服务正在运行。
    *   在 MySQL 中创建一个数据库 (例如 `news_db`) 并确保使用 `utf8mb4` 字符集。
    *   **重要**: 请在以下两个文件中修改数据库连接信息，确保它们一致：
        *   `app.py` (Flask 应用)
        *   `news/settings.py` (Scrapy 爬虫)
    *   需要修改的变量包括：
        ```python
        MYSQL_HOST = 'your_mysql_host'       # 数据库主机 (e.g., '127.0.0.1')
        MYSQL_USER = 'your_mysql_user'       # 数据库用户名
        MYSQL_PASSWORD = 'your_mysql_password' # 数据库密码
        MYSQL_DB = 'your_database_name'      # 数据库名称 (e.g., 'news_db')
        MYSQL_PORT = 3306                  # 数据库端口 (通常是 3306)
        ```
    *   *注意：直接在代码中硬编码凭据不安全。在生产环境中，强烈建议使用环境变量或配置文件管理敏感信息。*

## 如何运行 (非 Docker)

1.  **运行爬虫**:
    在项目根目录 (包含 `scrapy.cfg` 文件的目录) 下执行以下命令来运行指定的爬虫：
    ```bash
    # 确保虚拟环境已激活
    # source venv/bin/activate 或 venv\Scripts\activate

    # 运行单个爬虫，例如微博爬虫
    scrapy crawl weibo_spider

    # 运行百度爬虫
    scrapy crawl baidu_spider

    # ...运行其他爬虫...
    ```
    *(可选) 如果 `run.py` 脚本用于批量运行爬虫，可以尝试：*
    ```bash
    python run.py
    ```
    *请检查 `run.py` 的具体实现以了解其功能。*
    *或者，可以通过 Flask 应用界面提供的按钮来触发所有爬虫的后台运行（如果该功能已实现）。*

2.  **运行 Web 应用**:
    在项目根目录 (包含 `app.py` 文件的目录) 下执行：
    ```bash
    # 确保虚拟环境已激活
    python app.py
    ```
    应用默认会在 `http://127.0.0.1:5000` 启动 (或者根据你的网络配置可能是 `http://0.0.0.0:5000`)。在浏览器中打开此地址即可访问新闻展示界面。

## 使用 Docker 运行

Docker 提供了一种容器化的部署方式，可以简化环境配置。

### 方式一: 从源代码构建

如果你希望自行构建镜像，可以使用项目提供的 `Dockerfile`。

1.  **配置**: 确保 `app.py` 和 `news/settings.py` 中的数据库连接信息指向你的 MySQL 服务器地址（注意：如果 MySQL 也运行在 Docker 中，可能需要使用 Docker 网络地址，而不是 `localhost` 或 `127.0.0.1`）。或者，修改 Dockerfile 和代码以从环境变量读取数据库配置。

2.  **构建 Docker 镜像**:
    在项目根目录下执行：
    ```bash
    docker build -t news-app:latest .
    ```
    `.dockerignore` 文件会确保构建镜像时忽略不必要的文件。

3.  **运行 Docker 容器**:
    ```bash
    docker run --name news-web -d -p 8081:8081 news-app:latest
    # --name news-web: 给容器命名为 news-web
    # -d: 在后台运行
    # -p 8081:8081: 将宿主机的 8081 端口映射到容器的 8081 端口
    ```
    *如果需要传递数据库环境变量（假设代码已修改为支持），可以添加 `-e` 参数:*
    ```bash
    # docker run --name news-web -d -p 8081:8081 \
    #  -e MYSQL_HOST='your_db_host_accessible_from_docker' \
    #  -e MYSQL_USER='your_user' \
    #  -e MYSQL_PASSWORD='your_password' \
    #  -e MYSQL_DB='your_db' \
    #  news-app:latest
    ```
    容器启动后，可以通过 `http://localhost:8081` (或服务器 IP:8081) 访问 Web 应用。Dockerfile 使用 `gunicorn` 运行 Flask 应用。

### 方式二: 使用预构建镜像 (一键部署)

如果你想快速启动应用而无需手动构建，可以使用预构建的 Docker 镜像。

1.  **拉取 Docker 镜像**:
    ```bash
    docker pull lihvarya/news:v1.0
    ```

2.  **运行 Docker 容器**:
    ```bash
    docker run --name news-web -d -p 8081:8081 lihvarya/news:v1.0
    ```
    *同样，需要确保容器可以访问你的 MySQL 数据库。如果预构建镜像 `lihvarya/news:v1.0` 支持环境变量配置，可以使用 `-e` 参数传入数据库连接信息，否则需要确保镜像内置的配置或默认配置与你的环境匹配。*
    ```bash
    # docker run --name news-web -d -p 8081:8081 \
    #  -e MYSQL_HOST='your_db_host_accessible_from_docker' \
    #  -e MYSQL_USER='your_user' \
    #  -e MYSQL_PASSWORD='your_password' \
    #  -e MYSQL_DB='your_db' \
    #  lihvarya/news:v1.0
    ```
    启动后通过 `http://localhost:8081` 访问。

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
├── requirements.txt   # 项目依赖
└── README.md          # 本文档
```





## 贡献

欢迎提交 Pull Requests 或报告 Issues。

## 许可证

Apache-2.0 license
