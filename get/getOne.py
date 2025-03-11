# 导入数据请求模块 pip install requests
import os

import requests
# 导入正则表达式模块 内置模块
import re
# 导入解码方法
from urllib.parse import unquote
# 导入json模块
import json

from config.headers_config import headers

url = 'https://www.douyin.com/discover?modal_id=7474109141796031783'
res = requests.get(url, headers=headers)

html = res.text
info = re.findall('<script id="RENDER_DATA" type="application/json">(.*?)</script>', html)[0]
info_json = unquote(info)
json_data = json.loads(info_json)

# 获取视频相关信息，包括视频链接、视频标题等
video_url = json_data['app']['videoDetail']['video']['bitRateList'][0]['playAddr'][0]['src']
title = json_data['app']['videoDetail']['desc']

# # 获取视频的作者信息，包括id，昵称，关注数量等
# author_id = json_data['app']['videoDetail']['authorInfo']['uid']
# author_name = json_data['app']['videoDetail']['authorInfo']['nickname']
# author_followers = json_data['app']['videoDetail']['authorInfo']['followerCount']
#
# # 获取视频的统计数据，包括评论总数comment，推荐总数digg，分享总数share，
# stats_comments = json_data['app']['videoDetail']['stats']['commentCount']
# stats_digg = json_data['app']['videoDetail']['stats']['diggCount']
# stats_share = json_data['app']['videoDetail']['stats']['shareCount']


"""保存数据"""
# 对于视频链接发送请求+获取视频内容
video_content = requests.get(url=video_url, headers=headers).content
# 数据保存
with open('../video/' + title + '.mp4', mode='wb') as f:
    # 写入数据
    f.write(video_content)
