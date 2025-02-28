# app/api/endpoints.py
from fastapi import APIRouter, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse
import json
from ..schemas.models import AnalysisResult
from ..services.preprocessor import DataPreprocessor
from ..services.analyzer import DataAnalyzer

router = APIRouter()
preprocessor = DataPreprocessor()
analyzer = DataAnalyzer()

@router.post("/analysis/{analysis_id}", response_model=AnalysisResult)
async def analyze_data(
    analysis_id: str,
    history_file: UploadFile = File(...),
    likes_file: UploadFile = File(...),
    subscriptions_file: UploadFile = File(...)
):
    try:
        # Read and parse JSON files
        history_data = json.loads(await history_file.read())
        likes_data = json.loads(await likes_file.read())
        subscriptions_data = json.loads(await subscriptions_file.read())
        
        # Preprocess data
        preprocessed_history = await preprocessor.preprocess_history(history_data)
        preprocessed_likes = await preprocessor.preprocess_likes(likes_data)
        preprocessed_subscriptions = await preprocessor.preprocess_subscriptions(subscriptions_data)
        
        # Analyze data
        analysis_data = await analyzer.analyze_data(
            preprocessed_history,
            preprocessed_likes,
            preprocessed_subscriptions
        )
        
        return AnalysisResult(
            status="success",
            data=analysis_data
        )
        
    except json.JSONDecodeError:
        raise HTTPException(
            status_code=400,
            detail="Invalid JSON format in uploaded files"
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )