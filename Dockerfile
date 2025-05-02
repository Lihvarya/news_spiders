# 使用官方 Python 运行时作为父镜像
FROM python:3.12-slim

# 设置工作目录
WORKDIR /app

# 安装系统依赖 (如果需要，例如编译某些 Python 包可能需要)
# RUN apt-get update && apt-get install -y --no-install-recommends gcc && rm -rf /var/lib/apt/lists/*

# 复制依赖文件
# 注意：requirements.txt 中有重复项，pip 会安装最后一个指定的版本
COPY requirements.txt .

# 安装项目依赖 (包括 gunicorn 用于生产环境运行 Flask)
# 使用 --no-cache-dir 减少镜像大小
RUN pip install --no-cache-dir -r requirements.txt gunicorn

# 复制项目代码到工作目录
COPY . .

# 暴露 Flask 应用运行的端口 (app.py 中指定的是 8081)
EXPOSE 8081

# 定义容器启动时运行的命令
# 使用 gunicorn 运行 Flask 应用
# -w 4: 使用 4 个 worker 进程 (根据需要调整)
# -b 0.0.0.0:8080: 绑定到所有网络接口的 8081 端口
# app:app: 指向 app.py 文件中的 Flask 应用实例 app
CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:8081", "app:app"]