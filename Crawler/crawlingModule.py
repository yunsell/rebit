import configparser
import time
import random

from Crawler.extractFactor.daum_extract import daum_blog_comment
from Crawler.extractFactor.naver_extract import naver_blog_content, naver_blog_comment, naver_cafe_comment
from Crawler.openapiRequest.daum_api import url_daum
from Crawler.openapiRequest.naver_api import url_naver
from Crawler.openapiRequest.twitter_api import get_url_twitter
from Crawler.openapiRequest.youtube_api import url_youtube

import pandas as pd
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

from sqlalchemy import create_engine

class crawlingModule:
    def __init__(self):
        config = configparser.ConfigParser()
        config.read('config.ini', encoding='utf-8')

        options = Options()

        options.add_argument(
            'user-agent=' + "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.54 Safari/537.36")
        options.add_argument('headless')
        options.add_argument('--window-size= 360, 360')  # 실행되는 브라우저 크기를 지정할 수 있습니다.
        options.add_argument('--blink-settings=imagesEnabled=false')  # 브라우저에서 이미지 로딩을 하지 않습니다.

        path = '/home/drsong/python/rebit/chromedriver' # linux server

        self.driver = webdriver.Chrome(executable_path=path,
                                  options=options)

        db_connection_str = config['MYSQL_CONFIG']['db_connection']
        self.db_connection = create_engine(db_connection_str)

    def naver_blog_content_Crawler(self, query):
        sql = "SELECT A.postdate, A.url, A.title FROM api_url A LEFT OUTER JOIN crawling_content B ON A.url = B.url WHERE A.source = 'naver_blog' AND B.url is NULL AND A.search_keyword = \'"+query+"\';"

        df = pd.read_sql(sql, self.db_connection)
        url_list = df['url'].values.tolist()

        for i, url in enumerate(url_list):
            print(i, '번째', url, end=' ')
            if 'naver' in url:
                src = 'naver_blog_content'
                content, gong, cmt = naver_blog_content(self.driver, url)
            elif 'daum' in url:
                src = 'daum_blog_content'
                content = ('daum')
                gong = 0
                cmt = 0
            else:
                src = 'etc'
                content = ('기타')
                gong = 0
                cmt = 0

            sql = "INSERT INTO crawling_content (comment_seq, search_keyword, url, comment, source, commentdate, num_gonggam, num_likes) " \
                  "SELECT %s, %s, %s, %s, %s, %s, %s, %s " \
                  "FROM DUAL WHERE NOT EXISTS (" \
                  "SELECT * FROM crawling_content WHERE comment_seq = %s AND url = %s AND source = %s)"
            try:
                self.db_connection.execute(sql, (1, query, url, content, src, df['postdate'][i], gong, cmt, 1, url, src))
            except:
                self.db_connection.execute(sql, (1, query, url, '특수문자_인식불가', src, df['postdate'][i], gong, cmt,  1, url, src))
            time.sleep(random.uniform(2, 4))
            print('done')

    def naver_blog_comment_Crawler(self, query):
        sql = "SELECT A.url FROM api_url A LEFT OUTER JOIN crawling_content B ON A.url = B.url WHERE A.source = 'naver_blog' AND B.url is NULL AND A.search_keyword = \'"+query+"\';"
        df = pd.read_sql(sql, self.db_connection)
        url_list = df['url'].values.tolist()

        for i, url in enumerate(url_list):
            print(i, '번째', url, end = ' ')
            results = naver_blog_comment(self.driver, url)
            if len(results)>0:
                sql = "INSERT INTO crawling_content (comment_seq, search_keyword, source, url, comment, author, commentdate) " \
                      "SELECT %s, %s, %s, %s, %s, %s, %s " \
                      "FROM DUAL WHERE NOT EXISTS (" \
                      "SELECT * FROM crawling_content WHERE comment_seq = %s AND url = %s AND source = %s)"
                for j, result in enumerate(results):
                    try:
                        num = result[2].rfind('.')
                        self.db_connection.execute(sql, (j+1, query, 'naver_blog_comment', url, result[1], result[0], result[2][:num] + result[2][num+1:], j+1, url, 'naver_blog_comment'))
                    except Exception as e:
                        print(e)
            else:
                sql = "INSERT INTO crawling_content (comment_seq, search_keyword, source, url) " \
                      "SELECT %s, %s, %s, %s " \
                      "FROM DUAL WHERE NOT EXISTS (" \
                      "SELECT * FROM crawling_content WHERE comment_seq = %s AND url = %s AND source=%s)"
                print('no comment', end= ' ')
                try:
                    self.db_connection.execute(sql, (0, query, 'naver_blog_comment', url, 0, url, 'naver_blog_comment'))
                except Exception as e:
                    print(e)
            print('done')
            time.sleep(random.uniform(2, 4))


    def naver_cafe_comment_Crawler(self, query):
        sql = "SELECT A.url FROM api_url A LEFT OUTER JOIN crawling_content B ON A.url = B.url WHERE A.source = 'naver_cafe' AND B.url is NULL AND A.search_keyword = \'"+query+"\';"
        df = pd.read_sql(sql, self.db_connection)
        url_list = df['url'].values.tolist()

        for i, url in enumerate(url_list):
            # url = 'https://cafe.naver.com/feko/5763292'  # 댓글 O
            # url = 'https://cafe.naver.com/clutorius/49038'  # 비공개 게시글
            # url = 'https://cafe.naver.com/hirake/64303' # 댓글 X
            print(i, '번째', url, end=' ')
            results = naver_cafe_comment(self.driver, url)
            if results == False:
                print('비공개 게시글입니다', end = ' ')
            elif len(results)>0:
                # sql = "INSERT INTO crawling_content (comment_seq, search_keyword, source, url) VALUES (%s, %s, %s, %s) " \
                #       "ON DUPLICATE KEY UPDATE url=%s;"

                sql = "INSERT INTO crawling_content (comment_seq, search_keyword, source, url, comment, author, commentdate) " \
                      "SELECT %s, %s, %s, %s, %s, %s, %s " \
                      "FROM DUAL WHERE NOT EXISTS (" \
                      "SELECT * FROM crawling_content WHERE comment_seq = %s AND url = %s AND source=%s)"
                for j, result in enumerate(results):
                    try:
                        self.db_connection.execute(sql, (j+1, query, 'naver_cafe_comment', url, result[1], result[0], result[2], j+1, url, 'naver_cafe_comment'))
                    except Exception as e:
                        print(e)
            else:
                # sql = "INSERT INTO crawling_content (comment_seq, search_keyword, source, url) VALUES (%s, %s, %s, %s) " \
                #       "ON DUPLICATE KEY UPDATE url=%s;"

                sql = "INSERT INTO crawling_content (comment_seq, search_keyword, source, url) " \
                      "SELECT %s, %s, %s, %s " \
                      "FROM DUAL WHERE NOT EXISTS (" \
                      "SELECT * FROM crawling_content WHERE comment_seq = %s AND url = %s AND source = %s)"
                print('no comment', end = ' ')
                try:
                    self.db_connection.execute(sql, (0, query, 'naver_cafe_comment', url, 0, url, 'naver_cafe_comment'))
                except Exception as e:
                    print(e)
            print('done')
            time.sleep(random.uniform(2, 4))

    def daum_blog_comment_Crawler(self, query):
        # results = daum_blog_comment(self.driver, "https://jkpos.tistory.com/122")
        sql = "SELECT A.url FROM api_url A LEFT OUTER JOIN crawling_content B ON A.url = B.url WHERE A.source = 'daum_blog' AND B.url is NULL AND A.search_keyword = \'"+query+"\';"
        df = pd.read_sql(sql, self.db_connection)
        url_list = df['url'].values.tolist()

        for i, url in enumerate(url_list):
            print(i, '번째', url, end=' ')
            results = daum_blog_comment(self.driver, url)
            if len(results)>0:
                sql = "INSERT INTO crawling_content (comment_seq, search_keyword, source, url, comment, author, commentdate) " \
                      "SELECT %s, %s, %s, %s, %s, %s, %s " \
                      "FROM DUAL WHERE NOT EXISTS (" \
                      "SELECT * FROM crawling_content WHERE comment_seq = %s AND url = %s AND source = %s)"
                for j, result in enumerate(results):
                    try:
                        # num = result[2].rfind('.')
                        self.db_connection.execute(sql, (j+1, query, 'daum_blog_comment', url, result[1], result[0], result[2], j+1, url, 'daum_blog_comment'))
                    except Exception as e:
                        print(e)
            else:
                sql = "INSERT INTO crawling_content (comment_seq, search_keyword, source, url) " \
                      "SELECT %s, %s, %s, %s " \
                      "FROM DUAL WHERE NOT EXISTS (" \
                      "SELECT * FROM crawling_content WHERE comment_seq = %s AND url = %s AND source=%s)"
                print('no comment', end = ' ')
                try:
                    self.db_connection.execute(sql, (0, query, 'daum_blog_comment', url, 0, url, 'daum_blog_comment'))
                except Exception as e:
                    print(e)
            print('done')
            time.sleep(random.uniform(2, 4))

    def youtube_comment_Crawler(slef, query):
        url_youtube(query)

    def twitter_Crawler(self, query):
        get_url_twitter(query)

    def daum_Crawler(self, query):
        url_daum(query)

    def naver_Crawler(self, query):
        url_naver(query, 'blog')
        url_naver(query, 'cafe')

    def quit_driver(self):
        self.driver.quit()