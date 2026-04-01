#
#  protocols.py - Professional PRD & Planning Document Rules
#  (Level 2: Unit Protocols - Documentation / Markdown)
#

class MarkdownProtocols:
    """
    [사용자] 마크다운 유닛 전용 기획 및 문서화 수칙입니다.
    기획자의 의도가 AI에게 왜곡 없이 전달되도록 문서의 무결성을 감시합니다. 
    """
    OVERVIEW = "모든 마크다운 문서를 작성할 때는 구조적 무결성과 가독성을 위해 아래 규약들을 엄격히 준수해야 한다. "

    @classmethod
    def get_rules(cls):
        UNIT_RULES = [
            "Protocol M-1 (Structural Hierarchy): H1(#) 제목은 1회만 사용하며, H2(##) 이상으로 문서의 계층 구조를 명확히 한다. ",
            "Protocol M-2 (Literal Specification): '중략', '생략', '...' 표현을 절대 금지하며 모든 명세는 리터럴 텍스트로 완성한다. ",
            "Protocol M-3 (Data Visualization): 복합 데이터나 비교 정보는 반드시 테이블(Table) 형식을 활용하여 가독성을 높인다. ",
            "Protocol M-4 (Content Consistency): 문서 전체에 걸쳐 동일한 대상을 지칭할 때 용어의 일관성을 유지한다. ",
            "Protocol M-5 (Logic Modeling): 복잡한 흐름이나 구조 설명 시 코드 블록 내 Mermaid 또는 UML 다이어그램을 활용한다. ",
            "Protocol M-6 (Reference Integrity): 문서 내 외부 링크나 에셋 참조의 무결성을 확인하고 올바른 경로를 사용한다. "
        ]
        return UNIT_RULES
