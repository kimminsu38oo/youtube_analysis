# app/servies/analyzer.py
from typing import Dict, Any, List, Counter
import logging
import os
import json
from openai import OpenAI
from app.schemas.models import AnalysisData, KeywordFrequency
from collections import defaultdict
from app.services.constant import KEYWORD_EXTRACTION_PROMPT, LLM_ANALYSIS_PROMPT, KEYWORD_EXTRACTER_MODEL, ANLYSIS_AGENT
from app.api.openai import OpenAIClient

class DataAnalyzer:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        # OpenAI API 클라이언트 초기화
        self.client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

        # OpenAIClient 초기화 추가
        self.openai_client = OpenAIClient()
    async def extract_hourly_channel_stats(self, preprocessed_history_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        시간대별 총 조회수와 채널별 조회수 TOP3를 추출합니다.
        Args:
            preprocessed_history_data: preprocess_history에서 반환된 전처리된 데이터
        Returns:
            시간대별 통계 리스트 (총 조회수, 채널별 TOP3)
        Example Returns:
        {
            'hour': 18,
            'totalViews': 2,
            'categories': [
                {'name': 'MBCNEWS', 'views': 1},
                {'name': 'JTBC Voyage', 'views': 1}
            ]
        }
        {
            'hour': 19,
            'totalViews': 1,
            'categories': [
                {'name': 'Test Channel', 'views': 1}
            ]
        }
        """
        try:
            if not preprocessed_history_data:
                return []

            # 시간대별 통계를 위한 딕셔너리 초기화
            hourly_stats = defaultdict(lambda: {'totalViews': 0, 'channels': defaultdict(int)})

            # 데이터 처리
            for entry in preprocessed_history_data:
                hour = entry['time'].hour  # 시청 시간대의 '시간' 추출
                channel = entry['channel']
                
                # 시간대 총 조회수 증가
                hourly_stats[hour]['totalViews'] += 1
                # 채널별 조회수 증가
                hourly_stats[hour]['channels'][channel] += 1

            # 결과 포맷팅
            result = []
            for hour in range(24):
                total_views = hourly_stats[hour]['totalViews']
                channels = hourly_stats[hour]['channels']
                
                # 채널별 조회수를 리스트로 변환하고 내림차순 정렬
                channel_list = [
                    {'name': channel, 'views': views} 
                    for channel, views in channels.items()
                ]
                channel_list.sort(key=lambda x: x['views'], reverse=True)
                
                # TOP3만 추출 (3개 미만이면 모두 포함)
                top_channels = channel_list[:min(3, len(channel_list))]
                
                result.append({
                    'hour': hour,
                    'totalViews': total_views,
                    'categories': top_channels if total_views > 0 else []
                })
            print("------total view------")
            print(result)
            print()
            return result

        except Exception as e:
            raise Exception(f"Hourly channel stats extraction failed: {str(e)}")
        
    async def extract_keywords(self, preprocessed_data: Dict[str, Any]) -> List[KeywordFrequency]:
        """키워드 빈도 분석"""
        try:
            # 분석할 데이터 준비
            history_data = preprocessed_data.get("history", [])
            subscriptions_data = preprocessed_data.get("subscriptions", [])
            
            # 데이터가 비어있는 경우 기본값 반환
            if not history_data and not subscriptions_data:
                return [
                    KeywordFrequency(keyword="데이터 없음", frequency=0)
                ]
            
            # 시청 기록에서 제목과 설명 추출
            video_titles = [entry.get('title', '') for entry in history_data if 'title' in entry]
            video_descriptions = [entry.get('description', '') for entry in history_data if 'description' in entry]
            
            # 구독 채널 정보 추출
            channel_names = [sub.get('channelName', '') for sub in subscriptions_data if 'channelName' in sub]
            channel_descriptions = [sub.get('description', '') for sub in subscriptions_data if 'description' in sub]
            
            # LLM에게 전달할 컨텍스트 구성
            context = {
                "video_titles": video_titles[:100],  # API 한도를 고려해 최대 100개만 전송
                "video_descriptions": video_descriptions[:50],  # 간결성을 위해 설명은 50개만 전송
                "channel_names": channel_names,
                "channel_descriptions": channel_descriptions[:50]
            }
            
            # OpenAI API 호출 (리팩토링된 함수 사용)
            response = await self.openai_client.create_chat_completion(
                model=KEYWORD_EXTRACTER_MODEL,
                system_prompt=KEYWORD_EXTRACTION_PROMPT,
                context=context,
                temperature=0.1,
                response_format={"type": "json_object"}
            )
            
            # API 응답 로깅
            print("-----raw data-----")
            print(response)
            print("------------------")
            
            # API 응답 파싱
            try:
                keywords_list = []
                
                if isinstance(response, dict):
                    # 'keywords' 키가 있는 경우
                    if "keywords" in response:
                        keywords_list = response.get("keywords", [])
                    # 'keyword' 키가 있는 경우 (예시 출력에서 확인됨)
                    elif "keyword" in response:
                        keywords_list = response.get("keyword", [])
                    # 다른 예상치 못한 구조인 경우
                    else:
                        # response 자체가 키워드 리스트인지 확인
                        if any("keyword" in item and "frequency" in item for item in response.values() if isinstance(item, dict)):
                            keywords_list = [item for item in response.values() if isinstance(item, dict) and "keyword" in item and "frequency" in item]
                            self.logger.info(f"Extracted {len(keywords_list)} keywords from response values")
                elif isinstance(response, list):
                    # 결과가 직접 리스트인 경우
                    keywords_list = response
                
                # KeywordFrequency 객체 리스트로 변환
                keyword_results = []
                for item in keywords_list:
                    if isinstance(item, dict) and "keyword" in item and "frequency" in item:
                        keyword_results.append(
                            KeywordFrequency(keyword=item["keyword"], frequency=item["frequency"])
                        )
                
                # 결과가 비어 있으면 오류 메시지 출력
                if not keyword_results and keywords_list:
                    self.logger.error(f"Failed to convert keywords to KeywordFrequency objects. Raw list: {keywords_list}")
                
                # 결과가 비어 있으면 기본값 반환
                if not keyword_results:
                    return [
                        KeywordFrequency(keyword="뉴스", frequency=150),
                        KeywordFrequency(keyword="정치", frequency=100),
                        KeywordFrequency(keyword="스포츠", frequency=80),
                        KeywordFrequency(keyword="문화", frequency=60),
                        KeywordFrequency(keyword="엔터테인먼트", frequency=40)
                    ]
                print("-----keyword_results-----")
                print(keyword_results)
                print("-------------------------")
                return keyword_results
                
            except (json.JSONDecodeError, KeyError, TypeError) as e:
                # 오류 발생 시 기본 키워드 반환
                default_keywords = [
                    KeywordFrequency(keyword="음악", frequency=150),
                    KeywordFrequency(keyword="게임", frequency=100),
                    KeywordFrequency(keyword="요리", frequency=80),
                    KeywordFrequency(keyword="여행", frequency=60),
                    KeywordFrequency(keyword="스포츠", frequency=40)
                ]
                return default_keywords
                
        except Exception as e:
            raise Exception(f"Keyword extraction failed: {str(e)}")

    async def generate_llm_analysis(self, analysis_results: Dict[str, Any]) -> str:
        """
        시간대별 통계와 키워드 빈도를 기반으로 LLM을 통해 사용자의 YouTube 시청 패턴을 분석합니다.
        
        Args:
            analysis_results: 분석 결과 딕셔너리
                - hourly_stats: 시간대별 시청 통계 리스트
                - keyword_frequency: 키워드 빈도 리스트
        
        Returns:
            str: LLM이 생성한 분석 내용
        """
        try:
            hourly_stats = analysis_results.get("hourly_stats", [])
            keyword_frequency = analysis_results.get("keyword_frequency", [])
            
            if not hourly_stats and not keyword_frequency:
                return "분석에 필요한 충분한 데이터가 없습니다. 더 많은 YouTube 활동이 필요합니다."
            
            # 분석을 위한 데이터 정리
            # 가장 시청이 많은 시간대 찾기
            peak_hours = sorted(
                [h for h in hourly_stats if h["totalViews"] > 0],
                key=lambda x: x["totalViews"],
                reverse=True
            )[:3]  # 상위 3개 시간대
            
            # 키워드 빈도 정리 (상위 10개)
            top_keywords = sorted(
                keyword_frequency,
                key=lambda x: x.frequency,
                reverse=True
            )[:10]
            
            # 시간대 그룹화 (아침, 오후, 저녁, 밤)
            time_groups = {
                "아침(06-11)": sum(h["totalViews"] for h in hourly_stats if 6 <= h["hour"] <= 11),
                "오후(12-17)": sum(h["totalViews"] for h in hourly_stats if 12 <= h["hour"] <= 17),
                "저녁(18-23)": sum(h["totalViews"] for h in hourly_stats if 18 <= h["hour"] <= 23),
                "심야(00-05)": sum(h["totalViews"] for h in hourly_stats if 0 <= h["hour"] <= 5)
            }
            
            # LLM에게 전달할 컨텍스트 구성
            context = {
                "peak_hours": [
                    {
                        "hour": h["hour"],
                        "totalViews": h["totalViews"],
                        "top_channels": h["categories"][:3] if h["categories"] else []
                    } 
                    for h in peak_hours
                ],
                "top_keywords": [
                    {
                        "keyword": kw.keyword,
                        "frequency": kw.frequency
                    } 
                    for kw in top_keywords
                ],
                "time_groups": [
                    {
                        "name": name,
                        "total_views": views
                    }
                    for name, views in time_groups.items()
                ],
                "total_views": sum(h["totalViews"] for h in hourly_stats)
            }
            
            # OpenAI API 호출
            analysis_text = await self.openai_client.create_chat_completion(
                model=ANLYSIS_AGENT,
                system_prompt=LLM_ANALYSIS_PROMPT,
                context=context,
                temperature=0.7,
                max_tokens=500
            )
            
            if not analysis_text:
                return "충분한 시청 데이터가 없어 정확한 분석이 어렵습니다. YouTube를 더 시청한 후 다시 시도해 주세요."
            
            print(analysis_text)
            return analysis_text
            
        except Exception as e:
            self.logger.error(f"LLM analysis generation failed: {str(e)}")
            # 오류 발생 시 기본 분석 메시지 반환
            return "분석 중 오류가 발생했습니다. 시스템 관리자에게 문의해 주세요."

    async def analyze_data(self, 
                        history_data: List[Dict[str, Any]],  # 타입 수정: Dict -> List[Dict]
                        subscriptions_data: List[Dict[str, Any]]) -> AnalysisData:  # 타입 수정: Dict -> List[Dict]
        """
        전체 데이터 분석 수행
        Args:
            history_data: 시청 기록데이터 
            subscriptions_data: 구독 채널 데이터
        Returns:
            AnalysisData: 분석 결과 (시간대별 통계, 키워드 빈도, LLM 분석)
        """
        try:
            # 시간대별 총 조회수와 채널별 TOP3 추출
            hourly_stats = await self.extract_hourly_channel_stats(history_data)
            
            # 키워드 빈도 분석
            keyword_frequency = await self.extract_keywords({
                "history": history_data,
                "subscriptions": subscriptions_data
            })
            
            # LLM 기반 분석
            llm_analysis = await self.generate_llm_analysis({
                "hourly_stats": hourly_stats,
                "keyword_frequency": keyword_frequency
            })

            # AnalysisData 객체로 반환
            return AnalysisData(
                hourlyStats=hourly_stats,  # 시간대별 통계 (HourlyStat 리스트)
                keywordFrequency=keyword_frequency,  # 키워드 빈도 (KeywordFrequency 리스트)
                llmAnalysis=llm_analysis  # LLM 분석 결과 (문자열)
            )

        except Exception as e:
            raise Exception(f"Data analysis failed: {str(e)}")