import json

from flask import request, make_response
from flask_restx import Resource, Namespace

from service.analysisService import AnalysisService

Analysis_mostAppear = Namespace('Analysis_mostAppear')

@Analysis_mostAppear.route('')
class TestClass(Resource):
    def get(self):
        keyword = request.args.get("keyword", default="그랜드성형외과", type=str)
        duration = int(request.args.get("duration", default="30", type=str))
        sources = request.args.getlist("source")
        request_type = request.args.get("type", default="now", type=str)

        sources = "mostAppear"  # mostAppear, 형태소 분석 모듈 호출하도록 파라미터 설정

        analService = AnalysisService(keyword, duration, sources)

        # 실시간 / 주기적 결과 저장
        try:
            if request_type == 'now':
                result = analService.request_body_realtime()
            elif request_type == 'period':
                result = analService.request_body_periodic()
        except Exception as e:
            result = "Error : " + str(e) + " 적합한 요청 방식이 아닙니다."

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