# app/services/preprocessor.py
from typing import Dict, Any, List
import logging
from datetime import datetime

class DataPreprocessor:
    def __init__(self):
        self.logger = logging.getLogger(__name__)

    async def preprocess_history(self, history_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        시청 기록 데이터 전처리
        Returns:
            동영상 제목, 채널명, 시청한 시각 추출
        Example Returns:
        [
            {
                'title': '아형 최장신 서장훈 키로 놀리며 하극상',
                'channel': 'JTBC Voyage,
                'time': datetime.datetime(2025, 2, 13, 13, 52, 46, 874000)
            }
        ]
        """
        try:
            if not history_data:
                return []
                
            processed_data = []
            
            for entry in history_data:
                # 채널명 추출
                channel = None
                if 'subtitles' in entry and entry['subtitles']:
                    channel = entry['subtitles'][0]['name']
                    
                # channel이 None인 경우는 건너뛰기
                if channel is None:
                    continue
                    
                processed_item = {
                    'title': entry['title'].replace('을(를) 시청했습니다.', '').strip(),
                    'channel': channel,
                    'time': None
                }
                
                # 시청 시간 처리
                time_str = entry['time']
                try:
                    time_obj = datetime.strptime(time_str, "%Y-%m-%dT%H:%M:%SZ")
                except ValueError:
                    try:
                        time_obj = datetime.strptime(time_str, "%Y-%m-%dT%H:%M:%S.%fZ")
                    except ValueError:
                        continue
                        
                processed_item['time'] = time_obj
                processed_data.append(processed_item)
            
            return processed_data
            
        except Exception as e:
            self.logger.error(f"History preprocessing failed: {str(e)}")
            raise Exception(f"History preprocessing failed: {str(e)}")

    async def preprocess_subscriptions(self, data: Any) -> List[Dict[str, str]]:
        """
        구독 채널 데이터 전처리
        Returns:
            구독한 채널 명, 채널 설명 추출
        Example Returns:
        [
            {
                'title': '살란다',
                'description': 'No description'
            }
        ]
        """
        try:
            processed_data = []

            # 데이터 형식 확인
            if isinstance(data, dict) and 'items' in data:
                # 기존 형식 처리 (items 키가 있는 딕셔너리)
                items = data.get('items', [])
                for item in items:
                    snippet = item.get('snippet', {})
                    processed_item = {
                        'title': snippet.get('title', 'Unknown Channel'),
                        'description': snippet.get('description', '').strip() or 'No description'
                    }
                    if processed_item['title'] != 'Unknown Channel':
                        if len(processed_item['description']) > 500:
                            processed_item['description'] = processed_item['description'][:500] + '...'
                        processed_data.append(processed_item)

            elif isinstance(data, list):
                # 새로운 형식 처리 (리스트)
                for item in data:
                    if isinstance(item, dict):
                        processed_item = {
                            'title': item.get('채널 제목', 'Unknown Channel'),
                            'description': 'No description'
                        }
                        if processed_item['title'] != 'Unknown Channel':
                            processed_data.append(processed_item)

            return processed_data

        except Exception as e:
            self.logger.error(f"Subscriptions preprocessing failed: {str(e)}")
            raise Exception(f"Subscriptions preprocessing failed: {str(e)}")