#
#  axioms.py - Standard Python & MCP Architecture Rules
#  (Level 2: Tenant Axioms - Software Engineering / Python)
#

from shared.hub_axioms import HubAxioms

class PythonAxioms(HubAxioms):
    """
    Python 및 MCP 허브 개발 도메인을 위한 테넌트 공리입니다.
    최상위 HubAxioms를 상속받아 기술 스택 특화 규칙을 정의합니다. 🐍🚀
    """

    # --- [Architecture Rules] ---
    STRICT_TYPE_HINTING = True
    PYDANTIC_MANDATORY = True
    ASYNC_IO_REQUIRED = True
    
    # [대장님 🎯] Naming: vc, nav 등 축약어 금지. 명확한 의도를 담은 풀네임 사용 🧼
    CLEAN_NAMING_STRICT = True 
    
    # [대장님 🎯] Docstring: 모든 public 메서드에 Google/Numpy 스타일 docstring 필수 📝
    DOCSTRING_MANDATORY = True
    
    @classmethod
    def get_rules(cls):
        """
        부모(HubAxioms)의 글로벌 규칙과 Python 테넌트 전용 규칙을 재귀적으로 병합하여 반환합니다.
        """
        python_rules = [
            "Strict Type Hinting (Return type '->' mandatory) 🏷️",
            "Pydantic BaseModel for Data Contracts 📥",
            "Asynchronous IO (async/await) for Core logic 🏎️",
            "No Abbreviations (view_controller over vc) 🧼",
            "Standard Docstrings (Google/Numpy Style) 📝",
            "PEP 8 Compliance (Surgical Formatting Only) 📏"
        ]
        # Level 1 (Global) + Level 2 (Tenant) 규칙 결합
        return super().get_rules() + python_rules
