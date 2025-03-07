# 导入数据请求模块 pip install requests
import requests
# 导入正则表达式模块 内置模块
import re
# 导入解码方法
from urllib.parse import unquote
# 导入json模块
import json
# 导入自动化模块
from DrissionPage import ChromiumPage
# 导入格式化输出函数
from pprint import pprint
# 导入项目工具类
from config.headers_config import headers
# 导入csv文件写入
import csv
# 导入工具类
from utils.tools import get_by_url_input

url, pages = get_by_url_input()

# 设置输出文件
file = open(f'../data/comment.csv', mode='w', encoding='utf-8', newline='')
csv_writer = csv.DictWriter(file, fieldnames=['用户id', '评论内容', '评论者昵称', '评论者ip地址'])
csv_writer.writeheader()

# 打开浏览器
dp = ChromiumPage().latest_tab

# 监听数据包
dp.listen.start('/aweme/v1/web/comment/list/')
# 访问网站
dp.get(url)
# 等待两秒，元素加载
dp.wait(2)
# 点击评论按钮
comment_button = dp.ele("@data-e2e=feed-comment-icon")
comment_button.click(by_js=None)
# 获取侧边评论栏
comment_aside = dp.ele("@data-e2e=comment-list")

video_id = ''

for page in range(1, pages + 1):
    resp = dp.listen.wait()
    comments = resp.response.body['comments']
    # 获取到视频的唯一id，作为文件名称
    if page == 1:
        video_id = comments[0]['aweme_id']
    for comment in comments:
        # 评论唯一id
        cid = comment['cid']
        # 评论内容
        text = comment['text']
        # 评论者昵称
        user_nickname = comment['user']['nickname']
        # 评论者ip地址
        user_ip_address = comment['ip_label']

        # 构建字典用于存放信息
        comment_dict = {
            '用户id': cid,
            '评论内容': text,
            '评论者昵称': user_nickname,
            '评论者ip地址': user_ip_address
        }
        print(comment_dict)
        csv_writer.writerow(comment_dict)
    dp.wait(1)
    comment_aside.scroll.to_bottom()
