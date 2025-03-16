# app/services/analysis_service.py
import json
from typing import Dict, List, Any, AsyncGenerator

from .preprocessor import DataPreprocessor
from .analyzer import DataAnalyzer
from ..schemas.models import AnalysisData

# 서비스 인스턴스 생성
preprocessor = DataPreprocessor()
analyzer = DataAnalyzer()


async def process_analysis_request(
    history_data: Dict[str, Any], 
    subscriptions_data: Dict[str, Any]
) -> AnalysisData:
    """
    분석 프로세스 실행 및 결과 생성 (기존 엔드포인트용)
    
    Args:
        history_data: 시청 기록 데이터
        subscriptions_data: 구독 정보 데이터
        
    Returns:
        AnalysisData: 분석 결과
    """
    # 데이터 전처리
    preprocessed_history = await preprocessor.preprocess_history(history_data)
    preprocessed_subscriptions = await preprocessor.preprocess_subscriptions(subscriptions_data)
    
    # 데이터 분석
    analysis_data = await analyzer.analyze_data(
        preprocessed_history,
        preprocessed_subscriptions
    )
    
    return analysis_data


async def process_streaming_analysis(
    history_data: Dict[str, Any], 
    subscriptions_data: Dict[str, Any]
) -> AsyncGenerator[str, None]:
    """
    스트리밍 분석 프로세스 실행 및 결과 생성
    
    Args:
        history_data: 시청 기록 데이터
        subscriptions_data: 구독 정보 데이터
        
    Yields:
        각 분석 단계의 결과를 JSON 문자열로 반환
    """
    try:
        # 데이터 전처리
        preprocessed_history = await preprocessor.preprocess_history(history_data)
        preprocessed_subscriptions = await preprocessor.preprocess_subscriptions(subscriptions_data)
        
        # 1. 시간대별 통계 분석 및 전송
        hourly_stats = await analyzer.extract_hourly_channel_stats(preprocessed_history)
        hourly_response = {
            "function": "hourly_stats",
            "status": "success",
            "data": hourly_stats
        }
        yield json.dumps(hourly_response) + "\n"
        
        # 2. 키워드 분석 및 전송
        keyword_frequency = await analyzer.extract_keywords({
            "history": preprocessed_history,
            "subscriptions": preprocessed_subscriptions
        })
        # Pydantic 모델을 dict로 변환
        keyword_data = [{"keyword": kw.keyword, "frequency": kw.frequency} for kw in keyword_frequency]
        keyword_response = {
            "function": "keyword_frequency",
            "status": "success",
            "data": keyword_data
        }
        yield json.dumps(keyword_response) + "\n"
        
        # 3. LLM 분석 및 전송
        llm_analysis = await analyzer.generate_llm_analysis({
            "hourly_stats": hourly_stats,
            "keyword_frequency": keyword_frequency
        })
        llm_response = {
            "function": "llm_analysis",
            "status": "success",
            "data": llm_analysis
        }
        yield json.dumps(llm_response) + "\n"
        
        # 4. 완료 메시지
        final_response = {
            "function": "completion",
            "status": "success",
            "message": "분석이 완료되었습니다."
        }
        yield json.dumps(final_response) + "\n"
        
    except Exception as e:
        error_response = {
            "function": "error",
            "status": "error",
            "message": str(e)
        }
        yield json.dumps(error_response) + "\n"
