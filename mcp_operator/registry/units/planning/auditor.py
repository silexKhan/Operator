#
#  auditor.py - Universal Planning Auditor
#

import re
import os
from mcp_operator.engine.interfaces import BaseAuditor

class PlanningAuditor(BaseAuditor):
    """[사용자] 기획 문서의 무결성과 요구사항 정합성을 검증하는 감사관입니다."""

    def __init__(self, logger=None):
        super().__init__(logger)

    def audit(self, file_path: str, content: str = "") -> list[str]:
        results = []
        
        # 1. PRD 필수 섹션 검사 (P-1)
        required_headers = ["목적", "배경", "상세 기능", "인수 조건", "예외 케이스"]
        for header in required_headers:
            if header not in content:
                results.append(f" FAIL: [P-1] 필수 섹션 '{header}'이(가) 누락되었습니다.")

        # 2. 용어 통일성 검사 (P-3)
        if "유저" in content:
            results.append(" WARNING: [P-3] '유저' 대신 '사용자'라는 표준 용어를 사용하십시오.")

        # 3. 글로벌 규약 0-1 (No Omission) 검사 (P-5)
        if "..." in content or "중략" in content:
            results.append(" FAIL: [P-5] 문서 내에 '...' 또는 '중략'을 사용하지 마십시오. 완전한 명세가 필요합니다.")

        # 4. 모호성 검사 (P-4)
        vague_terms = ["나중에 추가", "TBD", "미정"]
        for term in vague_terms:
            if term in content:
                results.append(f" WARNING: [P-4] 모호한 표현 '{term}'이 발견되었습니다. 구체적인 명세가 권장됩니다.")

        return results
