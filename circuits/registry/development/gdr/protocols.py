#
#  protocols.py - GDR 프로젝트 핵심 규약 (Project Alpha) 🛡️⚡️
#

class Protocols:
    PROJECT_NAME = "GDR (프로젝트 알파)"
    
    # [대장님 🎯] 골프존 GDR 개발 시 AI가 준수해야 할 5대 핵심 규약(Protocols)입니다. 🛡️⚡️
    RULES = [
        "Protocol 1: 안전 제일 (Force Unwrapping '!' 절대 사용 금지)",
        "Protocol 2: 엄격한 MVVM 준수 (View는 데이터 전달만 수행하는 'Dumb View' 유지)",
        "Protocol 3: 의도 중심 ViewModel (Input/Output 구조체와 transform 함수가 유일한 명세)",
        "Protocol 4: Combine 명명 규격 (Private Subject 변수에 'Subject' 접미사 사용 금지)",
        "Protocol 5: 이중 언어 커밋 (한글/영어 병행, 제목 + 항목별 본문 구성)"
    ]

    @classmethod
    def get_summary(cls) -> dict:
        return {
            "이름": cls.PROJECT_NAME,
            "규약목록": cls.RULES
        }
