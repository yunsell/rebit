import pymysql
import configparser
from konlpy.tag import Okt
from collections import Counter, OrderedDict

config = configparser.ConfigParser()
config.read('config.ini', encoding='utf-8')

class textAnalysisModule:
    def __init__(self):
        self.okt = Okt()

    def tagging_sentence(self, sentence):
        tagging = self.okt.nouns(sentence)

        return tagging

    def mostAppearedNoun(self, sentence_list, num):
        conn = pymysql.connect(
            host=config['MYSQL_CONFIG']['sql_host'],
            user=config['MYSQL_CONFIG']['user'],
            password=config['MYSQL_CONFIG']['password'],
            db=config['MYSQL_CONFIG']['db'],
            charset=config['MYSQL_CONFIG']['charset']
        )
        curs = conn.cursor()

        text = []
        mostAppear = OrderedDict()
        for sentence in sentence_list:
            text += self.tagging_sentence(sentence)
        result = Counter(text)

        for val in result.most_common(num):
            mostAppear[val[0]] = val[1]

        print(val)
        # sql = "UPDATE review SET mention = %s WHERE seq = %s"
        #
        # curs.execute(sql, (mostAppear, 1))
        # conn.commit()
        # conn.close()

        return mostAppear