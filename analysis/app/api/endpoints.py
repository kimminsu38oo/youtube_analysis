# app/api/endpoints.py
from fastapi import APIRouter, UploadFile, File, HTTPException
from ..schemas.models import AnalysisResult
from ..services.preprocessor import DataPreprocessor
from ..services.analyzer import DataAnalyzer
import json

router = APIRouter()
preprocessor = DataPreprocessor()
analyzer = DataAnalyzer()

@router.post("/analysis/{analysis_id}", response_model=AnalysisResult)
async def analyze_data(
        analysis_id: str,
        history_file: UploadFile = File(...),
        subscriptions_file: UploadFile = File(...)
):
    try:
        # JSON 파일 읽기 및 파싱
        history_data = json.loads(await history_file.read())
        subscriptions_data = json.loads(await subscriptions_file.read())
        # 데이터 전처리
        preprocessed_history = await preprocessor.preprocess_history(history_data)
        preprocessed_subscriptions = await preprocessor.preprocess_subscriptions(subscriptions_data)
        # 데이터 분석
        analysis_data = await analyzer.analyze_data(
            preprocessed_history,
            preprocessed_subscriptions
        )
        return AnalysisResult(
            status="success",
            data=analysis_data
        )

    except json.JSONDecodeError:
        raise HTTPException(
            status_code=400,
            detail="업로드된 파일 중 하나의 JSON 형식이 올바르지 않습니다."
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )
