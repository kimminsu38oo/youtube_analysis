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

    async def preprocess_likes(self, likes_data: Dict[str, Any]) -> List[Dict[str, str]]:
        """
        좋아요 누른 데이터 전처리
        Returns:
            동영상 제목, 동영상 설명, 채널 명 추출
        Example Returns:
        [
            {
                'title': '내 컴퓨터도 이렇게 돼있으면 무조건 보세요',
                'description': '#컴퓨터 #직장인 #노트북 #PC #대학생\n모든문의 : test@test.com',
                'channel': '1분미만'
            },
            {
                'title': '아는 형님 하이라이트',
                'description': '207cm 서장훈\n키 작다고 놀리는 유일한 존재 하승진',
                'channel': 'JTBC Voyage'
            }
        ]
        """
        try:
            processed_data = []
            items = likes_data.get('items', [])
            
            for item in items:
                snippet = item.get('snippet', {})
                
                # 필요한 정보만 추출
                processed_item = {
                    'title': snippet.get('title', 'Deleted video'),
                    'description': snippet.get('description', '').strip(),
                    'channel': snippet.get('videoOwnerChannelTitle', 'Unknown Channel')
                }
                
                # 유효한 동영상 데이터만 포함
                if processed_item['title'] != 'Deleted video' and processed_item['channel'] != 'Unknown Channel':
                    # 설명 텍스트 처리
                    if not processed_item['description']:
                        processed_item['description'] = 'No description'
                    elif len(processed_item['description']) > 500:
                        processed_item['description'] = processed_item['description'][:500] + '...'
                    
                    processed_data.append(processed_item)
            
            return processed_data
            
        except Exception as e:
            self.logger.error(f"Likes preprocessing failed: {str(e)}")
            raise Exception(f"Likes preprocessing failed: {str(e)}")

    async def preprocess_subscriptions(self, data: Dict[str, Any]) -> List[Dict[str, str]]:
        """
        구독 채널 데이터 전처리
        Returns:
            구독한 채널 명, 채널 설명 추출
        Example Returns:
        [
            {
                'title': '스포타임',
                'description': "'스포타임(SPOTIME)'은 SPOTV의 영상 콘텐츠 브랜드입니다."
            },
            {
                'title': 'MBCNEWS',
                'description': 'MBC 뉴스 공식 유튜브 채널입니다. 시청자 여러분의 의견과 제보를 항상 기다립니다.'
            }
        ]
        """
        try:
            processed_data = []
            items = data.get('items', [])  # items 키로 접근
            
            for item in items:  # items 리스트를 순회
                snippet = item.get('snippet', {})
                
                # 필요한 필드 추출
                processed_item = {
                    'title': snippet.get('title', 'Unknown Channel'),
                    'description': snippet.get('description', '').strip()
                }
                
                # 유효한 채널만 포함
                if processed_item['title'] != 'Unknown Channel':
                    # 빈 설명 처리
                    if not processed_item['description']:
                        processed_item['description'] = 'No description'
                        
                    # 긴 설명 자르기
                    if len(processed_item['description']) > 500:
                        processed_item['description'] = processed_item['description'][:500] + '...'
                    
                    processed_data.append(processed_item)
            
            return processed_data
            
        except Exception as e:
            self.logger.error(f"Subscriptions preprocessing failed: {str(e)}")
            raise Exception(f"Subscriptions preprocessing failed: {str(e)}")