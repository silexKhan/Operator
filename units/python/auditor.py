#
#  auditor.py - Python & MCP Code Auditor
#

import re
import os
from units.python.protocols import PythonProtocols

class PythonAuditor:
    def __init__(self, logger=None):
        self.logger = logger

    def log(self, msg, level=1):
        if self.logger:
            self.logger.log(msg, level)

    def audit(self, file_path: str, content: str) -> list[str]:
        results = []
        self.log(f"Python 전문 유닛 감사 시작 - 파일: {os.path.basename(file_path)}", 1)

        # 1. Strict Type Hinting (Protocol P-1)
        # 함수 정의에서 -> 가 없는 경우 찾기
        missing_hints = re.findall(r"def\s+\w+\(.*\)(?!\s*->)", content)
        if missing_hints:
            self.log("Type Hinting 위반 발견", 2)
            results.append(" FAIL: Protocol P-1 (Strict Type Hinting) - 함수 반환 타입을 '->'를 통해 명시하십시오.")

        # 2. Pydantic Usage (Protocol P-2)
        if ("/shared/" in file_path or "/models/" in file_path) and "BaseModel" not in content:
            self.log("Pydantic 미사용 발견", 2)
            results.append(" FAIL: Protocol P-2 (Pydantic Usage) - 공용 데이터 모델은 Pydantic BaseModel을 사용하십시오.")

        # 3. Async/Await (Protocol P-3)
        if ("main.py" in file_path or "/core/" in file_path) and "async def" not in content and "def " in content:
            self.log("Async IO 위반 의심", 1)
            results.append(" WARNING: Protocol P-3 (Async IO) - MCP 코어 로직은 비동기(async def)를 권장합니다.")

        # 4. Naming Convention (Protocol P-4)
        bad_names = ["vc", "nav", "topVC", "vc_controller"]
        for name in bad_names:
            if f" {name} " in content or f"={name}" in content or f"{name}=" in content:
                self.log(f"Naming 위반 발견: {name}", 2)
                results.append(f" FAIL: Protocol P-4 (Clean Naming) - 축약어({name}) 대신 풀네임(view_controller, navigation)을 사용하십시오.")
                break

        # 5. Docstring Mandatory (Protocol P-5)
        # 함수나 클래스 선언 바로 아래에 """ 가 없는 경우 (간단한 정규식 체크)
        functions = re.findall(r"(def|class)\s+\w+\(.*\):", content)
        docstrings = re.findall(r'"""[\s\S]*?"""', content)
        if len(functions) > len(docstrings) + 2: # 약간의 여유를 줌 (내부 함수 등 고려)
            self.log("Docstring 부족 감지", 1)
            results.append(" Protocol P-5 (Standard Docstrings) - 주요 함수/클래스에 대한 Docstring 작성을 권장합니다. ")

        # 6. Mechanical Integrity (Global Protocol 0-1)
        if "..." in content or "중략" in content:
            self.log("Mechanical Integrity 위반 발견", 2)
            results.append(" FAIL: Protocol 0-1 (Mechanical Integrity) - 코드 내에 '...' 또는 '중략'을 사용하지 마십시오. 완전한 리터럴 텍스트가 필요합니다. ")

        return results
