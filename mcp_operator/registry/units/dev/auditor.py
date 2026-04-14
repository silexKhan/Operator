#
#  auditor.py - Universal Development Auditor
#

import re
import os
import ast
from mcp_operator.engine.interfaces import BaseAuditor

class DevAuditor(BaseAuditor):
    """[사용자] 코드의 기술적 무결성과 스타일을 검증하는 감사관입니다."""

    def __init__(self, logger=None):
        super().__init__(logger)

    def audit(self, file_path: str, content: str = "") -> list[str]:
        results = []
        
        # 1. Self-Documenting 검사 (C-3)
        if file_path.endswith(".py"):
            try:
                tree = ast.parse(content)
                for node in ast.walk(tree):
                    if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
                        if not ast.get_docstring(node):
                            results.append(f" FAIL: [C-3] '{node.name}'에 Docstring이 누락되었습니다.")
            except:
                pass # 문법 에러는 다른 툴에서 처리

        # 2. Type Safety 검사 (C-2) - 간단한 키워드 체크
        if ": any" in content or "as any" in content:
            results.append(" WARNING: [C-2] 'any' 타입 사용이 감지되었습니다. 구체적인 타입 정의를 권장합니다.")

        # 3. No Hacks (C-5)
        hacks = ["@ts-ignore", "eslint-disable", "no-explicit-any"]
        for hack in hacks:
            if hack in content:
                results.append(f" FAIL: [C-5] 규칙 억제 해킹('{hack}')이 발견되었습니다.")

        return results
