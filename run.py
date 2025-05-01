import subprocess
import os
import time
import sys

# 获取当前脚本所在的目录
# 这相当于批处理脚本中的 %~dp0
script_dir = os.path.dirname(os.path.abspath(__file__))

print("正在查找并准备启动所有 Scrapy spiders...")
# 查找 spiders 目录下的所有爬虫文件
spiders_dir = os.path.join(script_dir, 'news', 'spiders')
spider_files = [f for f in os.listdir(spiders_dir) if f.endswith('.py') and f != '__init__.py']
spider_names = [os.path.splitext(f)[0] for f in spider_files]

if not spider_names:
    print("错误：在 'news/spiders' 目录下未找到任何爬虫文件。")
    # sys.exit(1) # 如果没有爬虫是关键错误，则退出
else:
    print(f"找到以下爬虫: {', '.join(spider_names)}")
    # 构建在新窗口中顺序运行所有爬虫的命令
    # 使用 '&' 连接多个命令，使其在同一个 cmd 窗口中顺序执行
    crawl_commands = ' & '.join([f'scrapy crawl {name}' for name in spider_names])
    scrapy_command = f'start "Scrapy Spiders 控制台" cmd /k "{crawl_commands}"'

    # 使用 'start "Title" cmd /k' 在新窗口中打开，并在命令执行后保持窗口打开
    # 我们使用 shell=True 是因为 'start' 和 'cmd /k' 是 shell 命令
    try:
        # 使用 subprocess.Popen 异步运行命令 (不等待它完成)
        # 设置工作目录 (cwd) 为脚本所在的目录
        subprocess.Popen(
            scrapy_command,
            cwd=script_dir,
            shell=True
        )
        print("已在新窗口中发出启动所有 Scrapy spiders 的命令。")

    except Exception as e:
        print(f"启动 Scrapy spiders 时发生错误: {e}")
        # 如果此失败是关键的，可以选择在此处添加 sys.exit(1)

print("正在等待进程初始化...")
# 相当于 ping 127.0.0.1 -n 6 > nul (等待约 5 秒)
time.sleep(5)
print("等待完成。")

print("正在启动 Flask web 服务器...")
try:
    # 构造在新窗口中启动 Flask 服务器的命令
    flask_command = f'start "Flask Server 控制台" cmd /k "python app.py"'

    # 使用 subprocess.Popen 异步运行命令
    subprocess.Popen(
        flask_command,
        cwd=script_dir,
        shell=True
    )
    print("已在新窗口中发出启动 Flask web 服务器的命令。")

except Exception as e:
    print(f"启动 Flask 服务器时发生错误: {e}")
    # 如果此失败是关键的，可以选择在此处添加 sys.exit(1)

print("两个进程都已在单独的窗口中启动。")

# 原始批处理脚本末尾有一个 'pause'。
# 在从控制台运行的 Python 脚本中，控制台通常在执行完成后会保持打开。
# 如果你双击运行此脚本，并且希望窗口像批处理文件的 pause 那样保持打开，
# 你可以在这里添加 input("按 Enter 键退出...")。
# 但通常用于启动其他进程的脚本会直接退出。
# 我们只打印最后一条消息然后正常退出。
print("Python 脚本完成进程启动。")

