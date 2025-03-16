# app/api/endpoints.py
from fastapi import APIRouter, UploadFile, File, HTTPException
from ..schemas.models import AnalysisResult
from fastapi.responses import StreamingResponse
from ..services.analysis_service import process_analysis_request, process_streaming_analysis
import json

router = APIRouter()

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
        
        # 분석 서비스 호출
        analysis_data = await process_analysis_request(history_data, subscriptions_data)
        
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
    
@router.post("/analysis-stream/{analysis_id}")
async def analyze_data_stream(
        analysis_id: str,
        history_file: UploadFile = File(...),
        subscriptions_file: UploadFile = File(...)
):
    try:
        # JSON 파일 읽기 및 파싱
        history_data = json.loads(await history_file.read())
        subscriptions_data = json.loads(await subscriptions_file.read())
        
        # 스트리밍 서비스 호출
        return StreamingResponse(
            process_streaming_analysis(history_data, subscriptions_data),
            media_type="application/json",
            headers={"X-Content-Type-Options": "nosniff"}
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

# @router.post("/analysis/{analysis_id}", response_model=AnalysisResult)
# async def analyze_data(
#         analysis_id: str,
#         history_file: UploadFile = File(...),
#         subscriptions_file: UploadFile = File(...)
# ):
#     try:
#         # JSON 파일 읽기 및 파싱
#         history_data = json.loads(await history_file.read())
#         subscriptions_data = json.loads(await subscriptions_file.read())
#         # 데이터 전처리
#         preprocessed_history = await preprocessor.preprocess_history(history_data)
#         preprocessed_subscriptions = await preprocessor.preprocess_subscriptions(subscriptions_data)
#         # 데이터 분석
#         analysis_data = await analyzer.analyze_data(
#             preprocessed_history,
#             preprocessed_subscriptions
#         )
#         return AnalysisResult(
#             status="success",
#             data=analysis_data
#         )

#     except json.JSONDecodeError:
#         raise HTTPException(
#             status_code=400,
#             detail="업로드된 파일 중 하나의 JSON 형식이 올바르지 않습니다."
#         )
#     except Exception as e:
#         raise HTTPException(
#             status_code=500,
#             detail=str(e)
#         )


# # 기존 엔드포인트는 유지하고 새로운 스트리밍 엔드포인트 추가
# @router.post("/analysis-stream/{analysis_id}")
# async def analyze_data_stream(
#         analysis_id: str,
#         history_file: UploadFile = File(...),
#         subscriptions_file: UploadFile = File(...)
# ):
#     try:
#         # JSON 파일 읽기 및 파싱
#         history_data = json.loads(await history_file.read())
#         subscriptions_data = json.loads(await subscriptions_file.read())
        
#         # 데이터 전처리
#         preprocessed_history = await preprocessor.preprocess_history(history_data)
#         preprocessed_subscriptions = await preprocessor.preprocess_subscriptions(subscriptions_data)
        
#         # 스트리밍 제너레이터 함수 정의
#         async def analysis_generator():
#             try:
#                 # 1. 시간대별 통계 분석 및 전송
#                 hourly_stats = await analyzer.extract_hourly_channel_stats(preprocessed_history)
#                 hourly_response = {
#                     "function": "hourly_stats",
#                     "status": "success",
#                     "data": hourly_stats
#                 }
#                 yield json.dumps(hourly_response) + "\n"
                
#                 # 2. 키워드 분석 및 전송
#                 keyword_frequency = await analyzer.extract_keywords({
#                     "history": preprocessed_history,
#                     "subscriptions": preprocessed_subscriptions
#                 })
#                 # Pydantic 모델을 dict로 변환
#                 keyword_data = [{"keyword": kw.keyword, "frequency": kw.frequency} for kw in keyword_frequency]
#                 keyword_response = {
#                     "function": "keyword_frequency",
#                     "status": "success",
#                     "data": keyword_data
#                 }
#                 yield json.dumps(keyword_response) + "\n"
                
#                 # 3. LLM 분석 및 전송
#                 llm_analysis = await analyzer.generate_llm_analysis({
#                     "hourly_stats": hourly_stats,
#                     "keyword_frequency": keyword_frequency
#                 })
#                 llm_response = {
#                     "function": "llm_analysis",
#                     "status": "success",
#                     "data": llm_analysis
#                 }
#                 yield json.dumps(llm_response) + "\n"
                
#                 # 4. 최종 완료 메시지 (선택사항)
#                 final_response = {
#                     "function": "completion",
#                     "status": "success",
#                     "message": "분석이 완료되었습니다."
#                 }
#                 yield json.dumps(final_response) + "\n"
                
#             except Exception as e:
#                 error_response = {
#                     "function": "error",
#                     "status": "error",
#                     "message": str(e)
#                 }
#                 yield json.dumps(error_response) + "\n"
        
#         # StreamingResponse 반환
#         return StreamingResponse(
#             analysis_generator(),
#             media_type="application/json",
#             headers={"X-Content-Type-Options": "nosniff"}
#         )
        
#     except json.JSONDecodeError:
#         raise HTTPException(
#             status_code=400,
#             detail="업로드된 파일 중 하나의 JSON 형식이 올바르지 않습니다."
#         )
#     except Exception as e:
#         raise HTTPException(
#             status_code=500,
#             detail=str(e)
#         )
