import configparser
import tweepy
from sqlalchemy import create_engine

from TwitterAPI import TwitterAPI

import datetime
import requests

config = configparser.ConfigParser()
config.read('config.ini', encoding='utf-8')

# twitter_openapi에 query 검색 결과 요청 함수 _ 실시간 조회
def request_twitter_REAL(query):
    result = []
    query = query.replace('+', '')

    client = tweepy.Client(bearer_token= config['CRAWLING_CONFIG']['twitter_bear_token'],
                           consumer_key=config['CRAWLING_CONFIG']['twitter_consumer_key'],
                           consumer_secret=config['CRAWLING_CONFIG']['twitter_consumer_secret'],
                           access_token=config['CRAWLING_CONFIG']['twitter_access_token'],
                           access_token_secret=config['CRAWLING_CONFIG']['twitter_access_token_secret'],
                           return_type=requests.Response,
                           wait_on_rate_limit=True)

    tweets = client.search_recent_tweets(query=query,
                                         tweet_fields=['author_id', 'created_at'],
                                         max_results=100)

    tweets_dict = tweets.json()
    try:
        tweets_data = tweets_dict['data']
        for item in tweets_data:
            date = item['created_at'][:10]
            # print(item)
            # date = str(datetime.datetime.strptime(date[4:7], "%b").month)+ date[7:20] + date[26:] # 원본 Mon Feb 07 05:04:18 +0000 2022 가공
            # date = datetime.datetime.strptime(date, "%m %d %H:%M:%S %Y")
            try:
                url = 'https://twitter.com/%s/status/%s' % (item['author_id'], item['id'])
                val = [item['id'], item['text'], item['author_id'], date, url]
            except:
                val = ['', '', '', '', '']
            result.append(val)
    except:
        result = []

    return result

# twitter_openapi에 query 검색 결과 요청 함수 _ 전체 조회
def request_twitter_WHOLE(query):
    auth = tweepy.OAuthHandler(config['CRAWLING_CONFIG']['twitter_consumer_key'], config['CRAWLING_CONFIG']['twitter_consumer_secret'])
    auth.set_access_token(config['CRAWLING_CONFIG']['twitter_access_token'], config['CRAWLING_CONFIG']['twitter_access_token_secret'])

    api = tweepy.API(auth)

    result = []
    location = "%s,%s,%s" % ("35.95", "128.25", "1000km")  # 검색기준(대한민국 중심) 좌표, 반지름
    cursor = tweepy.Cursor(api.search_tweets,
                           q=query,
                           count=100,  # 페이지당 반환할 트위터 수 최대 100
                           geocode=location,  # 검색 반경 조건
                           include_entities=True)

    for i, tweet in enumerate(cursor.items()):
        dic = {}
        url = 'https://twitter.com/%s/status/%s' % (tweet.user.screen_name, tweet.id)
        dic['id'] = tweet.id
        dic['content'] = tweet.text
        dic['author'] = tweet.user.screen_name
        dic['postdate'] = tweet.created_at.replace(tzinfo=None)  # TypeError 2: offset-naive and offset-aware datetimes 해결
        dic['url'] = url
        dic['num_likes'] = tweet.favorite_count
        result.append(dic)

    return result

# 결과 요청 및 json 응답 결과 중 원하는 값 db에 저장
def get_url_twitter(query):
    db_connection = create_engine(config['MYSQL_CONFIG']['db_connection'])

    result = []

    tweets = request_twitter_WHOLE(query)

    for tweet in enumerate(tweets):
        tweet = tweet[1]
        source = 'twitter'
        try:
            sql = "INSERT INTO crawling_content (comment_seq, search_keyword, source, url, comment, author, commentdate, num_likes) VALUES (%s, %s, %s, %s, %s, %s, %s, %s) ON DUPLICATE KEY UPDATE num_likes=%s;"

            db_connection.execute(sql, (tweet['id'], query, source, tweet['url'], tweet['content'], tweet['author'], tweet['postdate'].strftime("%Y-%m-%d"), tweet['num_likes'], tweet['num_likes']))
            print(tweet['url'], ' done')
        except Exception as e:
            print(e)

    return result