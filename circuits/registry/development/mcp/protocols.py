#
#  protocols.py - MCP 프로젝트 전용 규약 (Auto-Detect Path) 🛡️⚡️
#

import os

class Protocols:
    PROJECT_NAME = "Operator (교환)"
    # 상위 4단계 폴더로 이동 (mcp -> development -> registry -> circuits -> root)
    PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))))
    
    RULES = [
        "Protocol P-1 (엄격한 정체성): 모든 코드에 엄격한 타입 힌팅을 적용하여 데이터의 흐름을 명확히 한다. (Any 사용 금지)",
        "Protocol P-2 (무결성 검증): Pydantic을 사용하여 데이터 스키마를 엄격히 검증하고 안정성을 확보한다.",
        "Protocol P-3 (안정적 비동기): Async/Await를 생활화하고, 에러 마스킹을 통해 시스템이 멈추지 않게 관리한다.",
        "Protocol P-4 (독립적 도구): 각 도구는 단일 책임을 가지며, 서로 간섭하지 않도록 모듈화하여 격리한다.",
        "Protocol W-1 (비개발자 중심 관제): 웹 인터페이스는 기술적 용어를 배제하고 'AI 행동 규약(Protocols) 관리'라는 본질에 집중한다. 기획자가 한글로 AI의 미션과 수칙을 직관적으로 제어할 수 있는 'Circuits' 미학을 유지한다.",
        "Protocol W-2 (세로형 반응형 구조): 모든 웹 컨텐츠는 모바일 대응을 위해 가로 배치보다 세로 적층(Vertical Stacking) 구조를 우선시한다. 특히 핵심 정보와 보조 정보가 가로로 배치되어 가독성을 해치지 않도록 Circuits별 유연한 레이아웃을 설계한다.",
        "Protocol W-3 (언어 정체성 및 일관성): 영어가 원어인 핵심 용어(예: Circuits, Protocols)는 억지로 번역하지 않고 원어 그대로 사용하며, 한글과 영어를 모호하게 혼용하지 않는다. 이는 UI, 규약 정의, 시스템 메시지 전체에 일관되게 적용하여 전문적인 지휘 환경을 유지한다."
    ]

    @classmethod
    def get_summary(cls) -> dict:
        return {
            "name": cls.PROJECT_NAME,
            "rules": cls.RULES
        }
