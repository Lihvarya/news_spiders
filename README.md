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
    ```

## 使用 Docker 运行

本项目提供了 Dockerfile，方便使用 Docker 进行构建和运行。

### 构建 Docker 镜像

在项目根目录下执行以下命令构建 Docker 镜像：

```bash
docker build -t news-app .
```

`.dockerignore` 文件会确保构建镜像时忽略不必要的文件（如 `.git` 目录、虚拟环境、缓存文件等），从而减小镜像体积并提高构建速度。

### 运行 Docker 容器

使用以下命令运行 Docker 容器：

```bash
docker run -p 8081:8081 news-app
```

这将在后台启动容器，并将容器内的 8081 端口映射到宿主机的 8081 端口。你可以通过访问 `http://localhost:8081` 来查看 Web 应用。

Dockerfile 使用 `gunicorn` 作为 WSGI 服务器来运行 Flask 应用，配置了 4 个 worker 进程，并监听 `0.0.0.0:8081`。

```bash
    git clone <your-repository-url>
    cd news
    ```

## 使用 Docker 运行

本项目提供了 Dockerfile，方便使用 Docker 进行构建和运行。

### 构建 Docker 镜像

在项目根目录下执行以下命令构建 Docker 镜像：

```bash
docker build -t news-app .
```

`.dockerignore` 文件会确保构建镜像时忽略不必要的文件（如 `.git` 目录、虚拟环境、缓存文件等），从而减小镜像体积并提高构建速度。

### 运行 Docker 容器

使用以下命令运行 Docker 容器：

```bash
docker run -p 8081:8081 news-app
```

这将在后台启动容器，并将容器内的 8081 端口映射到宿主机的 8081 端口。你可以通过访问 `http://localhost:8081` 来查看 Web 应用。

Dockerfile 使用 `gunicorn` 作为 WSGI 服务器来运行 Flask 应用，配置了 4 个 worker 进程，并监听 `0.0.0.0:8081`。

```

2.  **安装依赖**: 
    使用 `requirements.txt` 文件安装所有必要的依赖：
    ```

## 使用 Docker 运行

本项目提供了 Dockerfile，方便使用 Docker 进行构建和运行。

### 构建 Docker 镜像

在项目根目录下执行以下命令构建 Docker 镜像：

```bash
docker build -t news-app .
```

`.dockerignore` 文件会确保构建镜像时忽略不必要的文件（如 `.git` 目录、虚拟环境、缓存文件等），从而减小镜像体积并提高构建速度。

### 运行 Docker 容器

使用以下命令运行 Docker 容器：

```bash
docker run -p 8081:8081 news-app
```

这将在后台启动容器，并将容器内的 8081 端口映射到宿主机的 8081 端口。你可以通过访问 `http://localhost:8081` 来查看 Web 应用。

Dockerfile 使用 `gunicorn` 作为 WSGI 服务器来运行 Flask 应用，配置了 4 个 worker 进程，并监听 `0.0.0.0:8081`。

```bash
    pip install -r requirements.txt
    ```

## 使用 Docker 运行

本项目提供了 Dockerfile，方便使用 Docker 进行构建和运行。

### 构建 Docker 镜像

在项目根目录下执行以下命令构建 Docker 镜像：

```bash
docker build -t news-app .
```

`.dockerignore` 文件会确保构建镜像时忽略不必要的文件（如 `.git` 目录、虚拟环境、缓存文件等），从而减小镜像体积并提高构建速度。

### 运行 Docker 容器

使用以下命令运行 Docker 容器：

```bash
docker run -p 8081:8081 news-app
```

这将在后台启动容器，并将容器内的 8081 端口映射到宿主机的 8081 端口。你可以通过访问 `http://localhost:8081` 来查看 Web 应用。

Dockerfile 使用 `gunicorn` 作为 WSGI 服务器来运行 Flask 应用，配置了 4 个 worker 进程，并监听 `0.0.0.0:8081`。

```

3.  **数据库配置**:
    *   确保你的 MySQL 服务正在运行。
    *   在 MySQL 中创建一个数据库 (例如 `news_db`)。
    *   **重要**: 请在以下两个文件中修改数据库连接信息，确保它们一致：
        *   `app.py` (Flask 应用)
        *   `news/settings.py` (Scrapy 爬虫)
    *   需要修改的变量包括：
        ```

## 使用 Docker 运行

本项目提供了 Dockerfile，方便使用 Docker 进行构建和运行。

