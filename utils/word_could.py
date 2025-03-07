import jieba
import pandas as pd
from wordcloud import wordcloud

# 读取文件
df = pd.read_csv(f'../data/comment.csv')
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
wc.to_file('../data/comment.png')