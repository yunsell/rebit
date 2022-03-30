from flask import Flask  # 서버 구현을 위한 Flask 객체 import
from flask_restx import Api  # Api 구현을 위한 Api 객체 import
from routes.analysisRouter import Analysis
from routes.analysisLatest import Analysis_date
from routes.analysisSimilarity import Analysis_similarity
from routes.analysisMostAppear import Analysis_mostAppear
from routes.test import Test

app = Flask(__name__)  # Flask 객체 선언, 파라미터로 어플리케이션 패키지의 이름을 넣어줌.
api = Api(app, version='1.0', title="rebit_nlp",
          description="REST_API Server")

# 객체 경로 지정
api.add_namespace(Analysis, '/analysis') #평판검색
api.add_namespace(Analysis_date, '/latest') #오늘의 평판
api.add_namespace(Analysis_similarity, '/relation') #관련도순
api.add_namespace(Analysis_mostAppear, '/mostAppear') #연관어 빈도수 정렬
# api.add_namespace(Document, '/document') #분석 보고서
api.add_namespace(Test, '/test/<str>')

if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0')