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
# 提取视频链接
video_url = json_data['app']['videoDetail']['video']['bitRateList'][0]['playAddr'][0]['src']
# 提取视频标题
title = json_data['app']['videoDetail']['desc']
"""保存数据"""
# 对于视频链接发送请求+获取视频内容
video_content = requests.get(url=video_url, headers=headers).content
# 数据保存
with open('../video/' + title + '.mp4', mode='wb') as f:
    # 写入数据
    f.write(video_content)
