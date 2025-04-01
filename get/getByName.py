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
from utils.tools import extract_aweme_ids, get_by_name_input, get_current_date
from config.headers_config import headers
import os
import datetime
import pandas as pd

# 提示用户输入
keyword, pages = get_by_name_input()
video_dir = f'D:/download/douyin-datas/video/{keyword}'  # 新增目录路径变量
os.makedirs(video_dir, exist_ok=True)  # 自动创建目录

# 设置视频信息写入文件
file = open(f'../data/video_relation.csv', mode='a', encoding='utf-8', newline='')
csv_writer = csv.DictWriter(file,
                            fieldnames=['video_title', 'author_id', 'author_name', 'author_followers', 'stats_comments',
                                        'stats_digg', 'stats_share', 'video_id', 'video_url', 'video_createTime',
                                        'search_keywords', 'download_time'])

# 仅在文件不存在或为空时写入表头
if file.tell() == 0:
    csv_writer.writeheader()

# 读取已有video_id到集合
existing_ids = set()
try:
    with open('../data/video_relation.csv', 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            existing_ids.add(row['video_id'])
    print(f"已加载 {len(existing_ids)} 个现有视频ID")
except FileNotFoundError:
    print("未找到历史数据文件，将从头开始采集")

# 打开浏览器，监听/stream数据包，并根据关键字访问
dp = ChromiumPage().latest_tab
dp.listen.start('/aweme/v1/web/general/search/stream/')
dp.get(f'https://www.douyin.com/search/{keyword}')

def update_keywords_in_csv(video_id: str, new_keyword: str, csv_path: str) -> None:
    """更新CSV文件中指定视频ID的关键词"""
    try:
        # 读取CSV文件
        df = pd.read_csv(csv_path)
        # 找到匹配的行
        mask = df['video_id'] == video_id
        if not df[mask].empty:
            # 获取当前的keywords
            current_keywords = df.loc[mask, 'search_keywords'].iloc[0]
            # 如果新关键词不在现有关键词中，则添加
            if new_keyword not in str(current_keywords).split(','):
                df.loc[mask, 'search_keywords'] = current_keywords + ',' + new_keyword
                # 保存更新后的CSV
                df.to_csv(csv_path, index=False)
                print(f"已更新视频ID {video_id} 的关键词: {current_keywords + ',' + new_keyword}")
    except Exception as e:
        print(f"更新关键词时出错: {e}")

for page in range(1, pages + 1):
    # 如果是第一次搜索，触发的是stream，后面的搜索触发的都是single
    if (page == 1):
        resp = dp.listen.wait()
        aweList = extract_aweme_ids(resp.response.body)
        print(f'正在采集第{page}页的数据内容，共{len(aweList)}条数据')
        for video_id in aweList:
            if video_id in existing_ids:
                print(f"跳过已存在的视频ID: {video_id}")
                update_keywords_in_csv(video_id, keyword, '../data/video_relation.csv')
                continue
            retry_count = 0  # 初始化重试计数器
            max_retries = 1  # 设置最大重试次数

            while retry_count < max_retries:  # 如果重试次数未达到上限，则继续尝试
                try:
                    url = f'https://www.douyin.com/discover?modal_id={video_id}'
                    res = requests.get(url, headers=headers)
                    html = res.text
                    info = re.findall('<script id="RENDER_DATA" type="application/json">(.*?)</script>', html)[0]
                    info_json = unquote(info)
                    json_data = json.loads(info_json)

                    # 获取视频相关信息，包括视频链接、视频标题等
                    video_url = json_data['app']['videoDetail']['video']['bitRateList'][0]['playAddr'][0]['src']
                    # 检查视频URL是否以https://sf开头
                    if video_url.startswith(('https://sf', 'https://lf')):
                        print(f"跳过图文视频: {video_url}")
                        break
                    old_title = json_data['app']['videoDetail']['desc']
                    # 替换特殊字符
                    title = re.sub(r'[\\/:*"<>|\n]', '', old_title)
                    createTimeMap = json_data['app']['videoDetail']['createTime']
                    video_createTime = datetime.datetime.utcfromtimestamp(createTimeMap)

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
                        'video_id': video_id,
                        'video_url': video_url,
                        'video_createTime': video_createTime,
                        'search_keywords': keyword,
                        'download_time': get_current_date()
                    }
                    csv_writer.writerow(video_relation)

                    # 对于视频链接发送请求 + 获取视频内容
                    video_content = requests.get(url=video_url, headers=headers).content
                    with open(os.path.join(video_dir, video_id + '.mp4'), mode='wb') as f:
                        f.write(video_content)
                    print(title)
                    print(video_url)
                    break  # 如果成功完成操作，跳出 while 循环，继续下一个 video_id
                except Exception as e:
                    print(f"Error occurred for video_id {video_id}: {e}")
                    retry_count += 1  # 增加重试计数器
                    if retry_count >= max_retries:
                        print(f"Max retries reached for video_id {video_id}. Skipping...")
        dp.listen.start('/aweme/v1/web/general/search/single/')
        dp.scroll.to_bottom()
    else:
        resp = dp.listen.wait()
        aweList = resp.response.body['data']
        print(f'正在采集第{page}页的数据内容，共{len(aweList)}条数据')
        for aweme in aweList:
            try:
                video_id = aweme['aweme_info']['aweme_id']
            except KeyError:
                print(f"无效的视频数据结构: {aweme}")
                continue

            if video_id in existing_ids:
                print(f"跳过已存在的视频ID: {video_id}")
                update_keywords_in_csv(video_id, keyword, '../data/video_relation.csv')
                continue
            retry_count = 0  # 初始化重试计数器
            max_retries = 1  # 设置最大重试次数
            while retry_count < max_retries:  # 如果重试次数未达到上限，则继续尝试
                try:
                    # 获取视频相关信息，包括视频链接、视频标题等
                    video_url = aweme['aweme_info']['video']['play_addr']['url_list'][0]
                    # 检查视频URL是否以https://sf开头
                    if video_url.startswith(('https://sf', 'https://lf')):
                        print(f"跳过图文视频: {video_url}")
                        break
                    video_old_title = aweme['aweme_info']['desc']
                    video_title = re.sub(r'[\\/:*"<>|\n]', '', video_old_title)
                    video_createTime = aweme['aweme_info']['create_time']

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
                        'video_url': video_url,
                        'video_createTime': video_createTime,
                        'search_keywords': keyword,
                        'download_time': get_current_date()
                    }
                    csv_writer.writerow(video_relation)

                    video_content = requests.get(url=video_url, headers=headers).content
                    with open(os.path.join(video_dir, video_id + '.mp4'), mode='wb') as f:
                        f.write(video_content)
                    print(video_title)
                    print(video_url)
                    break  # 如果成功完成操作，跳出 while 循环，继续下一个 video_id
                except Exception as e:
                    print(f"Error occurred: {e}")
                    retry_count += 1  # 增加重试计数器
                    if retry_count >= max_retries:
                        print(f"Max retries reached. Skipping...")
        dp.scroll.to_bottom()
