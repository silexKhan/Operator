#
#  protocols.py - Professional PRD & Planning Document Rules
#  (Level 2: Unit Protocols - Documentation / Markdown)
#

class MarkdownProtocols:
    """
    [대장님 🎯] 마크다운 유닛 전용 기획 및 문서화 수칙입니다.
    기획자의 의도가 AI에게 왜곡 없이 전달되도록 문서의 무결성을 감시합니다. 📝⚡️
    """

    @classmethod
    def get_rules(cls):
        UNIT_RULES = [
            "Protocol M-1 (PRD Integrity): 문서 내에 '목표', '배경', '상세 기능', '기대 효과' 섹션을 반드시 포함한다. 📝",
            "Protocol M-2 (Terminology): '유저' 대신 '사용자'라는 공식 용어를 일관되게 사용한다. 🗣️",
            "Protocol M-3 (Date Standard): 모든 날짜 표기는 'YYYY-MM-DD' 형식을 엄격히 준수한다. 📅",
            "Protocol M-4 (Hierarchical Structure): H1(#)은 문서의 제목으로 한 번만 사용하며, 섹션은 H2(##) 이상으로 계층화한다. 🏗️",
            "Protocol M-5 (Literal Specification): '중략', '생략', '...' 표현을 금지하며 모든 명세는 리터럴 텍스트로 완성한다. 🛠️",
            "Protocol M-6 (Evidence Based): 기획안에는 정량적 수치(KPI) 또는 명확한 정성적 기대 효과가 기술되어야 한다. 📊",
            "Protocol M-7 (Tabular Representation): 정형화된 정보나 비교 분석이 필요한 내용은 반드시 테이블(Table) 형식을 사용하여 가독성을 극대화한다. 📋",
            "Protocol M-8 (Visual Modeling): 흐름(Flow) 설명 시에는 UML을, 구조 설명 시에는 아키텍처 다이어그램을 그려 시각적 명확성을 확보한다. 🗺️"
        ]
        return UNIT_RULES
