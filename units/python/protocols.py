#
#  protocols.py - Standard Python & MCP Architecture Rules
#  (Level 2: Unit Protocols - Software Engineering / Python)
#

class PythonProtocols:
    """
    [사용자] Python 유닛 전용 전문 기술 수칙입니다.
    상위 규약은 회선(Circuit)에서 상속받으므로, 여기서는 기술 본질에만 집중합니다. 
    """
    OVERVIEW = "모든 파이썬 코드를 작성할 때는 아래 기술 수칙들을 단 하나의 예외 없이 엄격히 준수해야 한다. "

    @classmethod
    def get_rules(cls):
        UNIT_RULES = [
            "Protocol P-1 (Strict Type Hinting): 모든 함수와 변수에 명확한 타입 힌팅을 적용하여 데이터 흐름을 가시화한다. ",
            "Protocol P-2 (Async IO Priority): 입출력(I/O) 중심 로직은 반드시 async/await를 사용하여 비동기로 처리한다. ",
            "Protocol P-3 (Pythonic Naming): 약어 사용을 지양하고 스네이크 케이스(snake_case)의 명확한 명칭을 사용한다. ",
            "Protocol P-4 (Standard Documentation): 모든 클래스와 공개 메서드에 Google/Numpy 스타일의 독스트링을 작성한다. ",
            "Protocol P-5 (PEP 8 Standard): 파이썬 공식 코딩 스타일 가이드를 준수하여 코드의 일관성을 유지한다. ",
            "Protocol P-6 (Logic Simplicity): 복잡한 추상화보다 직관적이고 단순한(KISS) 파이썬 로직 작성을 지향한다. "
        ]
        return UNIT_RULES
