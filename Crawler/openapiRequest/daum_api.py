import configparser

import requests
from urllib.parse import urlparse
from sqlalchemy import create_engine

config = configparser.ConfigParser()
config.read('config.ini', encoding='utf-8')


# daum_openapi에 query 검색 결과 요청 함수
def request_daum(source, query, start):
    if source == 'blog':
        url = "https://dapi.kakao.com/v2/search/blog?&query="+query+"&size=50"+"&sort=accuracy&page="+str(start)
    elif source == 'cafe':
        url = "https://dapi.kakao.com/v2/search/cafe?&query="+query+"&size=50"+"&sort=accuracy&page="+str(start)
    else:
        return False
    header = {'authorization':'KakaoAK '+config['CRAWLING_CONFIG']['Daum_REST_API_KEY']}    # 그럼 뭘로 하라는겨

    r = requests.get(urlparse(url).geturl(), headers=header)
    if r.status_code == 200:
        return r.json()
    else:
        return r.error

# 결과 요청 및 json 응답 결과 중 원하는 값 추출
def get_daum(source, query):
    list=[]
    page = 1
    if source == 'blog':
        while page <= 50:
            json_obj = request_daum(source, query, page)
            for document in json_obj['documents']:
                val = [document['title'].replace("<b>", "").replace("</b>", ""),
                       document['contents'],
                       document['blogname'], document['datetime'][:10], document['url']]
                if '' in val:
                    continue
                else:
                    list.append(val)
            if json_obj['meta']['is_end'] is True: break
            page += 1
    elif source == 'cafe':
        while page <= 50:
            json_obj = request_daum(source, query, page)
            for document in json_obj['documents']:
                val = [document['title'].replace("<b>", "").replace("</b>", ""),
                       document['contents'],
                       document['cafename'].replace("&lt;","").replace("&gt;",""), document['datetime'][:10], document['url']]
                if '' in val:
                    continue
                else:
                    list.append(val)
            if json_obj['meta']['is_end'] is True: break
            page += 1
    return list

# 추출된 결과 db에 입력
def url_daum(query):
    db_connection = create_engine(config['MYSQL_CONFIG']['db_connection'])

    json_list_blog = get_daum('blog', query)

    for i, list in enumerate(json_list_blog):
        try:
            if 'naver' in list[4]:
                source = 'naver_blog'
                sql = "INSERT INTO api_url(title, content, name, postdate, url, search_keyword, source) " \
                      "values (%s, %s, %s, %s, %s, %s, %s) ON DUPLICATE KEY UPDATE postdate=%s;"
                db_connection.execute(sql, (list[0]), (list[1]), list[2], list[3], list[4], query, source, list[3])
            else :
                source = 'daum_blog'
                sql = "INSERT INTO api_url(title, content, name, postdate, url, search_keyword, source) " \
                      "values (%s, %s, %s, %s, %s, %s, %s) ON DUPLICATE KEY UPDATE postdate=%s;"
                db_connection.execute(sql, (list[0]), (list[1]), list[2], list[3], list[4], query, source, list[3])
            print(i, ': ', list[4], ' done')
        except Exception as e:
             print('sql insert error :',e)

    json_list_cafe = get_daum('cafe', query)

    for i, list in enumerate(json_list_cafe):
        # sql = "SELECT count(*) FROM naver_openApi WHERE url = %s"
        # naver_ = db_connection.execute(sql, (list[4]))
        # result = (naver_.first()[0])
        #
        # sql = "SELECT count(*) FROM daum_openApi WHERE url = %s"
        # daum_ = db_connection.execute(sql, (list[4]))
        # result += (daum_.first()[0])

        try:
            if 'naver' in list[4]:
                source = 'naver_cafe'
                sql = "INSERT INTO api_url(title, content, name, postdate, url, search_keyword, source) " \
                      "values (%s, %s, %s, %s, %s, %s, %s) ON DUPLICATE KEY UPDATE postdate=%s;"
                db_connection.execute(sql, (list[0]), (list[1]), list[2], list[3], list[4], query, source, list[3])
            else :
                source = 'daum_cafe'
                sql = "INSERT INTO api_url(title, content, name, postdate, url, search_keyword, source) " \
                      "values (%s, %s, %s, %s, %s, %s, %s) ON DUPLICATE KEY UPDATE postdate=%s;"
                db_connection.execute(sql, (list[0]), (list[1]), list[2], list[3], list[4], query, source, list[3])
            print(i, ': ', list[4], ' done')
        except Exception as e:
            print('sql insert error :',e)
