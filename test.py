import configparser
import pymysql
from sqlalchemy import create_engine

import time

start = time.time()


config = configparser.ConfigParser()
config.read('config.ini', encoding='utf-8')

def get_query():
    conn = pymysql.connect(
        host=config['MYSQL_CONFIG']['sql_host'],
        user=config['MYSQL_CONFIG']['user'],
        password=config['MYSQL_CONFIG']['password'],
        db=config['MYSQL_CONFIG']['db'],
        charset=config['MYSQL_CONFIG']['charset']
    )

    curs = conn.cursor()

    # sql = "INSERT INTO query_data (user_id, search_keyword) VALUES (%s, %s) "
    # print(config['MYSQL_CONFIG']['db_connection'])
    # db_connection = create_engine(config['MYSQL_CONFIG']['db_connection'])
    # db_connection.execute(sql, (1, 'hey'))

    sql= "select seq, search_keyword from query_data"
    curs.execute(sql)

    result = curs.fetchall()[0]

    return result

# query = get_query()
# query = query[1]
query = "푸틴"

from Crawler.crawlingModule import crawlingModule

modules = crawlingModule()

modules.youtube_comment_Crawler(query)
modules.twitter_Crawler(query)
modules.daum_Crawler(query)
modules.naver_Crawler(query)
modules.naver_blog_content_Crawler(query)
modules.daum_blog_comment_Crawler(query)
modules.naver_blog_comment_Crawler(query)
modules.naver_cafe_comment_Crawler(query)
modules.quit_driver()


from Crawler.openapiRequest.twitter_api import request_twitter_REAL

request_twitter_REAL(query)



from service.analysisService import AnalysisService
print(query, 'query')
analService = AnalysisService(query, 30, 11111, ['naver_blog'])

realtime = analService.request_body_realtime()
print(realtime, "realtime")
periodic = analService.request_body_periodic()
print(periodic, "periodic")


from GPTserver.analysisGPT import repu_main


text = ['이거 최악이에요', '너무 좋아요']
result = repu_main(text)
print(result, "result")

from GPTserver.gptModule import insert_sentence_senti_detail_column

insert_sentence_senti_detail_column()

from service.modules.textAnalysisModule import textAnalysisModule
from Crawler.openapiRequest.naver_api import get_naver
from Crawler.openapiRequest.daum_api import get_daum

# query = "닥터송+마케팅"

sentence_list = list(map(lambda x:x[1].replace('...', ''), get_naver('blog', query)))
sentence_list += list(map(lambda x: x[1].replace('...', ''), get_daum('blog', query)))
sentence_list += list(map(lambda x: x[1].replace('...', ''), get_daum('cafe', query)))
sentence_list += list(map(lambda x: x[1].replace('...', ''), get_naver('news', query)))

# sentence_list += list(map(lambda x: x[1], get_twitter))
textAnal = textAnalysisModule()
#
result = textAnal.mostAppearedNoun(sentence_list, 15)
print(result, "result 최종")

print(time.time() - start)