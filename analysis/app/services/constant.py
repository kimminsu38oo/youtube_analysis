# app/services/prompt.py

# 키워드 추출 프롬프트
KEYWORD_EXTRACTION_PROMPT = """
YouTube 시청기록에서 뉴스검색용 구체적 키워드 추출하라.

요구사항:
- 제공된 입력 데이터에서만 키워드 추출할 것
- 인물/유튜버 이름 중심으로 추출
- 가장 핵심적이고 이슈가 될 만한 내용 우선 추출
- 일반단어(요리,경제) 대신 구체적용어(분자요리,ESG투자) 사용
- 트렌드/기업/전문용어/지역/이벤트 포함할 것

결과는 다음 JSON 형식으로 반환:
[
    {"keyword": "키워드1", "frequency": 빈도수(1-1000 사이의 숫자)},
    {"keyword": "키워드2", "frequency": 빈도수(1-1000 사이의 숫자)},
    ...
]

제약사항: 
- 정확히 10개 키워드만 추출
- 반드시 제공된 입력 내용만 기반으로 키워드 추출
"""

# LLM 분석 프롬프트
LLM_ANALYSIS_PROMPT = """
당신은 사용자의 YouTube 시청 패턴을 분석하는 전문가입니다.
시간대별 시청 통계와 키워드 빈도 데이터를 바탕으로 사용자의 시청 습관과 관심사를 분석해 주세요.

다음을 포함한 깊이 있는 분석을 제공해 주세요:
1. 주요 시청 시간대 패턴 (아침, 오후, 저녁, 심야 중 언제 가장 활발한지)
2. 자주 시청하는 콘텐츠 유형 (키워드 기반 추론)
3. 사용자의 관심사와 취향
4. 시청 패턴에 대한 전반적인 특징

분석은 다음 형식을 따라주세요:
- 2~4개 문단으로 구성
- 한국어로 작성
- 개인 맞춤형 분석으로 명확하고 통찰력 있게 작성
- 불필요한 반복 없이 핵심 내용만 포함

중요: 사용자에게 직접 말하듯이 작성하고, 지나치게 형식적이거나 기계적인 분석은 피해주세요.
"""

# 모델
KEYWORD_EXTRACTER_MODEL = "gpt-4o-2024-11-20"
ANLYSIS_AGENT = "gpt-3.5-turbo-0125"

# 테스트 데이터 관련 상수
TEST_HOURLY_STATS = [
    {'hour': 0, 'totalViews': 7, 'categories': [
        {'name': '악어골프', 'views': 3},
        {'name': '침착맨', 'views': 2},
        {'name': '고누리', 'views': 2}
    ]},
    {'hour': 1, 'totalViews': 4, 'categories': [
        {'name': '침착맨', 'views': 2},
        {'name': '나몰라패밀리', 'views': 2}
    ]},
    {'hour': 2, 'totalViews': 0, 'categories': []},
    {'hour': 3, 'totalViews': 0, 'categories': []},
    {'hour': 4, 'totalViews': 0, 'categories': []},
    {'hour': 5, 'totalViews': 0, 'categories': []},
    {'hour': 6, 'totalViews': 3, 'categories': [
        {'name': '주주TV', 'views': 2},
        {'name': '박지성JSPARK', 'views': 1}
    ]},
    {'hour': 7, 'totalViews': 8, 'categories': [
        {'name': 'MBCNEWS', 'views': 5},
        {'name': '머니랩', 'views': 2},
        {'name': '삼프로TV', 'views': 1}
    ]},
    {'hour': 8, 'totalViews': 6, 'categories': [
        {'name': '머니랩', 'views': 3},
        {'name': '삼프로TV', 'views': 2},
        {'name': '떠먹여주는 경제', 'views': 1}
    ]},
    {'hour': 9, 'totalViews': 4, 'categories': [
        {'name': '씨네21', 'views': 2},
        {'name': '엠빅뉴스', 'views': 1},
        {'name': 'SPOTV', 'views': 1}
    ]},
    {'hour': 10, 'totalViews': 0, 'categories': []},
    {'hour': 11, 'totalViews': 0, 'categories': []},
    {'hour': 12, 'totalViews': 10, 'categories': [
        {'name': '맛객리우', 'views': 4},
        {'name': '백종원의 요리비책', 'views': 3},
        {'name': '쿠킹트리', 'views': 3}
    ]},
    {'hour': 13, 'totalViews': 14, 'categories': [
        {'name': 'MBCNEWS', 'views': 5}, 
        {'name': 'KBS Joy', 'views': 4}, 
        {'name': '1분미만', 'views': 3},
        {'name': 'MBC 공식채널', 'views': 2}
    ]},
    {'hour': 14, 'totalViews': 9, 'categories': [
        {'name': 'tvN', 'views': 4},
        {'name': '스브스케이팝', 'views': 3},
        {'name': 'HYBE LABELS', 'views': 2}
    ]},
    {'hour': 15, 'totalViews': 7, 'categories': [
        {'name': '스브스케이팝', 'views': 3},
        {'name': 'SMTOWN', 'views': 2},
        {'name': 'JYP Entertainment', 'views': 2}
    ]},
    {'hour': 16, 'totalViews': 0, 'categories': []},
    {'hour': 17, 'totalViews': 0, 'categories': []},
    {'hour': 18, 'totalViews': 18, 'categories': [
        {'name': '런닝맨 - 스브스 공식채널', 'views': 6},
        {'name': '나 혼자 산다 NAVER', 'views': 5},
        {'name': '신서유기', 'views': 4},
        {'name': '놀면 뭐하니?', 'views': 3}
    ]},
    {'hour': 19, 'totalViews': 22, 'categories': [
        {'name': '신서유기', 'views': 7},
        {'name': '나 혼자 산다 NAVER', 'views': 6},
        {'name': '대도서관', 'views': 5},
        {'name': '잇섭', 'views': 4}
    ]},
    {'hour': 20, 'totalViews': 17, 'categories': [
        {'name': '배달이요', 'views': 5},
        {'name': '잇섭', 'views': 4},
        {'name': '박씨TV', 'views': 4},
        {'name': '렌즈를 들다', 'views': 4}
    ]},
    {'hour': 21, 'totalViews': 13, 'categories': [
        {'name': '빠니보틀', 'views': 5},
        {'name': '걸어서 세계속으로', 'views': 4},
        {'name': '여행자 케빈', 'views': 4}
    ]},
    {'hour': 22, 'totalViews': 16, 'categories': [
        {'name': '밀덕딸기', 'views': 6},
        {'name': '궤도 Kuedo', 'views': 5},
        {'name': '우주과학이야기', 'views': 5}
    ]},
    {'hour': 23, 'totalViews': 9, 'categories': [
        {'name': '침착맨', 'views': 4},
        {'name': '릴카', 'views': 3},
        {'name': '풍월량', 'views': 2}
    ]}
]

