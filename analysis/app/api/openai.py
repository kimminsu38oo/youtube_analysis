import json
import os
import logging
from openai import OpenAI
from typing import Dict, Any, Optional, Union

class OpenAIClient:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

    async def create_chat_completion(
        self,
        model: str,
        system_prompt: str,
        context: Dict[str, Any],
        temperature: float = 0.7,
        response_format: Optional[Dict[str, str]] = None,
        max_tokens: Optional[int] = None
    ) -> Union[str, Dict[str, Any]]:
        """
        OpenAI API를 호출하여 chat completion을 생성합니다.
        
        Args:
            model: 사용할 OpenAI 모델 이름
            system_prompt: 시스템 프롬프트 내용
            context: 사용자 메시지로 전달될 컨텍스트
            temperature: 생성 모델의 temperature 값
            response_format: 응답 형식 (예: {"type": "json_object"})
            max_tokens: 최대 토큰 수
            
        Returns:
            API 응답으로부터 추출한 텍스트 또는 JSON 객체
        """
        try:
            # API 호출 파라미터 구성
            params = {
                "model": model,
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": json.dumps(context, ensure_ascii=False)}
                ],
                "temperature": temperature
            }
            
            # 선택적 파라미터 추가
            if response_format:
                params["response_format"] = response_format
                
            if max_tokens:
                params["max_tokens"] = max_tokens
            
            # API 호출
            response = self.client.chat.completions.create(**params)
            
            # 응답 추출
            content = response.choices[0].message.content.strip()
            
            # JSON 응답이 요청된 경우 파싱
            if response_format and response_format.get("type") == "json_object":
                try:
                    return json.loads(content)
                except json.JSONDecodeError as e:
                    self.logger.error(f"JSON 파싱 실패: {e}")
                    return content
            
            return content
            
        except Exception as e:
            self.logger.error(f"OpenAI API 호출 실패: {str(e)}")
            raise