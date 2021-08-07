# -*- encoding:utf-8 -*-
"""
@作者：踏着七色云彩
@问题名：爬新浪微博
@时间：2021/4/15  
"""

import requests
import time
import pandas as pd
import pymysql
from sqlalchemy import create_engine

# 获取微博数据
# 以微博热搜 #文科生太多会影响国家发展吗# 为研究对象，爬取相关微博

print("开始爬取微博数据")
data = list()
headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; U; CPU iPhone OS 4_3_3 like Mac OS X; en-us) AppleWebKit/533.17.9 (KHTML, like Gecko) Version/5.0.2 Mobile/8J2 Safari/6533.18.5"
}
# 总共抓取55页
total_page_number_to_crawl = 10
target_url = "https://m.weibo.cn/api/container/getIndex?containerid=100103type%3D61%26q%3D%E7%96%AB%E6%83%85%26t%3D0&page_type=searchall&page=5"
for page in range(total_page_number_to_crawl):
    print('Crawl Page: %d/%d' % (page + 1, total_page_number_to_crawl))
    url = target_url + str(page)
    resp = requests.get(url, headers=headers)
    time.sleep(4)
    resp_data = resp.json()['data']
    for card in resp_data['cards'] if 'cards' in resp_data else []:
        if 'mblog' in card:
            data.append(card['mblog'])
print("爬取成功，已存入data列表里")

# 将微博数据写入数据库

print("开始将数据写入mysql数据库")
# 准备数据 Mblog
mblog_data = [
    {
        'mid': t['mid'],
        'comments_count': t['comments_count'],
        'created_at': t['created_at'],
        'source': t['source'],
        'text': t['text'],
        'user_id': str(t['user']['id'])
    } for t in data
]
mblog_df = pd.DataFrame(mblog_data).drop_duplicates(['mid'])

# 准备数据User
user_data = [
    {
        'user_id': t['user']['id'],
        'description': t['user']['description'],
        'follow_count': t['user']['follow_count'],
        'followers_count': t['user']['followers_count'],
        'gender': t['user']['gender'],
        'profile_url': t['user']['profile_url'],
        'screen_name': t['user']['screen_name'],
        'statuses_count': t['user']['statuses_count']
    } for t in data if 'user' in t
]
user_df = pd.DataFrame(user_data).drop_duplicates(['user_id'])

# 创建数据库连接

engine = create_engine('mysql+pymysql://root:1234@127.0.0.1:3306/pweibo?charset=utf8mb4', echo=False)
user_df.to_sql(name='user', con=engine, if_exists='append', index=False)
mblog_df.to_sql(name='mblog', con=engine, if_exists='append', index=False)
print("写入成功")
