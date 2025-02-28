# app/services/analyzer.py
from typing import Dict, Any, List, Counter
import logging
from app.schemas.models import AnalysisData, KeywordFrequency
from collections import defaultdict

class DataAnalyzer:
    def __init__(self):
        self.logger = logging.getLogger(__name__)

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

            return result

        except Exception as e:
            self.logger.error(f"Hourly channel stats extraction failed: {str(e)}")
            raise Exception(f"Hourly channel stats extraction failed: {str(e)}")

    async def extract_keywords(self, preprocessed_data: Dict[str, Any]) -> List[KeywordFrequency]:
        """키워드 빈도 분석"""
        try:
            # TODO: Implement keyword frequency analysis
            return [
                KeywordFrequency(keyword="음악", frequency=150),
                KeywordFrequency(keyword="게임", frequency=100)
            ]
        except Exception as e:
            raise Exception(f"Keyword extraction failed: {str(e)}")

    async def generate_llm_analysis(self, analysis_results: Dict[str, Any]) -> str:
        """LLM 기반 텍스트 분석 생성"""
        try:
            # TODO: Implement LLM analysis
            return "사용자는 주로 저녁 시간대에 엔터테인먼트 콘텐츠를 시청하는 경향이 있습니다."
        except Exception as e:
            raise Exception(f"LLM analysis failed: {str(e)}")

    async def analyze_data(self, 
                        history_data: Dict[str, Any],
                        likes_data: Dict[str, Any],
                        subscriptions_data: Dict[str, Any]) -> AnalysisData:
        """
        전체 데이터 분석 수행
        Args:
            history_data: 시청 기록 데이터
            likes_data: 좋아요 데이터
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
                "likes": likes_data,
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