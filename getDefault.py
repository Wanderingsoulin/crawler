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

from config.headers_config import headers

# 打开浏览器
dp = ChromiumPage().latest_tab

# 监听数据包
dp.listen.start('/aweme/v1/web/module/feed/')
# 访问网站
dp.get('https://www.douyin.com/discover')

# 等待数据包加载
resp = dp.listen.wait(timeout=10)
aweList = resp.response.body['cards']
for awe in aweList:
    try:
        aweJson = json.loads(awe['aweme'])
        aweId = aweJson['aweme_id']
        oldTitle = aweJson['desc']
        title = re.sub(r'[\\/:*"<>|\n]', '', oldTitle)
        url = f'https://www.douyin.com?modal_id={aweId}'
        response = requests.get(url=url, headers=headers)
        html = response.text
        info = re.findall('<script id="RENDER_DATA" type="application/json">(.*?)</script>', html)[0]
        # 解码
        info_json = unquote(info)
        # 转成json字典数据
        json_data = json.loads(info_json)
        # 提取视频链接
        video_url = json_data['app']['videoDetail']['video']['bitRateList'][0]['playAddr'][0]['src']
        # 对于视频链接发送请求+获取视频内容
        video_content = requests.get(url=video_url, headers=headers).content
        with open('video\\' + title + aweId + '.mp4', mode='wb') as f:
            # 写入数据
            f.write(video_content)
        print(title)
        print(video_url)
    except Exception as e:
        print(e)
