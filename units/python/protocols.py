#
#  protocols.py - Standard Python & MCP Architecture Rules
#  (Level 2: Unit Protocols - Software Engineering / Python)
#

class PythonProtocols:
    """
    [대장님 🎯] Python 유닛 전용 전문 기술 수칙입니다.
    상위 규약은 회선(Circuit)에서 상속받으므로, 여기서는 기술 본질에만 집중합니다. 🐍⚡️
    """

    @classmethod
    def get_rules(cls):
        UNIT_RULES = [
            "Protocol P-1 (Strict Type Hinting): Return type '->' mandatory 🏷️",
            "Protocol P-2 (Pydantic Usage): BaseModel for Data Contracts 📥",
            "Protocol P-3 (Async IO): async/await for Core logic 🏎️",
            "Protocol P-4 (Clean Naming): No Abbreviations (view_controller over vc) 🧼",
            "Protocol P-5 (Standard Docstrings): Google/Numpy Style 📝",
            "Protocol P-6 (PEP 8): Surgical Formatting Only 📏",
            "Protocol P-7 (Single Responsibility): KISS 원칙 준수 🏗️"
        ]
        return UNIT_RULES