TEST_KEYWORD_DATA = [
    {"keyword": "예능", "frequency": 350.0},
    {"keyword": "뉴스", "frequency": 300.0},
    {"keyword": "게임", "frequency": 280.0},
    {"keyword": "음악", "frequency": 250.0},
    {"keyword": "여행", "frequency": 220.0},
    {"keyword": "요리", "frequency": 180.0},
    {"keyword": "경제", "frequency": 160.0},
    {"keyword": "연예인", "frequency": 150.0},
    {"keyword": "스포츠", "frequency": 130.0},
    {"keyword": "과학", "frequency": 120.0},
    {"keyword": "컴퓨터", "frequency": 100.0},
    {"keyword": "IT기기", "frequency": 95.0},
    {"keyword": "아이돌", "frequency": 90.0},
    {"keyword": "가족", "frequency": 80.0},
    {"keyword": "우주", "frequency": 75.0}
]

# LLM 분석 텍스트
TEST_LLM_ANALYSIS = """
사용자의 YouTube 시청 패턴을 분석한 결과, 주로 저녁 시간대(18-22시)에 가장 활발한 시청 활동을 보이는 것으로 나타났습니다. 특히 19시에 가장 많은 시청량(22회)을 기록했으며, 주로 '신서유기', '나 혼자 산다' 등 인기 예능 프로그램과 '대도서관', '잇섭' 같은 IT/게임 관련 채널을 시청하셨습니다.

오전(7-9시)에는 'MBCNEWS'와 '머니랩' 등 뉴스와 경제 관련 콘텐츠를, 점심 시간대(12-13시)에는 '맛객리우', '백종원의 요리비책' 등 요리 관련 콘텐츠를 주로 시청하는 경향이 있습니다. 오후 시간대(14-15시)에는 음악과 엔터테인먼트 채널을 선호하며, 밤 시간대(21-22시)에는 여행과 과학 관련 콘텐츠로 전환하는 패턴을 보입니다.

키워드 분석 결과, '예능'(350), '뉴스'(300), '게임'(280)이 가장 높은 빈도를 나타내고 있어 사용자가 주로 엔터테인먼트와 정보 콘텐츠에 관심이 많은 것으로 보입니다. 또한 '음악'(250)과 '여행'(220)에 대한 관심도 높게 나타났습니다.

전체적으로 사용자는 다양한 분야에 골고루 관심을 가지고 있으며, 시간대별로 콘텐츠 소비 패턴이 뚜렷하게 구분되는 것이 특징입니다. 아침에는 정보성 콘텐츠, 저녁에는 오락성 콘텐츠를 선호하는 일반적인 시청 패턴을 보이고 있습니다. 특히 예능 프로그램과 IT/게임 관련 콘텐츠에 대한 선호도가 두드러지며, 취미와 학습을 위한 다양한 채널도 꾸준히 시청하고 있습니다.
"""