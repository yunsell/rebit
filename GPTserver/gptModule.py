import pymysql
import configparser
import numpy as np

from GPTserver.analysisGPT import detailed_sentiment

config = configparser.ConfigParser()
config.read('config.ini', encoding='utf-8')

# def analysisSentence(corpus):
#     document = getCorpus_Khaiii(corpus)
#     for sentence in document:
#         for phrase in sentence:
#             for word in phrase:
#                 senti_score = senti_Anal(word[0])
#                 print(word[0], '/', senti_score)
#     return document

def insert_sentence_senti_detail_column():
    conn = pymysql.connect(
        host=config['MYSQL_CONFIG']['sql_host'],
        user=config['MYSQL_CONFIG']['user'],
        password=config['MYSQL_CONFIG']['password'],
        db=config['MYSQL_CONFIG']['db'],
        charset=config['MYSQL_CONFIG']['charset']
    )
    curs = conn.cursor()

    id = []
    content = []

    try:
        # sql = "select seq, comment from crawling_content where comment is not null"
        sql = "select crawl.seq, crawl.comment from crawling_content as crawl " \
              "left join sentiment_anal as senti on senti.seq = crawl.seq " \
              "where senti.seq IS NULL and crawl.comment IS NOT NULL and length(crawl.comment) > 0 order by crawl.seq"

        curs.execute(sql)
        rows = curs.fetchall()
        for row in rows:
            id.append(row[0])
            content.append(row[1])

        repu, value = detailed_sentiment(content)
        repu = np.array(value)

        for i, row in enumerate(rows):
            sql = "INSERT INTO sentiment_anal (seq, sentiment_detail, sentiment_sentence) VALUES (%s, %s, %s) ON DUPLICATE KEY UPDATE seq=%s;"
            sentence = '부정'
            if repu[i] == 0:
                result = '기쁨'
                sentence = '긍정'
            elif repu[i] == 1:
                result = '불안'
            elif repu[i] == 2:
                result = '당황'
            elif repu[i] == 3:
                result = '슬픔'
            elif repu[i] == 4:
                result = '분노'
            elif repu[i] == 5:
                result = '상처'
            curs.execute(sql, (id[i], result, sentence, id[i]))
    except Exception as e:
        print(e)
        conn.close()
        return False

    conn.commit()
    conn.close()

    return True