### 构建 Docker 镜像

在项目根目录下执行以下命令构建 Docker 镜像：

```bash
docker build -t news-app .
```

`.dockerignore` 文件会确保构建镜像时忽略不必要的文件（如 `.git` 目录、虚拟环境、缓存文件等），从而减小镜像体积并提高构建速度。

### 运行 Docker 容器

使用以下命令运行 Docker 容器：

```bash
docker run -p 8081:8081 news-app
```

这将在后台启动容器，并将容器内的 8081 端口映射到宿主机的 8081 端口。你可以通过访问 `http://localhost:8081` 来查看 Web 应用。

Dockerfile 使用 `gunicorn` 作为 WSGI 服务器来运行 Flask 应用，配置了 4 个 worker 进程，并监听 `0.0.0.0:8081`。

```python
        MYSQL_HOST = 'your_mysql_host'       # 数据库主机
        MYSQL_USER = 'your_mysql_user'       # 数据库用户名
        MYSQL_PASSWORD = 'your_mysql_password' # 数据库密码
        MYSQL_DB = 'your_database_name'      # 数据库名称
        MYSQL_PORT = 3306                  # 数据库端口 (通常是 3306)
        ```

## 使用 Docker 运行

本项目提供了 Dockerfile，方便使用 Docker 进行构建和运行。

### 构建 Docker 镜像

在项目根目录下执行以下命令构建 Docker 镜像：

```bash
docker build -t news-app .
```

`.dockerignore` 文件会确保构建镜像时忽略不必要的文件（如 `.git` 目录、虚拟环境、缓存文件等），从而减小镜像体积并提高构建速度。

### 运行 Docker 容器

使用以下命令运行 Docker 容器：

```bash
docker run -p 8081:8081 news-app
```

这将在后台启动容器，并将容器内的 8081 端口映射到宿主机的 8081 端口。你可以通过访问 `http://localhost:8081` 来查看 Web 应用。

Dockerfile 使用 `gunicorn` 作为 WSGI 服务器来运行 Flask 应用，配置了 4 个 worker 进程，并监听 `0.0.0.0:8081`。

```
    *   *注意：当前配置直接硬编码在代码中。在生产环境中，建议使用环境变量或配置文件管理敏感信息。*

## 如何运行

1.  **运行爬虫**:
    在项目根目录 (包含 `scrapy.cfg` 文件的目录) 下执行以下命令来运行指定的爬虫：
    ```

## 使用 Docker 运行

本项目提供了 Dockerfile，方便使用 Docker 进行构建和运行。

### 构建 Docker 镜像

在项目根目录下执行以下命令构建 Docker 镜像：

```bash
docker build -t news-app .
```

`.dockerignore` 文件会确保构建镜像时忽略不必要的文件（如 `.git` 目录、虚拟环境、缓存文件等），从而减小镜像体积并提高构建速度。

### 运行 Docker 容器

使用以下命令运行 Docker 容器：

```bash
docker run -p 8081:8081 news-app
```

这将在后台启动容器，并将容器内的 8081 端口映射到宿主机的 8081 端口。你可以通过访问 `http://localhost:8081` 来查看 Web 应用。

Dockerfile 使用 `gunicorn` 作为 WSGI 服务器来运行 Flask 应用，配置了 4 个 worker 进程，并监听 `0.0.0.0:8081`。

```bash
    # 运行单个爬虫，例如微博爬虫
    scrapy crawl weibo_spider

    # 运行百度爬虫
    scrapy crawl baidu_spider

    # ...运行其他爬虫...

    # (可选) 如果 `run.py` 脚本用于批量运行爬虫，可以尝试：
    # python run.py 
    ```

## 使用 Docker 运行

本项目提供了 Dockerfile，方便使用 Docker 进行构建和运行。

### 构建 Docker 镜像

在项目根目录下执行以下命令构建 Docker 镜像：

```bash
docker build -t news-app .
```

`.dockerignore` 文件会确保构建镜像时忽略不必要的文件（如 `.git` 目录、虚拟环境、缓存文件等），从而减小镜像体积并提高构建速度。

### 运行 Docker 容器

使用以下命令运行 Docker 容器：

```bash
docker run -p 8081:8081 news-app
```

这将在后台启动容器，并将容器内的 8081 端口映射到宿主机的 8081 端口。你可以通过访问 `http://localhost:8081` 来查看 Web 应用。

