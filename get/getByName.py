import csv
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
from utils.tools import extract_aweme_ids, get_by_name_input
from config.headers_config import headers

# 提示用户输入
keyword, pages = get_by_name_input()

# 设置视频信息写入文件
file = open(f'../data/video_relation.csv', mode='w', encoding='utf-8', newline='')
csv_writer = csv.DictWriter(file,
                            fieldnames=['video_title', 'author_id', 'author_name', 'author_followers', 'stats_comments',
                                        'stats_digg', 'stats_share', 'video_id', 'video_url'])
csv_writer.writeheader()

# 打开浏览器，监听/stream数据包，并根据关键字访问
dp = ChromiumPage().latest_tab
dp.listen.start('/aweme/v1/web/general/search/stream/')
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

                    # 获取视频相关信息，包括视频链接、视频标题等
                    video_url = json_data['app']['videoDetail']['video']['bitRateList'][0]['playAddr'][0]['src']
                    old_title = json_data['app']['videoDetail']['desc']
                    # 替换特殊字符
                    title = re.sub(r'[\\/:*"<>|\n]', '', old_title)

                    # 获取视频的作者信息，包括id，昵称，关注数量等
                    author_id = json_data['app']['videoDetail']['authorInfo']['uid']
                    author_name = json_data['app']['videoDetail']['authorInfo']['nickname']
                    author_followers = json_data['app']['videoDetail']['authorInfo']['followerCount']

                    # 获取视频的统计数据，包括评论总数comment，推荐总数digg，分享总数share，
                    stats_comments = json_data['app']['videoDetail']['stats']['commentCount']
                    stats_digg = json_data['app']['videoDetail']['stats']['diggCount']
                    stats_share = json_data['app']['videoDetail']['stats']['shareCount']

                    # 构建输出文件字典，将信息写入到文件中保存
                    video_relation = {
                        'video_title': title,
                        'author_id': author_id,
                        'author_name': author_name,
                        'author_followers': author_followers,
                        'stats_comments': stats_comments,
                        'stats_digg': stats_digg,
                        'stats_share': stats_share,
                        'video_id': aweme_id,
                        'video_url': video_url
                    }
                    csv_writer.writerow(video_relation)

                    # 对于视频链接发送请求 + 获取视频内容
                    video_content = requests.get(url=video_url, headers=headers).content
                    with open('../video/' + title + aweme_id + '.mp4', mode='wb') as f:
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
                    # 获取视频相关信息，包括视频链接、视频标题等
                    video_url = aweme['aweme_info']['video']['play_addr']['url_list'][0]
                    video_old_title = aweme['aweme_info']['desc']
                    video_title = re.sub(r'[\\/:*"<>|\n]', '', video_old_title)
                    video_id = aweme['aweme_info']['aweme_id']

                    # 获取视频的作者信息，包括id，昵称，关注数量等
                    author_id = aweme['aweme_info']['author']['uid']
                    author_name = aweme['aweme_info']['author']['nickname']
                    author_followers = aweme['aweme_info']['author']['follower_count']

                    # 获取视频的统计数据，包括评论总数comment，推荐总数digg，分享总数share
                    stats_comments = aweme['aweme_info']['statistics']['comment_count']
                    stats_digg = aweme['aweme_info']['statistics']['digg_count']
                    stats_share = aweme['aweme_info']['statistics']['share_count']

                    # 构建输出文件字典，将信息写入到文件中保存
                    video_relation = {
                        'video_title': video_title,
                        'author_id': author_id,
                        'author_name': author_name,
                        'author_followers': author_followers,
                        'stats_comments': stats_comments,
                        'stats_digg': stats_digg,
                        'stats_share': stats_share,
                        'video_id': video_id,
                        'video_url': video_url
                    }
                    csv_writer.writerow(video_relation)

                    video_content = requests.get(url=video_url, headers=headers).content
                    with open('../video/' + video_title + video_id + '.mp4', mode='wb') as f:
                        f.write(video_content)
                    print(video_title)
                    print(video_url)
                    break  # 如果成功完成操作，跳出 while 循环，继续下一个 aweme_id
                except Exception as e:
                    print(f"Error occurred: {e}")
                    retry_count += 1  # 增加重试计数器
                    if retry_count >= max_retries:
                        print(f"Max retries reached. Skipping...")
        dp.scroll.to_bottom()
