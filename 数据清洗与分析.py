# -*- encoding:utf-8 -*-
"""
@作者：踏着七色云彩
@问题名：数据清洗与分析
@时间：2021/4/17  
"""

import pandas as pd
import pymysql
from sqlalchemy import create_engine
import matplotlib.pyplot as plt
import jieba
import jieba.analyse
import re
from collections import Counter
from wordcloud import WordCloud
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.datasets import load_iris
from sklearn.linear_model import LogisticRegression

# 数据导入

engine = create_engine('mysql+pymysql://root:1234@127.0.0.1:3306/pweibo?charset=utf8mb4', echo=False)
user_dataframe = pd.read_sql_table("user", con=engine)
weibo_dataframe = pd.read_sql_table("mblog", con=engine)


# 数据分析

# # 非空型检验
# def analyze_empty_string(dataframe, column_name):
#     total_length = len(dataframe)
#     valid_length = len(dataframe[dataframe[column_name] != ""])
#     print("Analyze Column[%s]: %d/%d, Ratio is %f" % (column_name,valid_length, total_length, valid_length/total_length))
# # 检验用户的个人描述非空率
# analyze_empty_string(user_dataframe,'description')
# 数值统计
# 统计用户性别比例，以柱状图的形式展现
# user_dataframe.groupby('gender').size().plot.bar()
# # 统计用户关注了多少博主，以柱状图的形式展现（横坐标是关注博主数量，纵坐标是用户数量)
# user_dataframe.hist('follow_count', bins=20, )
# 统计每条微博评论数，及相关微博数
# weibo_dataframe.hist('comments_count', bins=20)
# plt.savefig('gender.jpg')
# plt.show()

# 文本分析
# 1.1数据清洗（只留下中文）
def cleanse_text(value):
    if value:
        text = "".join(re.findall(r"[\u4e00-\u9fff]+", value))
        return text if len(text) > 0 else None
    else:
        return None


# 2.1 jieba分词
weibo_dataframe['text_clean'] = weibo_dataframe.text.apply(lambda t: cleanse_text(t))
words_cleanse = weibo_dataframe.text_clean.apply(lambda t: list(jieba.cut(t)))


# 1.2再次清洗（去除停词） 为了高词频统计
def stopwords_list(flie_path):
    stopwords = set([line.strip() for line in open(flie_path, 'r', encoding='utf-8').readlines()])
    return stopwords


stop_words_cn = stopwords_list('./停词库/cn_stopwords.txt')
words_cleanse_remove_stopwords = [list(filter(lambda w: w not in stop_words_cn, words)) for words in words_cleanse]

# 3.词频统计
word_freq = Counter([w for words in words_cleanse_remove_stopwords for w in words])
word_freq_df = pd.DataFrame(word_freq.items())
word_freq_df.columns = ['word', 'count']
# 以‘count’大小降序排序，取出前十
print(word_freq_df.sort_values('count', ascending=0).head(20))

# # 2.2将分词结果（为未去除停词）写入数据库
# weibo_tokenize = weibo_dataframe.apply(lambda r:(r['mid'], [w for w in jieba.cut(r['text_clean']) if w not in stop_words_cn]),axis=1)
# weibo_word_df = pd.DataFrame([(t[0], w) for t in weibo_tokenize for w in t[1]])
# weibo_word_df.columns = ['mid', 'word']
# weibo_word_df.to_sql(name='mblogword',con=engine,if_exists='append',index=False)
# print("写入成功")

# 4.词云分析
# 将高频词转化为dict
top_k = 100
word_freq_dict = dict(list(
    word_freq_df.sort_values('count', ascending=0).head(top_k).apply(lambda row: (row['word'], row['count']), axis=1)))
print()
# 产生词云
wc = WordCloud(font_path="simkai.ttf",
               background_color="white",
               scale=20
               )
wc.generate_from_frequencies(word_freq_dict)
plt.imshow(wc)

# 显示词云
plt.axis("off")
plt.figure(dpi=1000)
# plt.show()

