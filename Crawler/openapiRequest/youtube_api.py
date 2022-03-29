import time
import pandas as pd
import configparser

from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from sqlalchemy import create_engine

# poetry add google-api-python-client
# poetry add google-auth-oauthlib google-auth-httplib2

config = configparser.ConfigParser()
config.read('config.ini', encoding='utf-8')

DEVELOPER_KEY = config['CRAWLING_CONFIG']['Youtube_DEVELOPER_KEY']
YOUTUBE_API_SERVICE_NAME = config['CRAWLING_CONFIG']['Youtube_YOUTUBE_API_SERVICE_NAME']
YOUTUBE_API_VERSION = config['CRAWLING_CONFIG']['Youtube_YOUTUBE_API_VERSION']
db_connection_str = config['MYSQL_CONFIG']['db_connection']

# youtube_openapi에 query 검색 결과 요청 함수
# def request_youtube_videoId(query):
#     youtube = build(YOUTUBE_API_SERVICE_NAME, YOUTUBE_API_VERSION, developerKey=DEVELOPER_KEY)
#
#     search_response = youtube.search().list(
#         q=query,
#         order="date",
#         part="snippet",
#         maxResults=100
#     ).execute()
#
#     result_list = []
#
#     for document in search_response['items']:
#         try:
#             val = [query, document['snippet']['title'],
#                    document['snippet']['channelTitle'],
#                    document['id']['videoId']]
#             result_list.append(val)
#         except:
#             continue
#
#     return result_list

# youtube_openapi에 query 검색 결과 요청 함수
def request_youtube(query):
    db_connection = create_engine(db_connection_str)
    youtube = build(YOUTUBE_API_SERVICE_NAME, YOUTUBE_API_VERSION, developerKey=DEVELOPER_KEY)

    search_response = youtube.search().list(
        q=query,
        order="date",
        part="snippet",
        maxResults=100
    ).execute()

    result_list = []
    urls =[]

    for document in search_response['items']:
        try:
            val = [query, document['snippet']['title'],
                   document['snippet']['channelTitle'],
                   document['id']['videoId']]
            result_list.append(val)
            urls.append(document['id']['videoId'])

            sql = "INSERT INTO api_url (search_keyword, url, source, title, name) VALUES (%s, %s, %s, %s, %s)" \
                  "ON DUPLICATE KEY UPDATE search_keyword=%s;"
            db_connection.execute(sql, (query, document['id']['videoId'], 'youtube_comment', document['snippet']['title'], document['snippet']['channelTitle'], query))
        except Exception as e:
            print('error:', e)
            continue
        break

    return result_list, urls

# 추출한 값 db에 저장
def url_youtube(query):
    request_youtube(query)

    db_connection = create_engine(db_connection_str)

    result = []
    comments = []
    api_obj = build(YOUTUBE_API_SERVICE_NAME, YOUTUBE_API_VERSION, developerKey=DEVELOPER_KEY)

    sql = "SELECT url FROM  api_url WHERE search_keyword = \'" +query+ "\' AND source= 'youtube_comment';"

    df = pd.read_sql(sql, db_connection)

    for i, url in enumerate(df.values.tolist()):
        url = url[0]
        id = 1
        try:
            sql = "INSERT INTO crawling_content (comment_seq, search_keyword, source, url, comment, author, commentdate, num_likes) " \
                  "SELECT %s, %s, %s, %s, %s, %s, %s, %s " \
                  "FROM DUAL WHERE NOT EXISTS (" \
                    "SELECT * FROM crawling_content WHERE comment_seq = %s AND url = %s AND comment = %s AND num_likes = %s)"
            response = api_obj.commentThreads().list(part='snippet,replies', videoId=url, maxResults=100).execute()
            while response:
                for item in response['items']:
                    comment = item['snippet']['topLevelComment']['snippet']
                    text = comment['textDisplay']
                    comments = [{'id': id, 'url': url, 'keyword': query, 'content': text,
                                 'author': comment['authorDisplayName'],
                                 'date': comment['publishedAt'].replace("-", ""), 'source': 'Youtube',
                                 'num_likes': comment['likeCount']}]
                    db_connection.execute(sql, (id, query, 'youtube_comment', url, text, comment['authorDisplayName'], comment['publishedAt'].replace("-", "")[:8], comment['likeCount'],
                                                id, url, text, comment['likeCount']))
                    id += 1

                    if item['snippet']['totalReplyCount'] > 0:
                        for reply_item in item['replies']['comments']:
                            reply = reply_item['snippet']
                            text = reply['textDisplay']
                            comments = [{'id': id, 'url': url, 'keyword': query, 'content': text,
                                         'author': reply['authorDisplayName'],
                                         'date': reply['publishedAt'].replace("-", ""), 'source': 'Youtube',
                                         'num_likes': reply['likeCount']}]
                            db_connection.execute(sql,
                                                  (id, query, 'youtube_comment', url, text, reply['authorDisplayName'],
                                                   reply['publishedAt'].replace("-", "")[:8], comment['likeCount'],
                                                                        id, url, text, comment['likeCount']))
                            id += 1
                if 'nextPageToken' in response:
                    response = api_obj.commentThreads().list(part='snippet,replies', videoId=url,
                                                             pageToken=response['nextPageToken'],
                                                             maxResults=100).execute()
                else:
                    break
            result.append(comments)
            time.sleep(0.4)
        except HttpError as err:
            print('index', i, 'error code', err)
    return result