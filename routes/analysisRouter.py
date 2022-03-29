import json

from flask import request, make_response
from flask_restx import Resource, Namespace

from service.analysisService import AnalysisService

Analysis = Namespace('Analysis')

@Analysis.route('')
class TestClass(Resource):
    def get(self):
        # parameter get
        keyword = request.args.get("keyword", default="코로나진단키트", type=str)
        duration = int(request.args.get("duration", default="30", type=str))
        set = request.args.get("set", default="11111", type=str)
        request_type = request.args.get("type", default="now", type=str)
        sources = request.args.getlist("source")

        sources = ["naver_blog"]

        # 서비스 객체 생성
        analService = AnalysisService(keyword, duration, set, sources)

        # 실시간 / 주기적 결과 저장
        try:
            if request_type == 'now':
                result = analService.request_body_realtime()
            elif request_type == 'period':
                result = analService.request_body_periodic()
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