# 保存到文件
wc.to_file("wordcloud.png")


# 5.文本向量化
# Tf-idf模型 关键词抽取
# 对数据集进行批量处理
# weibo_keywords = weibo_dataframe.apply(lambda r: (r['mid'], [w for w in
#                                                              jieba.analyse.extract_tags(r['text_clean'], topK=5,
#                                                                                         withWeight=False, allowPOS=())
#                                                              if w not in stop_words_cn]), axis=1)
# weibo_keywords.df = pd.DataFrame([(t[0], w) for t in weibo_keywords for w in t[1]])
# weibo_keywords.df.columns = ['mid', 'keyword']

# 将关键词进行数值转化-基于词袋模型，用sklearn的CountVectorizer实现
# 将关键词通过分隔符链接起来
weibo_keywords_text = weibo_dataframe.apply(lambda r: '|'.join(
    [w for w in jieba.analyse.extract_tags(r['text_clean'], topK=5, withWeight=False, allowPOS=()) if
     w not in stop_words_cn]), axis=1).tolist()
# 构造CountVectorizer
vectorizer = CountVectorizer(max_features=1000, analyzer='word', tokenizer=lambda s: s.split('|'))
# 词频矩阵，元素aij，j词在i类文本下的词频(微博条数为行，列数为词数，你设定值)
weibo_bow = vectorizer.fit_transform(weibo_keywords_text)
# # 获取词袋中所有文本的关键字
# feature_name = vectorizer.get_feature_names()

# 6.数据建模
# 转为excel

# t = weibo_dataframe[['mid', 'text_clean']]
# t.to_excel('sentiment.xlsx')

# 手动在Excel中sentiment字段下人工标注情感值，总共标记100条微博，微博总数436：
# 1：赞成
# 0：既不赞成也不反对；与本热搜无关；陈述事实
# -1：反对；对这个问题的提出持贬义


# 在Excel里手动导出.CSV文件后，引入文件
train_data = pd.read_csv('sentiment.CSV',encoding='gb18030')

# 检查数据中是否有缺失值
print('检查数据中是否有缺失值,True为有缺失值')
# Flase:对应特征的特征值中无缺失值
# True：有缺失值
print(train_data.isnull().any())

# 缺失值处理
# 删除包含缺失值的行
# 当然原数据dataframe也是没有改变的，需要添加参数inplace=True，才可以改变原数据。
train_data.dropna(inplace=True)

# 检查
print('再次检查')
print(train_data.isnull().any())
print('检查结束')


# X 是词频，y是预测的情感分析结果（1,0，-1）
y = train_data.Sentiment
X = weibo_bow[:len(y), :]
# 训练模型
clf = LogisticRegression(random_state=0,solver='lbfgs',multi_class='multinomial').fit(X,y)
# # 训练数据打分(在训练数据集上)
# print(clf.score(X,y))

# 7.模型应用
# 得到y
sentiment_values = clf.predict(weibo_bow)
# 可视化
# 统计情感值各有多少个，生成一个字典
sentiment_dist = Counter(sentiment_values)
# 转为dataframe结构
sentiment_dist_df = pd.DataFrame(sentiment_dist.items())
sentiment_dist_df.columns = ['Sentiment_Value','Count']
# 将情感值作为索引，就不用dataframe默认的索引了
sentiment_dist_df = sentiment_dist_df.set_index('Sentiment_Value')
sentiment_dist_df.plot.bar()
# plt.savefig('sentiment.jpg')
# plt.show()

# # 一些正面微博的例子
# print('一些正面微博的例子')
# print(weibo_dataframe.text_clean[sentiment_values == 1].head(10))
# # 一些中性微博的例子
# print('一些中性微博的例子')
# print(weibo_dataframe.text_clean[sentiment_values == 0].head(10))
# # 一些负面微博的例子
# print('一些负面微博的例子')
# print(weibo_dataframe.text_clean[sentiment_values == -1].head(10))
