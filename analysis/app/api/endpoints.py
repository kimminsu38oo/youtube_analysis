# # app/api/endpoints.py
# from fastapi import APIRouter, UploadFile, File, HTTPException
# from ..schemas.models import AnalysisResult
# from fastapi.responses import StreamingResponse
# from ..services.analysis_service import process_analysis_request, process_streaming_analysis
# import json

# router = APIRouter()

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
        
#         # 분석 서비스 호출
#         analysis_data = await process_analysis_request(history_data, subscriptions_data)
        
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
        
#         # 스트리밍 서비스 호출
#         return StreamingResponse(
#             process_streaming_analysis(history_data, subscriptions_data),
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
        
        # 분석 서비스 호출 (analysis_id 전달)
        analysis_data = await process_analysis_request(
            history_data, 
            subscriptions_data,
            analysis_id=analysis_id  # analysis_id 전달
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
        
        # 스트리밍 서비스 호출 (analysis_id 전달)
        return StreamingResponse(
            process_streaming_analysis(
                history_data, 
                subscriptions_data,
                analysis_id=analysis_id  # analysis_id 전달
            ),
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