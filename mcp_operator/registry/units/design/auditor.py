#
#  auditor.py - Universal Design Auditor
#

import re
import os
from mcp_operator.engine.interfaces import BaseAuditor

class DesignAuditor(BaseAuditor):
    """[사용자] 아키텍처 설계와 UI 구성의 무결성을 검증하는 감사관입니다."""

    def __init__(self, logger=None):
        super().__init__(logger)

    def audit(self, file_path: str, content: str = "") -> list[str]:
        results = []
        
        # 1. 아키텍처 명세 검사 (D-1)
        if file_path.endswith("_ARCHITECT.md"):
            required_sections = ["Equation", "Fences", "Core Strategy"]
            for section in required_sections:
                if section not in content:
                    results.append(f" FAIL: [D-1] ARCHITECT 문서에 필수 섹션 '{section}'이(가) 누락되었습니다.")

        # 2. 인터페이스 우선 원칙 (D-4)
        if "Interface" not in content and "API" not in content and "Props" not in content:
            results.append(" WARNING: [D-4] 인터페이스 정의가 명확하지 않습니다. API 또는 Props 명세를 권장합니다.")

        # 3. 디자인 토큰 준수 여부 (D-2) - 간단한 키워드 체크
        tokens = ["Color", "Spacing", "Typography", "Token"]
        if not any(token in content for token in tokens):
             results.append(" WARNING: [D-2] 디자인 토큰 사용이 감지되지 않았습니다. 스타일의 방정식을 확인하십시오.")

        return results
