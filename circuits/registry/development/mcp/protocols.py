#
#  protocols.py - MCP 프로젝트 전용 규약 (Auto-Detect Path) 
#

import os

class Protocols:
    PROJECT_NAME = "Operator (교환)"
    # 상위 4단계 폴더로 이동 (mcp -> development -> registry -> circuits -> root)
    PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))))
    
    RULES = [
        "Protocol P-1 (데이터 계약 무결성): Pydantic 등을 활용하여 데이터 스키마를 엄격히 검증하고 시스템 전반의 안정성을 확보한다. ",
        "Protocol P-2 (독립적 도구 설계): 각 도구(Action)는 단일 책임을 가지며, 서로 간섭하지 않도록 모듈화하여 철저히 격리한다. ",
        "Protocol W-1 (사용자 중심 관제): 웹 인터페이스는 기술적 용어를 배제하고 'AI 행동 규약 관리'라는 본질적 가치에 집중한다. ",
        "Protocol W-2 (Circuits 미학 유지): 모든 UI는 세로형 반응형 구조를 우선시하며 핵심 정보의 가독성을 해치지 않는 레이아웃을 설계한다. ",
        "Protocol W-3 (일관된 언어 체계): Circuits, Protocols 등 핵심 용어는 원어 그대로 사용하며 UI와 시스템 전체에 일관되게 적용한다. "
    ]

    @classmethod
    def get_summary(cls) -> dict:
        return {
            "name": cls.PROJECT_NAME,
            "rules": cls.RULES
        }
