# 导入数据请求模块 pip install requests
import requests
# 导入正则表达式模块 内置模块
import re
# 导入解码方法
from urllib.parse import unquote
# 导入json模块
import json
# 导入格式化输出模块
# 导入自动化模块
from DrissionPage import ChromiumPage
# 导入所需工具以及配置
from utils.tools import extract_aweme_ids, get_by_name_input, get_comments_by_name_input
import csv
from config.headers_config import headers

# 获取所需要的关键字和页数
keyword, video_pages, comment_pages = get_comments_by_name_input()

# 打开浏览器
dp = ChromiumPage().latest_tab

# 监听数据包
dp.listen.start('/aweme/v1/web/general/search/stream/')

# 访问网站
dp.get(f'https://www.douyin.com/search/{keyword}')

# 设置输出文件
file = open(f'../data/user_ids.csv', mode='w', encoding='utf-8', newline='')
csv_writer = csv.DictWriter(file, fieldnames=['视频id'])
csv_writer.writeheader()

# 查找的视频id
video_ids = []

# 循环得到所有的视频id列表，并输出
for page in range(1, video_pages + 1):
    if page == 1:
        resp = dp.listen.wait()
        aweList = extract_aweme_ids(resp.response.body)
        video_ids = aweList
        dp.listen.start('/aweme/v1/web/general/search/single/')
        dp.wait(1)
        dp.scroll.to_bottom()

    else:
        resp = dp.listen.wait()
        aweList = resp.response.body['data']
        for aweme in aweList:
            aweme_id = aweme['aweme_info']['aweme_id']
            video_ids.append(aweme_id)
        dp.wait(1)
        dp.scroll.to_bottom()

# 输出所有的视频 id 到 csv 文件
for video_id in video_ids:
    video_dict = {'视频id': video_id}
    csv_writer.writerow(video_dict)

# 依次获取所有的视频评论
for page in range(1, comment_pages + 1):
    pass
