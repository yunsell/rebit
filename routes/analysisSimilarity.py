import json

from flask import request, make_response
from flask_restx import Resource, Namespace

from service.analysisService import AnalysisService

Analysis_similarity = Namespace('Analysis_similarity')

@Analysis_similarity.route('')
class TestClass(Resource):
    def get(self):
        # parameter get
        keyword = request.args.get("keyword", default="그랜드성형외과", type=str)
        sources = request.args.getlist("source")

        duration = 'sim'
        sources = ["naver_blog"]

        # 서비스 객체 생성
        analService = AnalysisService(keyword, duration, sources)

        # 실시간 / 주기적 결과 저장
        try:
            result = analService.request_body_realtime()
        except Exception as e:
            result = "Error : "+str(e) + " 적합한 요청 방식이 아닙니다."

        # json 형식으로 반환
        result = json.dumps(result, ensure_ascii=False)

        return make_response(result, 200)

    def post(self):
        # test = request.json.get()
        response = request.json.get("keyword")

        print(response)
        #SERVICE에서 처리한 값을 Result로 넘겨줌
        # result = SortingByFrequency()

        return make_response('result', 200)