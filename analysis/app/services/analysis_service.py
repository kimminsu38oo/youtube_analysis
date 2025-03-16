# app/services/analysis_service.py
import json
import asyncio
from typing import Dict, Any, AsyncGenerator, Optional

from .preprocessor import DataPreprocessor
from .analyzer import DataAnalyzer
from ..schemas.models import AnalysisData, KeywordFrequency
from .constant import TEST_HOURLY_STATS, TEST_KEYWORD_DATA, TEST_LLM_ANALYSIS

# 서비스 인스턴스 생성
preprocessor = DataPreprocessor()
analyzer = DataAnalyzer()


def get_test_analysis_data() -> AnalysisData:
    """
    테스트용 분석 데이터를 반환합니다. (일반 엔드포인트용)
    
    Returns:
        AnalysisData: 미리 정의된 테스트 분석 결과
    """
    # 테스트 데이터를 constants.py에서 가져옴
    hourly_stats = TEST_HOURLY_STATS
    
    # 키워드 데이터를 KeywordFrequency 객체 리스트로 변환
    keyword_frequency = [
        KeywordFrequency(keyword=item["keyword"], frequency=item["frequency"]) 
        for item in TEST_KEYWORD_DATA
    ]
    
    # LLM 분석 텍스트
    llm_analysis = TEST_LLM_ANALYSIS
    
    # AnalysisData 객체 반환
    return AnalysisData(
        hourlyStats=hourly_stats,
        keywordFrequency=keyword_frequency,
        llmAnalysis=llm_analysis
    )


async def get_test_streaming_data() -> AsyncGenerator[str, None]:
    """
    테스트용 스트리밍 분석 데이터를 생성합니다. (스트리밍 엔드포인트용)
    각 단계의 결과를 2초 간격으로 반환합니다.
    
    Yields:
        각 분석 단계의 결과를 JSON 문자열로 반환
    """
    # 1. 시간대별 통계 데이터 (constants.py에서 가져옴)
    hourly_response = {
        "function": "hourly_stats",
        "status": "success",
        "data": TEST_HOURLY_STATS
    }
    yield json.dumps(hourly_response) + "\n"
    
    # 2초 대기
    await asyncio.sleep(2)
    
    # 2. 키워드 빈도 데이터 (constants.py에서 가져옴)
    keyword_response = {
        "function": "keyword_frequency",
        "status": "success",
        "data": TEST_KEYWORD_DATA
    }
    yield json.dumps(keyword_response) + "\n"
    
    # 2초 대기
    await asyncio.sleep(2)
    
    # 3. LLM 분석 데이터 (constants.py에서 가져옴)
    llm_response = {
        "function": "llm_analysis",
        "status": "success",
        "data": TEST_LLM_ANALYSIS
    }
    yield json.dumps(llm_response) + "\n"
    
    # 2초 대기
    await asyncio.sleep(2)
    
    # 4. 완료 메시지
    final_response = {
        "function": "completion",
        "status": "success",
        "message": "분석이 완료되었습니다."
    }
    yield json.dumps(final_response) + "\n"


async def process_analysis_request(
    history_data: Dict[str, Any], 
    subscriptions_data: Dict[str, Any],
    analysis_id: Optional[str] = None
) -> AnalysisData:
    """
    분석 프로세스 실행 및 결과 생성 (기존 엔드포인트용)
    
    Args:
        history_data: 시청 기록 데이터
        subscriptions_data: 구독 정보 데이터
        analysis_id: 분석 식별자 (테스트 모드 확인용)
        
    Returns:
        AnalysisData: 분석 결과
    """
    # 테스트 모드 확인 (analysis_id가 "test"인 경우)
    if analysis_id == "test":
        return get_test_analysis_data()
    
    # 일반 분석 프로세스 (기존 코드)
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
    subscriptions_data: Dict[str, Any],
    analysis_id: Optional[str] = None
) -> AsyncGenerator[str, None]:
    """
    스트리밍 분석 프로세스 실행 및 결과 생성
    
    Args:
        history_data: 시청 기록 데이터
        subscriptions_data: 구독 정보 데이터
        analysis_id: 분석 식별자 (테스트 모드 확인용)
        
    Yields:
        각 분석 단계의 결과를 JSON 문자열로 반환
    """
    # 테스트 모드 확인 (analysis_id가 "test"인 경우)
    if analysis_id == "test":
        async for result in get_test_streaming_data():
            yield result
        return
    
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