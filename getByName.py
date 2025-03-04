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
from utils.find_aweme import extract_aweme_ids

from config.headers_config import headers


def get_input():
    # 输入关键字，确保不为空
    while True:
        find_keyword = input("请输入查找关键字（不能为空）：").strip()
        if find_keyword:
            break
        else:
            print("关键字不能为空，请重新输入！")

    # 输入查找页数，确保为1到10之间的整数
    while True:
        try:
            pages = int(input("请输入查找页数（1到10之间的整数）："))
            if 1 <= pages <= 10:
                break
            else:
                print("页数必须在1到10之间，请重新输入！")
        except ValueError:
            print("输入无效，请输入一个整数！")
    print(f"查找关键字是：{find_keyword}，查找页数是：{pages}")
    return find_keyword, pages


keyword, pages = get_input()
# 打开浏览器
dp = ChromiumPage().latest_tab

# 监听数据包
dp.listen.start('/aweme/v1/web/general/search/stream/')
# 访问网站
dp.get(f'https://www.douyin.com/search/{keyword}')

for page in range(1, pages + 1):
    # 如果是第一次搜索，触发的是stream，后面的搜索触发的都是single
    if (page == 1):
        resp = dp.listen.wait()
        aweList = extract_aweme_ids(resp.response.body)
        print(f'正在采集第{page}页的数据内容，共{len(aweList)}条数据')
        for aweme_id in aweList:
            retry_count = 0  # 初始化重试计数器
            max_retries = 2  # 设置最大重试次数

            while retry_count < max_retries:  # 如果重试次数未达到上限，则继续尝试
                try:
                    url = f'https://www.douyin.com/discover?modal_id={aweme_id}'
                    res = requests.get(url, headers=headers)

                    html = res.text
                    info = re.findall('<script id="RENDER_DATA" type="application/json">(.*?)</script>', html)[0]
                    info_json = unquote(info)
                    json_data = json.loads(info_json)

                    # 提取视频链接
                    video_url = json_data['app']['videoDetail']['video']['bitRateList'][0]['playAddr'][0]['src']
                    # 提取视频标题
                    old_title = json_data['app']['videoDetail']['desc']
                    # 替换特殊字符
                    title = re.sub(r'[\\/:*"<>|\n]', '', old_title)

                    # 对于视频链接发送请求 + 获取视频内容
                    video_content = requests.get(url=video_url, headers=headers).content

                    # 数据保存
                    with open('video\\' + title + aweme_id + '.mp4', mode='wb') as f:
                        f.write(video_content)
                    print(title)
                    print(video_url)
                    break  # 如果成功完成操作，跳出 while 循环，继续下一个 aweme_id
                except Exception as e:
                    print(f"Error occurred for aweme_id {aweme_id}: {e}")
                    retry_count += 1  # 增加重试计数器
                    if retry_count >= max_retries:
                        print(f"Max retries reached for aweme_id {aweme_id}. Skipping...")
        dp.listen.start('/aweme/v1/web/general/search/single/')
        dp.scroll.to_bottom()
    else:
        resp = dp.listen.wait()
        aweList = resp.response.body['data']
        print(f'正在采集第{page}页的数据内容，共{len(aweList)}条数据')
        for aweme in aweList:
            retry_count = 0  # 初始化重试计数器
            max_retries = 2  # 设置最大重试次数
            while retry_count < max_retries:  # 如果重试次数未达到上限，则继续尝试
                try:
                    video_url = aweme['aweme_info']['video']['play_addr']['url_list'][0]
                    video_old_title = aweme['aweme_info']['desc']
                    video_title = re.sub(r'[\\/:*"<>|\n]', '', video_old_title)
                    video_id = aweme['aweme_info']['aweme_id']
                    video_content = requests.get(url=video_url, headers=headers).content
                    with open('video\\' + video_title + video_id + '.mp4', mode='wb') as f:
                        f.write(video_content)
                    print(video_title)
                    print(video_url)
                    break  # 如果成功完成操作，跳出 while 循环，继续下一个 aweme_id
                except Exception as e:
                    video_id = aweme['aweme_info']['aweme_id']
                    print(f"Error occurred for aweme_id {video_id}: {e}")
                    retry_count += 1  # 增加重试计数器
                    if retry_count >= max_retries:
                        print(f"Max retries reached for aweme_id {video_id}. Skipping...")
        dp.scroll.to_bottom()