Dockerfile 使用 `gunicorn` 作为 WSGI 服务器来运行 Flask 应用，配置了 4 个 worker 进程，并监听 `0.0.0.0:8081`。

```
    *注意: `run.py` 的具体功能取决于其实现。请查看该文件以了解其用途。*
    *或者，你可以通过 Flask 应用界面提供的按钮来触发所有爬虫的后台运行。*

2.  **运行 Web 应用**:
    在项目根目录 (包含 `app.py` 文件的目录) 下执行：
    ```

## 使用 Docker 运行

本项目提供了 Dockerfile，方便使用 Docker 进行构建和运行。

### 构建 Docker 镜像

在项目根目录下执行以下命令构建 Docker 镜像：

```bash
docker build -t news-app .
```

`.dockerignore` 文件会确保构建镜像时忽略不必要的文件（如 `.git` 目录、虚拟环境、缓存文件等），从而减小镜像体积并提高构建速度。

### 运行 Docker 容器

使用以下命令运行 Docker 容器：

```bash
docker run -p 8081:8081 news-app
```

这将在后台启动容器，并将容器内的 8081 端口映射到宿主机的 8081 端口。你可以通过访问 `http://localhost:8081` 来查看 Web 应用。

Dockerfile 使用 `gunicorn` 作为 WSGI 服务器来运行 Flask 应用，配置了 4 个 worker 进程，并监听 `0.0.0.0:8081`。

```bash
    python app.py
    ```

## 使用 Docker 运行

本项目提供了 Dockerfile，方便使用 Docker 进行构建和运行。

### 构建 Docker 镜像

在项目根目录下执行以下命令构建 Docker 镜像：

```bash
docker build -t news-app .
```

`.dockerignore` 文件会确保构建镜像时忽略不必要的文件（如 `.git` 目录、虚拟环境、缓存文件等），从而减小镜像体积并提高构建速度。

### 运行 Docker 容器

使用以下命令运行 Docker 容器：

```bash
docker run -p 8081:8081 news-app
```

这将在后台启动容器，并将容器内的 8081 端口映射到宿主机的 8081 端口。你可以通过访问 `http://localhost:8081` 来查看 Web 应用。

Dockerfile 使用 `gunicorn` 作为 WSGI 服务器来运行 Flask 应用，配置了 4 个 worker 进程，并监听 `0.0.0.0:8081`。

```
    应用默认会在 `http://127.0.0.1:5000` 启动 (或者根据你的网络配置可能是 `http://0.0.0.0:5000`)。在浏览器中打开此地址即可访问新闻展示界面。

## 项目结构

```

## 使用 Docker 运行

本项目提供了 Dockerfile，方便使用 Docker 进行构建和运行。

### 构建 Docker 镜像

在项目根目录下执行以下命令构建 Docker 镜像：

```bash
docker build -t news-app .
```

`.dockerignore` 文件会确保构建镜像时忽略不必要的文件（如 `.git` 目录、虚拟环境、缓存文件等），从而减小镜像体积并提高构建速度。

### 运行 Docker 容器

使用以下命令运行 Docker 容器：

```bash
docker run -p 8081:8081 news-app
```

这将在后台启动容器，并将容器内的 8081 端口映射到宿主机的 8081 端口。你可以通过访问 `http://localhost:8081` 来查看 Web 应用。

Dockerfile 使用 `gunicorn` 作为 WSGI 服务器来运行 Flask 应用，配置了 4 个 worker 进程，并监听 `0.0.0.0:8081`。

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

## 使用 Docker 运行

本项目提供了 Dockerfile，方便使用 Docker 进行构建和运行。

### 构建 Docker 镜像

在项目根目录下执行以下命令构建 Docker 镜像：

```bash
docker build -t news-app .
```

`.dockerignore` 文件会确保构建镜像时忽略不必要的文件（如 `.git` 目录、虚拟环境、缓存文件等），从而减小镜像体积并提高构建速度。

### 运行 Docker 容器

使用以下命令运行 Docker 容器：

```bash
docker run -p 8081:8081 news-app
```

这将在后台启动容器，并将容器内的 8081 端口映射到宿主机的 8081 端口。你可以通过访问 `http://localhost:8081` 来查看 Web 应用。

Dockerfile 使用 `gunicorn` 作为 WSGI 服务器来运行 Flask 应用，配置了 4 个 worker 进程，并监听 `0.0.0.0:8081`。

```

## 贡献

欢迎提交 Pull Requests 或报告 Issues。

## 许可证

Apache-2.0 license
