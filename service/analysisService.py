############## 결과 분석 서비스 ###############
from collections import OrderedDict

from Crawler.openapiRequest.daum_api import get_daum
from Crawler.openapiRequest.naver_api import get_naver
from Crawler.openapiRequest.twitter_api import request_twitter_REAL
from service.modules.analysisModule import AnalysisModule
#from service.modules.textAnalysisModule import textAnalysisModule_khaiii

import datetime

class AnalysisService:
    def __init__(self, keyword, duration, set, sources):
        self.result = OrderedDict()
        self.keyword = keyword.replace('+', ' ').replace('%2B', '+')
        self.duration = duration
        self.set = set
        self.sources = sources
        self.AnalModule = AnalysisModule()
        #self.textAnal = textAnalysisModule_khaiii()

    # 빈도수 기준 정렬
    # def SortingByFrequency(self, dict_list):
    #     result = []
    #     c = self.analysisModule.sortByFrequency(dict_list)
    #     dict_list = sorted(c.items(), key=lambda x: x[1], reverse=True)
    #
    #     sorted_list = dict_list[:10]
    #     for i, x in enumerate(sorted_list):
    #         item = {}
    #         item['title'] = x[0]
    #         item['value'] = x[1]
    #         result.append(item)
    #
    #     return result

    # 이번달&저번달 감성 단어 등장 횟수
    def EachMonthPosNeg(self, cur, pas):
        result = []
        currentData = OrderedDict()
        pastData = OrderedDict()
        currentData['label'] = "Current Month"
        currentData['fill'] = "start"
        currentData['pos_data'] = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
        currentData['neg_data'] = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]

        pastData['label'] = "Past Month"
        pastData['fill'] = "start"
        pastData['pos_data'] = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
        pastData['neg_data'] = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]

        cur_date = []
        cur_sentiDetail = []

        for data in cur:
            cur_date.append(data[7].strftime("%Y%m%d"))
            cur_sentiDetail.append(data[10])

        cur_date = (list(map(lambda s: s[4:6], cur_date)))

        for i, detail in enumerate(cur_sentiDetail):
            if detail == '기쁨':
                currentData['pos_data'][int(cur_date[i]) - 1] += 1
            else:
                currentData['neg_data'][int(cur_date[i]) - 1] += 1

        pas_date = []
        pas_sentiDetail = []

        for data in pas:
            pas_date.append(data[7].strftime("%Y%m%d"))
            pas_sentiDetail.append(data[10])

        pas_date = (list(map(lambda s: s[4:6], pas_date)))

        for i, detail in enumerate(pas_sentiDetail):
            if detail == '기쁨':
                pastData['pos_data'][int(pas_date[i]) - 1] += 1
            else:
                pastData['neg_data'][int(pas_date[i]) - 1] += 1

        result.append(currentData)
        result.append(pastData)

        return result

    # 전체 긍 부정 비율
    def TotalPosNegRatio(self, items):
        result = OrderedDict()
        num_list = self.AnalModule.countPosNegword(items)
        Sum = len(num_list)
        if Sum != 0:
            PosNegMidRatioList = list(map(lambda x: x / Sum * 100, num_list))  # 비율 계산
            data_list = [round(item, 2) for item in PosNegMidRatioList]
        else:
            data_list = [0, 0, 0]
        result['data'] = data_list
        result['labels'] = ['긍정', '부정']

        return result

    # 전체 세부 감정 분석 비율
    def TotalDetailRatio(self, items):
        result = OrderedDict()
        num_list = self.AnalModule.countDetailSent(items)

        Sum = sum(num_list)
        if Sum != 0:
            PosNegMidRatioList = list(map(lambda x: x / Sum * 100, num_list))
            data_list = [round(item, 2) for item in PosNegMidRatioList]
        else:
            data_list = [0, 0, 0, 0, 0, 0]

        details = ['기쁨', '불안', '당황', '슬픔', '분노', '상처']
        for i, detail in enumerate(details):
            result[detail] = data_list[i]

        return result

    # 각 채널별 날짜 데이터 추출 및 일정 갯수만큼 저장한 뒤 날짜 순 정렬 (2022-03-17 현지성 평판검색 관련)
    def calcul_convert_api_data(self, naver_blog, daum_blog, daum_cafe, naver_news, twitter, num):
        result_dict = []
        channels = {}

        #print(self.set)

        channels['네이버 블로그'] = [datetime.datetime.strptime(row[3], "%Y%m%d") for row in naver_blog]
        channels['다음 블로그'] = [datetime.datetime.strptime(row[3], "%Y-%m-%d") for row in daum_blog]
        channels['다음 카페'] = [datetime.datetime.strptime(row[3], "%Y-%m-%d") for row in daum_cafe]
        channels['뉴스'] = [datetime.datetime.strptime(row[3], "%d %m %Y %H:%M:%S") for row in naver_news]
        channels['트위터'] = [datetime.datetime.strptime(row[3], "%Y-%m-%d") for row in twitter]

        total = naver_blog[:num] + daum_blog[:num] + daum_cafe[:num] + naver_news[:num] + twitter[:num]
        #total = daum_cafe[:num] + naver_news[:num] + twitter[:num]
        for i, tmpList in enumerate(total):
            tmp_dict = {}
            if i < num:
                if len(tmpList[3]) < 10:
                    stri = tmpList[3]
                    tmpList[3] = stri[0:4] + '-' + stri[4:6] + '-' + stri[6:]
                tmp_dict["domain"] = '네이버 블로그'
            elif i < num * 2:
                tmp_dict["domain"] = '다음 블로그'
            elif i < num * 3:
                tmp_dict["domain"] = '다음 카페'
            elif i < num * 4:
                stri = tmpList[3]
                if len(str(stri)) == 18:
                    tmpList[3] = stri[5:9] + '-0' + stri[3] + '-' + stri[0:2]
                else:
                    tmpList[3] = stri[6:10] + '-' + stri[3:5] + '-' + stri[0:2]
                tmp_dict["domain"] = '뉴스'
            else:
                tmp_dict["domain"] = '트위터'

            tmp_dict["keyword"] = self.keyword
            tmp_dict["url"] = tmpList[4]
            tmp_dict["postdate"] = tmpList[3]
            tmp_dict["title"] = tmpList[0]
            tmp_dict["author"] = tmpList[2]
            tmp_dict["content"] = tmpList[1]
            result_dict.append(tmp_dict)

        result_dict = sorted(result_dict, key=lambda x: x['postdate'], reverse=True)
        return channels, result_dict

    # api 검색을 통한 실시간 검색 정보 반환 _ 최신순
    def get_today_Review_DATE(self, num=5):
        sentence_list = []

        naver_blog = sorted(get_naver('blog', self.keyword), key=lambda x: x[3], reverse=True)
        daum_blog = sorted(get_daum('blog', self.keyword), key=lambda x: x[3], reverse=True)
        daum_cafe = sorted(get_daum('cafe', self.keyword), key=lambda x: x[3], reverse=True)
        naver_news = sorted(get_naver('news', self.keyword),
                            key=lambda x: datetime.datetime.strptime(x[3], "%d %m %Y %H:%M:%S"), reverse=True)
        twitter = sorted(request_twitter_REAL(self.keyword), key=lambda x: x[3], reverse=True)

        sentence_list += list(map(lambda x: x[1].replace('...', ''), naver_blog))
        sentence_list += list(map(lambda x: x[1].replace('...', ''), daum_blog))
        sentence_list += list(map(lambda x: x[1].replace('...', ''), daum_cafe))
        sentence_list += list(map(lambda x: x[1].replace('...', ''), naver_news))
        sentence_list += list(map(lambda x: x[1].replace('...', ''), twitter))

        channels, result_dict = self.calcul_convert_api_data(naver_blog, daum_blog, daum_cafe, naver_news, twitter, 15)

        return channels, result_dict, sentence_list

        # api 검색을 통한 실시간 검색 정보 반환 _ 관련도순
    def get_today_Review_SIM(self, num=15):
        sentence_list = []

        naver_blog = get_naver('blog', self.keyword)
        daum_blog = get_daum('blog', self.keyword)
        daum_cafe = get_daum('cafe', self.keyword)
        naver_news = get_naver('news', self.keyword)
        twitter = request_twitter_REAL(self.keyword)

        sentence_list += list(map(lambda x: x[1].replace('...', ''), naver_blog))
        sentence_list += list(map(lambda x: x[1].replace('...', ''), daum_blog))
        sentence_list += list(map(lambda x: x[1].replace('...', ''), daum_cafe))
        sentence_list += list(map(lambda x: x[1].replace('...', ''), naver_news))
        sentence_list += list(map(lambda x: x[1], twitter))

        channels, result_dict = self.calcul_convert_api_data(naver_blog, daum_blog, daum_cafe, naver_news, twitter, num)

        return channels, result_dict, sentence_list

    # 실시간 결과 반환
    def request_body_realtime(self):
        result = OrderedDict()
        domainReviewCount = []

        # mostAppear : 연관어 빈도수 기준

        # 평판 검색 화면 5개 내용
        if isinstance(self.duration, int):
            channels, result_dict, sentence_list = self.get_today_Review_DATE()

            for key, value in channels.items():
                domainReviewCount.append(self.AnalModule.calcul_realtime_date(value, self.duration, key))

            domainMentionDate, domainMentionValue, domainRatio = self.AnalModule.calcul_realtime_month_count(channels,
                                                                                                             self.duration)
            result['domainReviewCount'] = domainReviewCount
            result['overallStatus'] = self.AnalModule.getOverallStatus(domainReviewCount)
            result['todayReview'] = result_dict[:5]
            result['domainMentionDate'] = domainMentionDate
            result['domainMentionValue'] = domainMentionValue
            result['domainRatio'] = domainRatio

            if self.sources == 'mostAppear': # 가장 많이 등장한 형태소 리스트 추가
                mostAppear = self.textAnal.mostAppearedNoun(sentence_list, 15)
                result['mostAppear'] = mostAppear
        elif self.duration == 'date': # 평판 분석 화면 15개 내용 _ 최신순
            channels, result_dict, sentence_list = self.get_today_Review_DATE(15)
            result['todayReview'] = result_dict[:20]
        # elif self.duration == 'sim': # 평판 분석 화면 15개 내용 _ 관련도(정확도)순
        #     channels, result_dict, sentence_list = self.get_today_Review_SIM(15)
        #     result['todayReview'] = result_dict[:15]

        return result

    # 주기적 결과 반환
    def request_body_periodic(self):
        list_num = 5
        result = OrderedDict()

        self.sources = ['naver_blog_comment', 'youtube_comment']
        details = ['기쁨', '불안', '당황', '슬픔', '분노', '상처']

        sentiAnal_list, detailAnal_List, cur, pas = [], [], [], []
        for source in self.sources:
            try:
                dic, detail, cu, pa = self.AnalModule.compareDura_WHOLE(self.keyword, source, self.duration)
                sentiAnal_list += dic
                detailAnal_List += detail
                cur += cu
                pas += pa
            except Exception as e:
                print(e)

        channels, result_dict, sentence_list = self.get_today_Review_DATE()

        eachMonthPosNeg = self.EachMonthPosNeg(cur, pas)
        # totalPosNeg = self.TotalPosNegRatio(sentiAnal_list)
        totalDetail = self.TotalDetailRatio(detailAnal_List)
        # domainReviewCount_dict, domainReviewCount_list= self.analysisModule.getReviewRealTime(self.keyword, self.duration)  #비교 원하는 duration * 2
        # overallStatus = self.analysisModule.getOverallStatus(domainReviewCount_list)
        reviewList_eachDetail = {}
        for i, detail in enumerate(details):
            reviewList_eachDetail[detail] = (self.AnalModule.getDetailList(self.keyword, detail, list_num, self.sources))

        domainReviewCount = []
        for key, value in channels.items():
            domainReviewCount.append(self.AnalModule.calcul_realtime_date(value, self.duration * 2, key))
        overallStatus = self.AnalModule.getOverallStatus(domainReviewCount)

        result['domainReviewCount'] = domainReviewCount  # 도메인별 리뷰 수 -> 실시간 api request
        # result['domainReviewCount'] = domainReviewCount_list #도메인별 리뷰 수 -> DB 저장된 내용 불러오기

        result['overallStatus'] = overallStatus
        result['todayReview'] = result_dict[:5]  # 오늘 올라온 리뷰
        # result['orderedWord'] = orderedWord #전체 게시글 단어의 빈도수 기준 정렬 -> 제외
        result['eachMonthPosNeg'] = eachMonthPosNeg  # 저번달, 이번달 긍부정 단어 추이
        # result['totalPosNeg'] = totalPosNeg #전체 단어 긍, 부정 중립 비율
        result['totalDetail'] = totalDetail
        result['reviewList'] = reviewList_eachDetail

        return result

    # # DB 커넥션 종료
    # def __del__(self):
    #     self.AnalModule.close_db_con()


