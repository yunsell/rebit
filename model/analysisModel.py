############## DB Selection ###############
import configparser

import pymysql
from datetime import datetime, timedelta
from sqlalchemy import create_engine

class AnalysisModel:
    def __init__(self):
        config = configparser.ConfigParser()
        config.read('config.ini', encoding='utf-8')

        self.conn = pymysql.connect(
            host=config['MYSQL_CONFIG']['sql_host'],
            user=config['MYSQL_CONFIG']['user'],
            password=config['MYSQL_CONFIG']['password'],
            db=config['MYSQL_CONFIG']['db'],
            charset=config['MYSQL_CONFIG']['charset']
        )

        db_connection_str = config['MYSQL_CONFIG']['db_connection']
        self.db_connection = create_engine(db_connection_str, pool_pre_ping=True, pool_recycle = 300)


    # 쿼리의 모든 api 검색 데이터 조회
    def get_all_api_data(self, query, source):
        curs = self.conn.cursor()

        f = '%Y-%m-%d %H:%M:%S'

        sql = "select * from api_url where query = %s AND source = %s"
        curs.execute(sql, query, source)

        rows = curs.fetchall()

        id = []
        title= []
        content = []
        postdate= []
        url = []
        source = []
        for row in rows:
            id.append(row[0])
            title.append(row[5])
            content.append(row[6])
            postdate.append(row[3].strftime(f))
            url.append(row[2])
            source.append(row[4])

        curs.close()
        return title, content, postdate, url, source

    # 쿼리의 모든 crawling 데이터 조회
    def get_all_crawling_data(self, query, source):
        curs = self.conn.cursor()

        sql = "select * from crawling_content where query = %s AND source = %s"
        curs.execute(sql, query, source)

        rows = curs.fetchall()

        id = []
        content = []
        postdate= []
        url = []
        source = []
        for row in rows:
            id.append(row[0])
            content.append(row[5])
            postdate.append(row[7])
            url.append(row[2])
            source.append(row[4])

        curs.close()

        return id, content, postdate, url, source

    # 쿼리의 오늘 api 검색 데이터 조회
    # def get_today_api_data(self, query):
    #     # naver_blog,  naver_cafe,    daum_blog,   daum_cafe, youtube_comment
    #     result = []
    #     result_dict = []
    #     tmp_dict = {}
    #     mon_len = 0
    #     curs = (self.conn).cursor()
    #
    #     edit = []
    #     today = datetime.today()
    #     today = today.strftime("%Y-%m-%d")
    #
    #     sql = "select * from api_url where search_keyword = %s AND postdate = %s"
    #     curs.execute(sql, (query, today))
    #     rows = (curs.fetchall())
    #     mon_len += len(rows)
    #     if len(rows) > 0 :
    #         for i, row in enumerate(rows):
    #             tmpList = list(row)
    #             tmpList[3] = tmpList[3].strftime("%Y-%m-%d")
    #             row = tuple(tmpList)
    #             tmp_dict["id"] = tmpList[0]
    #             tmp_dict["keyword"] = tmpList[1]
    #             tmp_dict["url"] = tmpList[2]
    #             tmp_dict["postdate"] = tmpList[3]
    #             tmp_dict["domain"] = tmpList[4]
    #             tmp_dict["title"] = tmpList[5]
    #             tmp_dict["author"] = tmpList[6]
    #             tmp_dict["content"] = tmpList[7]
    #             edit.append(row)
    #             result_dict.append(tmp_dict)
    #         result.append(edit)
    #
    #     curs.close()
    #
    #     return mon_len, result_dict

    # 쿼리의 최근 api 검색 데이터 조회
    # def get_recent_api_data(self, query):
    #     # naver_blog,  naver_cafe,    daum_blog,   daum_cafe, youtube_comment
    #     domain_map = {'naver_blog':'네이버 블로그', 'naver_cafe':'네이버 카페', 'daum_blog':'다음 블로그', 'daum_cafe':'다음 카페', 'youtue_comment':'유튜브'}
    #     result = []
    #     result_dict = []
    #     mon_len = 0
    #     curs = (self.conn).cursor()
    #
    #     edit = []
    #
    #     sql = "select * from api_url where search_keyword = %s AND postdate IS NOT NULL ORDER BY postdate DESC LIMIT 5"
    #     curs.execute(sql, (query))
    #     rows = (curs.fetchall())
    #     mon_len += len(rows)
    #     if len(rows) > 0 :
    #         for i, row in enumerate(rows):
    #             tmp_dict = {}
    #             tmpList = list(row)
    #             tmpList[3] = tmpList[3].strftime("%Y-%m-%d")
    #             tmp_dict["id"] = tmpList[0]
    #             tmp_dict["keyword"] = tmpList[1]
    #             tmp_dict["url"] = tmpList[2]
    #             tmp_dict["postdate"] = tmpList[3]
    #             tmp_dict["domain"] = domain_map[tmpList[4]]
    #             tmp_dict["title"] = tmpList[5]
    #             tmp_dict["author"] = tmpList[6]
    #             tmp_dict["content"] = tmpList[7]
    #             result_dict.append(tmp_dict)
    #         result.append(edit)
    #
    #     curs.close()
    #
    #     return mon_len, result_dict

    # 쿼리의 특정 기간 api 검색 데이터 조회
    def get_dura_api_data(self, query, source, dura):
        # naver_blog,  naver_cafe,    daum_blog,   daum_cafe, youtube_comment
        result = []
        result_dict = []
        tmp_dict = {}
        mon_len = 0
        curs = (self.conn).cursor()

        for i in range (0, dura):
            edit = []
            today = datetime.today() - timedelta(i)
            today = today.strftime("%Y-%m-%d")

            sql = "select * from api_url where search_keyword = %s AND postdate = %s AND source=%s"

            curs.execute(sql, (query, today, source))
            rows = curs.fetchall()
            mon_len += len(rows)
            if len(rows) > 0 :
                for row in (rows):
                    tmpList = list(row)
                    tmpList[3] = tmpList[3].strftime("%Y-%m-%d")
                    row = tuple(tmpList)
                    tmp_dict["id"] = tmpList[0]
                    tmp_dict["keyword"] = tmpList[1]
                    tmp_dict["url"] = tmpList[2]
                    tmp_dict["postdate"] = tmpList[3]
                    tmp_dict["domain"] = tmpList[4]
                    tmp_dict["title"] = tmpList[5]
                    tmp_dict["content"] = tmpList[6]
                    edit.append(row)
                result_dict.append(tmp_dict)
                result.append(edit)

        curs.close()

        return mon_len, result

    # 쿼리의 최근 api 검색 데이터 중 특정 도메인 조회
    def get_recent_boardList(self, query, source, listNum):
        curs = self.conn.cursor()

        sql = "select * FROM api_url WHERE search_keyword = %s AND source = %s ORDER BY postdate DESC LIMIT %s"
        curs.execute(sql, (query, source, listNum))
        rows = curs.fetchall()
        curs.close()

        return rows

    # 쿼리의 최근 감성 분석 데이터 조회
    def get_detail_boardList(self, query, source, detail, listNum):
        # query, source, 출력할 리스트 갯수 출력\
        curs = (self.conn).cursor()

        sql = "SELECT B.* FROM sentiment_anal as A JOIN crawling_content as B ON A.seq = B.seq " \
              "WHERE B.search_keyword = %s AND B.source = %s AND A.sentiment_detail = %s ORDER BY B.commentdate DESC LIMIT %s"

        try:
            curs.execute(sql, (query, source, detail, listNum))
            rows = curs.fetchall()
        except Exception as e:
            print(e)

        curs.close()

        return rows

    # 쿼리의 특정 기간 문장 단위 감성 분석 데이터 중 특정 도메인 조회
    def get_duration_sentiAnalSentence_data(self, query, source, from_day, to_day):
        sentiAnal_list = []
        sql = "SELECT A.sentiment_sentence FROM sentiment_anal as A JOIN crawling_content as B ON A.seq = B.seq " \
              "WHERE B.search_keyword = %s AND B.source = %s AND DATE(B.commentdate) BETWEEN %s AND %s "
        result = self.db_connection.execute(sql, query, source, from_day, to_day)
        rows = (result.fetchall())

        for row in rows:
            sentiAnal_list.append(row[0])

        return sentiAnal_list

    # 쿼리의 특정 기간 세부 감성 분석 데이터 조회
    def get_duration_sentiAnalDetail_data(self, query, source, from_day, to_day):
        sentiAnal_list = []

        sql = "SELECT A.sentiment_detail FROM sentiment_anal as A JOIN crawling_content as B ON A.seq = B.seq " \
              "WHERE B.search_keyword = %s AND B.source = %s AND DATE(B.commentdate) BETWEEN %s AND %s "

        result = self.db_connection.execute(sql, query, source, from_day, to_day)
        rows = (result.fetchall())
        for row in rows:
            sentiAnal_list.append(row[0])

        return sentiAnal_list

    # 올해와 작년 감성 분석 결과 중 특정 도메인 조회
    def get_smallstats_data(self, query, source, this_year, last_year):
        if 'naver_blog' in source:
            source = 'naver_blog'
        elif 'daum_blog' in source:
            source = 'daum_blog'
        elif 'naver_cafe' in source:
            source = 'naver_cafe'
        elif 'daum_cafe' in source:
            source = 'daum_cafe'

        sql = "SELECT B.*, A.sentiment_detail, A.sentiment_sentence FROM sentiment_anal as A JOIN crawling_content as B ON A.seq = B.seq " \
        "WHERE B.search_keyword = %s AND B.source = %s AND EXTRACT(YEAR FROM B.commentdate) = %s "

        cur = self.db_connection.execute(sql, (query, source, this_year))
        pas = self.db_connection.execute(sql, (query, source, last_year))
        cur_rows = (cur.fetchall())
        pas_rows = (pas.fetchall())

        return cur_rows, pas_rows

    # 수동 connection close
    def close_conn(self):
        self.conn.close()


    # 소멸자를 통한 connection close
    def __del__(self):
        self.db_connection.dispose()