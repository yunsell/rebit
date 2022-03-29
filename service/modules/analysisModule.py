############## 분석 모듈 ###############
from collections import OrderedDict, defaultdict
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
import random

from model.analysisModel import AnalysisModel

class AnalysisModule:
    def __init__(self):
        self.AnalModel = AnalysisModel()

    # Dictionary의 value 종류별 갯수 반환
    def sortByFrequency(self, items):
        key_list = {}
        for item in items:
            key_item = item.keys()
            for key in key_item:
                try:
                    key_list[key] += 1
                except:
                    key_list[key] = 1
        return key_list

    # List의 긍/부정 갯수 반환
    def countPosNegword(self, items):
        pos, neg = 0, 0
        for item in items:
            if item == '긍정':
                pos += 1
            elif item == '부정':
                neg += 1
        num_list = [item for item in (pos, neg)]

        return num_list

    # List의 세부 감정 문장 갯수 반환
    def countDetailSent(self, items):
        hap, anx, ner, sad, mad, hurt= 0,0,0,0,0,0
        # num_list = items
        for item in items:
            if item == '기쁨':
                hap += 1
            elif item == '불안':
                anx += 1
            elif item == '당황':
                ner += 1
            elif item == '슬픔':
                sad += 1
            elif item == '분노':
                mad += 1
            else :
                hurt += 1
        num_list = [item for item in (hap, anx, ner, sad, mad, hurt)]
        return num_list

    # 리뷰리스트 가져오기
    # def getReviewList(self, keyword):
    #     reviewList = []
    #     result = []
    #     source_type = ['naver_blog']
    #     for type in source_type:
    #         try:
    #             reviewList += self.AnalModel.get_recent_boardList(keyword, type, 5)
    #             # reviewList += get_sentence_senti_detail(keyword, type, '부정', 5)
    #         except:
    #             continue
    #
    #     for i, review in enumerate(reviewList[:5]):
    #         content = OrderedDict()
    #         content["id"] = i
    #         content["date"] = review[4].strftime("%Y-%m-%d")
    #         content["author"] = {"name": review[7], "url": review[5]}
    #         content["post"] = {"title": review[1]}
    #         content["body"] = review[2]
    #
    #         result.append(content)
    #
    #     return result

    # 세부감정 리스트 가져오기
    def getDetailList(self, keyword, detail, num, source_type):
        reviewList = []
        result = []
        source_type = ['youtube_comment', 'naver_blog_comment', 'naver_cafe_comment', 'daum_blog_comment']
        random.shuffle(source_type)
        # 현재 세부감정 리스트의 정렬 기준이 없어 youtube_comment의 데이터로 result 리스트가 모두 채워짐, 추후 정렬 기준을 정하여 다른 채널의 데이터도 출력될 수 있도록 해야함.
        # youtube_comment 결과만 나오지 않게 하기 위해 shuffle을 통해 실행마다 다른 순서로 결과 나오도록 함
        for type in source_type:
            try:
                reviewList += self.AnalModel.get_detail_boardList(keyword, type, detail, num)
            except:
                continue

            if 'youtube' in type:
                for i, review in enumerate(reviewList[:num]):
                    content = OrderedDict()
                    content["id"] = i
                    content["domain"] = review[3]
                    content["date"] = review[7].strftime("%Y-%m-%d")
                    content["name"] = review[6]
                    content["url"] = 'https://www.youtube.com/watch?v=' + review[1]
                    content["body"] = review[5]
                    result.append(content)
            else:
                for i, review in enumerate(reviewList[:num]):
                    content = OrderedDict()
                    content["id"] = i
                    content["domain"] = review[4]
                    content["date"] = review[7].strftime("%Y-%m-%d")
                    content["name"] = review[6]
                    content["url"] = review[2]
                    content["body"] = review[5]
                    result.append(content)

        return result

    # 두 기간의 API 검색 데이터 비교 결과 반환
    # def compareDura_API(self, keyword, source, type_name, duration):
    #     week = OrderedDict()
    #     halfDuration = int(duration / 2)
    #
    #     value, date = self.AnalModel.get_dura_api_data(keyword, source, duration)
    #
    #     lenList = list(map(lambda x: len(x), date))
    #
    #     percentage = sum(lenList[:halfDuration]) - sum(lenList[halfDuration: ])
    #
    #     week['domain'] = type_name
    #     week['value'] = sum(lenList[:halfDuration]) # 이번 기간 리뷰 갯수
    #     week['percentage'] = abs(percentage) #저번기간 - 이번기간의 절대값
    #     week['increase'] = True if percentage >= 0 else False # 증가인지 감소인지
    #
    #     return week

    # 입력받은 채널별 데이터 중 이번 주기와 저번 주기 비교 결과 반환
    def calcul_realtime_date(self, dateList, duration, source):
        week = OrderedDict()

        # if source == '트위터':
        #     lenList_cur = date
        #     percentage = 0
        try:
            today = datetime.today()
            today = today.strftime("%Y-%m-%d")

            tomorrow = datetime.today() + timedelta(1)
            tomorrow = tomorrow.strftime("%Y-%m-%d")

            month_1 = datetime.today() - timedelta(duration)
            month_1 = month_1.strftime("%Y-%m-%d")

            month_1_ = datetime.today() - timedelta(duration-1)  # 뉴스 postdate 형식의 초과 기준
            month_1_ = month_1_.strftime("%Y-%m-%d")

            month_2 = datetime.today() - timedelta(int(duration*2))
            month_2 = month_2.strftime("%Y-%m-%d")

            month_2 = datetime.strptime(month_2, "%Y-%m-%d")
            month_1 = datetime.strptime(month_1, "%Y-%m-%d")
            month_1_ = datetime.strptime(month_1_, "%Y-%m-%d")
            today = datetime.strptime(today, "%Y-%m-%d")
            tomorrow = datetime.strptime(tomorrow, "%Y-%m-%d")

            if source =='뉴스':   # 뉴스 api 응답 결과의 postdate에 시간 정보가 포함되어 초과로 계산
                lenList_cur = [i for i in dateList if month_1_ < i < tomorrow]
                lenList_pas = [i for i in dateList if month_2 < i <= month_1_]
            else:
                lenList_cur = [i for i in dateList if month_1 < i <= today]
                lenList_pas = [i for i in dateList if month_2 < i <= month_1]

            percentage = len(lenList_cur) - len(lenList_pas)
        except Exception as e:
            print(e)

        week['domain'] = source
        week['value'] =len(lenList_cur) # 이번 주 리뷰 갯수
        week['percentage'] = abs(percentage) #저번주 - 이번주의 절대값
        week['increase'] = True if percentage >= 0 else False # 증가인지 감소인지

        return week

    # 입력받은 채널별 데이터 중 월별 갯수 반환
    def calcul_realtime_month_count(self, channel_dict, dura):
        result = OrderedDict()
        result_ratio = OrderedDict()

        for key, value in channel_dict.items():
            each_month_value = OrderedDict()
            only_val = []
            for din in range(dura):
                day = datetime.today() - timedelta(din)
                day = day.strftime("%Y-%m-%d")
                each_month_value[day] = 0

            for val in value:
                month = val.strftime("%Y-%m-%d") if isinstance(val, datetime) else val[0:10]
                if month in each_month_value.keys():
                    each_month_value[month] += 1

            for vals in each_month_value.values():
                only_val.append(vals)

            domainDates = list(each_month_value.keys())[:dura]
            domainDates = list(map(lambda x:x[5:], domainDates))
            result[key] = only_val
            result_ratio[key] = sum(only_val)

        return domainDates, result, result_ratio

    # 입력받은 Dictionary list의 value 값 통계 결과(overallStatus) 반환
    def getOverallStatus(self, dict_list):
        result = OrderedDict()
        errorWord = "없음"

        newList = sorted(dict_list, key=lambda x: x['value'], reverse=True)

        mostReviewDomain = errorWord if not newList else newList[0]["domain"]
        result["mostReviewDomain"] = mostReviewDomain

        increaseItem = [item for item in newList if item['increase'] == True]
        increaseItem.sort(key=lambda x: x['percentage'], reverse=True)
        increaseReviewDomain = errorWord if not increaseItem else increaseItem[0]["domain"]
        result["increaseReviewDomain"] = increaseReviewDomain

        decreaseItem = [item for item in newList if item['increase'] == False]
        if len(decreaseItem) > 0:
            decreaseItem.sort(key=lambda x: x['percentage'], reverse=True)
            decreaseReviewDomain = errorWord if not decreaseItem else decreaseItem[0]["domain"]
        else:
            decreaseReviewDomain = errorWord if not increaseItem else increaseItem[-1]["domain"]
        result["decreaseReviewDomain"] = decreaseReviewDomain

        totalList = [item["value"] for item in newList]
        totalToday = errorWord if not newList else sum(totalList)
        result["totalToday"] = totalToday

        return result

    # API 검색 결과 반환 (실시간이 아닌 DB 저장되어 있는 데이터)
    # def getReviewRealTime(self, keyword, duration):
    #     result_dict = {}
    #     result_list = []
    #
    #     #실시간 크롤링 가능 도메인 목록
    #     source_type = ['naver_blog', 'youtube', 'daum_blog', 'daum_cafe']
    #     source_type_name = ['네이버 블로그', '네이버 카페', '유튜브', '다음 블로그', '다음 카페']
    #     for type, type_name in zip(source_type, source_type_name):
    #         result_dict[type_name] = self.compareDura_API(keyword, type, type_name, duration)
    #         result_list.append(self.compareDura_API(keyword, type, type_name, duration))
    #
    #     return result_dict, result_list

    # 두 기간의 데이터 비교, 현재와 과거(cus, pas) 리스트 형태로 반환
    def compareDura_WHOLE(self, query, source, duration):
        today = datetime.now()

        this_year = today.year - 1
        last_year = this_year - 2

        start = today - relativedelta(days = int(3*duration))

        today = today.strftime('%Y-%m-%d')
        start = start.strftime('%Y-%m-%d')

        sentiAnal_List = self.AnalModel.get_duration_sentiAnalSentence_data(query, source, start, today)
        detailAnal_List = self.AnalModel.get_duration_sentiAnalDetail_data(query, source, start, today)

        cur, pas = self.AnalModel.get_smallstats_data(query, source, this_year, last_year)

        return sentiAnal_List, detailAnal_List, cur, pas

    def close_db_con(self):
        self.AnalModel.close_conn()