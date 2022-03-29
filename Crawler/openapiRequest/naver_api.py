import configparser
from urllib.parse import urlparse

import urllib.request
import requests
from sqlalchemy import create_engine

from tqdm import tqdm
import datetime

config = configparser.ConfigParser()
config.read('config.ini', encoding='utf-8')

# naver_openapi에 query 검색 결과 요청 함수
def request_naver(source, query, start):
    client_id = config['CRAWLING_CONFIG']['Naver_API_ID']
    client_secret = config['CRAWLING_CONFIG']['Naver_API_SECRET']
    header = {'X-Naver-Client-Id': client_id, 'X-Naver-Client-Secret': client_secret}
    encText = urllib.parse.quote(query)

    if source == 'blog':
        url = "https://openapi.naver.com/v1/search/blog.json?query=" + encText + "&display=100&sort=sim&start=" + str(start) # json 결과
    elif source == 'cafe':
        url = "https://openapi.naver.com/v1/search/cafearticle.json?query=" + encText + "&display=100&sort=sim&start=" + str(start) # json 결과
    elif source == 'news':
        url = "https://openapi.naver.com/v1/search/news.json?query=" + encText + "&display=100&sort=sim&start=" + str(start)  # json 결과

    r = requests.get(urlparse(url).geturl(), headers=header)
    if r.status_code == 200:
        return r.json()
    else:
        return r.status_code

# 결과 요청 및 json 응답 결과 중 원하는 결과 추출
def get_naver(source, query):
    list = []
    page = 0
    if source == 'blog':
        while page < 10:  # 검색 시작 위치로 최대 1000까지 가능
            json_obj = (request_naver(source, query, (page * 100) + 1))  # 한 페이지 당 최대 100개 가능
            for document in json_obj['items']:
                # postdate가 없는 경우 ex)http://simsulbo.egloos.com/1258395
                val = [document['title'].replace("<b>", "").replace("</b>", "").replace("amp;", ""),
                       document['description'].replace("<b>", "").replace("</b>", ""),
                       document['bloggername'], document['postdate'], document['link']]
                if '' in val:
                    continue
                else:
                    list.append(val)
            page += 1
            if json_obj['total'] < (page * 100): break
    elif source == 'cafe':
        while page < 10:  # 검색 시작 위치로 최대 1000까지 가능
            json_obj = (request_naver(source, query, (page * 100) + 1))  # 한 페이지 당 최대 100개 가능
            for document in json_obj['items']:
                val = [document['title'].replace("<b>", "").replace("</b>", "").replace("amp;", ""),
                       document['description'].replace("<b>", "").replace("</b>", ""),
                       document['cafename'], document['link']]
                if '' in val:
                    continue
                else:
                    list.append(val)
            page += 1
            if json_obj['total'] < (page * 100): break
    elif source == 'news':
        while page < 10:   # 검색 시작 위치로 최대 1000까지 가능
            json_obj = (request_naver(source, query, (page * 100) + 1))  # 한 페이지 당 최대 100개 가능
            for document in json_obj['items']:
                date = document['pubDate'][5:]
                date = date[:3]+str(datetime.datetime.strptime(date[3:6], "%b").month)+date[6:-6]
                val = [document['title'].replace("<b>", "").replace("</b>", "").replace("amp;", ""),
                       document['description'].replace("<b>", "").replace("</b>", ""),
                       document['originallink'], date, document['link']]
                if '' in val:
                    continue
                else:
                    list.append(val)
            page += 1
            if json_obj['total'] < (page * 100): break
    return list

# 추출된 결과 db에 입력
def url_naver(query, source):
    db_connection_str = config['MYSQL_CONFIG']['db_connection']
    db_connection = create_engine(db_connection_str)

    json_list_blog = get_naver(source, query)
    for i, list in enumerate(tqdm(json_list_blog)):
        try:
            if 'cafe.naver' in list[3]:
                source = 'naver_cafe'
                sql = "INSERT INTO api_url (title, content, name, url, search_keyword, source) " \
                        "values (%s, %s, %s, %s, %s, %s) ON DUPLICATE KEY UPDATE url=%s;"
                db_connection.execute(sql, (list[0]), (list[1]), list[2], list[3], query, source, list[3])
            elif 'blog.naver' in list[4]:
                source = 'naver_blog'
                sql = "INSERT INTO api_url(title, content, name, postdate, url, search_keyword, source) " \
                      "values (%s, %s, %s, %s, %s, %s, %s) ON DUPLICATE KEY UPDATE postdate=%s;"
                db_connection.execute(sql, (list[0]), (list[1]), list[2], list[3], list[4], query, source, list[3])
            elif 'blog.daum':
                source = 'daum_blog'
                sql = "INSERT INTO api_url(title, content, name, postdate, url, search_keyword, source) " \
                      "values (%s, %s, %s, %s, %s, %s, %s) ON DUPLICATE KEY UPDATE postdate=%s;"
                db_connection.execute(sql, (list[0]), (list[1]), list[2], list[3], list[4], query, source, list[3])
            else:
                source = 'unknown_channel'
                sql = "INSERT INTO api_url(title, content, name, postdate, url, search_keyword, source) " \
                      "values (%s, %s, %s, %s, %s, %s, %s) ON DUPLICATE KEY UPDATE postdate=%s;"
                db_connection.execute(sql, (list[0]), (list[1]), list[2], list[3], list[4], query, source, list[3])
        except Exception as e:
            print(e)