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
from utils.tools import get_by_url_input

user_url, pages = get_by_url_input()
# 打开浏览器
dp = ChromiumPage()
# 监听数据包
dp.listen.start('/aweme/v1/web/aweme/post/')
# 访问网站
dp.get(user_url)
# 构建循环翻页
for page in range(1, pages+1):
    print(f'正在采集第{page}页的数据内容')
    # 等待数据包加载
    resp = dp.listen.wait()
    # 获取响应数据
    video_info_json = resp.response.body
    # 提取视频ID所在列表
    video_id_list = video_info_json['aweme_list']

    # for循环遍历, 提取列表里面元素
    for index in video_id_list:
        try:
            video_id = index['aweme_id']

            # url地址: 请求网址
            url = f'https://www.douyin.com/discover?modal_id={video_id}'
            # 发送请求
            response = requests.get(url=url, headers=headers)
            """获取数据: 获取响应文本数据"""
            html = response.text
            """解析数据: 提取我们需要的数据内容"""
            info = re.findall('<script id="RENDER_DATA" type="application/json">(.*?)</script>', html)[0]
            # 解码
            info_json = unquote(info)
            # 转成json字典数据
            json_data = json.loads(info_json)
            # 提取视频链接
            video_url = json_data['app']['videoDetail']['video']['bitRateList'][0]['playAddr'][0]['src']
            # 提取视频标题
            old_title = json_data['app']['videoDetail']['desc']
            # 替换特殊字符
            title = re.sub(r'[\\/:*"<>|\n]', '', old_title)
            """保存数据"""
            # 对于视频链接发送请求+获取视频内容
            video_content = requests.get(url=video_url, headers=headers).content
            # 数据保存
            with open('../video/' + title + video_id + '.mp4', mode='wb') as f:
                # 写入数据
                f.write(video_content)
            print(title)
            print(video_url)
        except Exception as e:
            print(e)
    dp.scroll.to_see(".Rcc71LyU")
