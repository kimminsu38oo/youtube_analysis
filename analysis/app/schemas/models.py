# app/schemas/models.py
from pydantic import BaseModel, Field
from typing import List

class CategoryViews(BaseModel):
    name: str = Field(description="카테고리 이름")
    views: float = Field(description="해당 시간대의 카테고리 시청 횟수", ge=0)

class HourlyStat(BaseModel):
    hour: int = Field(description="시간대 (0~23)", ge=0, le=23)
    totalViews: float = Field(description="해당 시간대의 전체 시청 횟수", ge=0)
    categories: List[CategoryViews] = Field(
        description="해당 시간대의 카테고리별 시청 횟수",
        default=[],
    )

class KeywordFrequency(BaseModel):
    keyword: str = Field(description="키워드")
    frequency: float = Field(description="키워드 출현 빈도", ge=0)

class AnalysisData(BaseModel):
    hourlyStats: List[HourlyStat] = Field(
        description="0시부터 23시까지의 시간대별 시청 통계",
        min_items=24,
        max_items=24
    )
    keywordFrequency: List[KeywordFrequency] = Field(
        description="키워드 빈도 분석 결과",
        min_items=1
    )
    llmAnalysis: str = Field(description="LLM 기반 텍스트 분석 결과")

class AnalysisResult(BaseModel):
    status: str = Field("success", description="API 요청 처리 상태")
    data: AnalysisData

    class Config:
        schema_extra = {
            "example": {
                "status": "success",
                "data": {
                    "hourlyStats": [
                        {"hour": 0, "totalViews": 0, "categories": []},
                        {"hour": 1, "totalViews": 0, "categories": []},
                        {"hour": 2, "totalViews": 0, "categories": []},
                        {"hour": 3, "totalViews": 0, "categories": []},
                        {"hour": 4, "totalViews": 0, "categories": []},
                        {"hour": 5, "totalViews": 0, "categories": []},
                        {"hour": 6, "totalViews": 0, "categories": []},
                        {"hour": 7, "totalViews": 0, "categories": []},
                        {"hour": 8, "totalViews": 0, "categories": []},
                        {"hour": 9, "totalViews": 0, "categories": []},
                        {"hour": 10, "totalViews": 0, "categories": []},
                        {"hour": 11, "totalViews": 0, "categories": []},
                        {"hour": 12, "totalViews": 0, "categories": []},
                        {"hour": 13, "totalViews": 0, "categories": []},
                        {"hour": 14, "totalViews": 0, "categories": []},
                        {"hour": 15, "totalViews": 0, "categories": []},
                        {"hour": 16, "totalViews": 0, "categories": []},
                        {"hour": 17, "totalViews": 0, "categories": []},
                        {"hour": 18, "totalViews": 200, "categories": [
                            {"name": "엔터테인먼트", "views": 121},
                            {"name": "교육", "views": 79}
                        ]},
                        {"hour": 19, "totalViews": 300, "categories": [
                            {"name": "엔터테인먼트", "views": 182},
                            {"name": "교육", "views": 118}
                        ]},
                        {"hour": 20, "totalViews": 250, "categories": [
                            {"name": "엔터테인먼트", "views": 151},
                            {"name": "교육", "views": 99}
                        ]},
                        {"hour": 21, "totalViews": 150, "categories": [
                            {"name": "엔터테인먼트", "views": 91},
                            {"name": "교육", "views": 59}
                        ]},
                        {"hour": 22, "totalViews": 100, "categories": [
                            {"name": "엔터테인먼트", "views": 61},
                            {"name": "교육", "views": 39}
                        ]},
                        {"hour": 23, "totalViews": 50, "categories": [
                            {"name": "엔터테인먼트", "views": 30},
                            {"name": "교육", "views": 20}
                        ]}
                    ],
                    "keywordFrequency": [
                        {"keyword": "음악", "frequency": 150},
                        {"keyword": "게임", "frequency": 100}
                    ],
                    "llmAnalysis": "사용자는 주로 저녁 시간대에 엔터테인먼트 콘텐츠를 시청하는 경향이 있습니다."
                }
            }
        }