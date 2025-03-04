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
# 导入数据处理
import pandas as pd
# 导入结巴分词
import jieba
# 导入词云图模块
import wordcloud


def input_environment():
    # 输入关键字，确保不为空
    while True:
        find_url = input("请输入查找视频链接（不能为空）：").strip()
        if find_url:
            break
        else:
            print("视频链接不能为空，请重新输入！")

    # 输入查找页数，确保为1到10之间的整数
    while True:
        try:
            find_pages = int(input("请输入查找页数（1到10之间的整数）："))
            if 1 <= find_pages <= 10:
                break
            else:
                print("页数必须在1到10之间，请重新输入！")
        except ValueError:
            print("输入无效，请输入一个整数！")
    print(f"查找视频链接是：{find_url}，查找页数是：{find_pages}")
    return find_url, find_pages


url, pages = input_environment()
# 设置输出文件
file = open(f'data\\comment.csv', mode='w', encoding='utf-8', newline='')
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

video_id=''

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

# 关闭文件，避免冲突
file.close()

# 读取文件
df = pd.read_csv(f'data\\{video_id}-comment.csv')
# 获取评论内容
content = ' '.join([str(i).replace('\n', '') for i in df['评论内容']])
# 分词处理
string = ''.join(jieba.lcut(content))
# 词云图配置
wc = wordcloud.WordCloud(
    font_path='C:/Windows/Fonts/msyh.ttc',
    width=1000,
    height=700,
    stopwords={'我们', '你们', '他们', '它们', '因为', '因而', '所以', '如果', '那么', '如此', '只是', '但是', '就是',
               '这是', '那是', '而是', '而且', '虽然', '这些', '有些', '然后', '已经', '于是', '一种', '一个', '一样',
               '时候', '没有', '什么', '这样', '这种', '这里', '不会', '一些', '这个', '仍然', '不是',
               '自己', '知道', '可以', '看到', '那儿', '问题', '一会儿', '一点', '现在', '两个', '三个'}
)
wc.generate(string)
# 导出词云图
wc.to_file('data\\{video_id}-comment.png')
