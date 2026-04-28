import re
import os
from typing import List

class PlanningAuditor:
    """기획 문서의 구조적 정합성을 검증하는 유닛입니다.
    
    1. 사용자 워크플로우 명시 여부
    2. 목차(TOC)와 상세 기획 헤더의 일치성
    3. 문서의 계층적 무결성
    """
    def __init__(self, logger=None, manager=None):
        self.logger = logger
        self.unit_path = os.path.dirname(os.path.abspath(__file__))
        self.guide_path = os.path.join(self.unit_path, "example", "architecture.md")

    def log(self, message: str, level: int = 0):
        if self.logger:
            self.logger.log(message, level)

    def audit(self, file_path: str, content: str) -> List[str]:
        results = []
        if not file_path.endswith(".md") or not content:
            return results

        self.log(f"Planning 유닛 감사 시작 - 파일: {os.path.basename(file_path)}", 1)

        # 1. 필수 섹션 존재 확인 (Workflow)
        if "# 1. User Workflow" not in content:
            results.append(" 🏗️ [PLAN FAIL] 필수 섹션 '# 1. User Workflow'가 누락되었습니다. 사용자 여정을 먼저 정의하십시오. ")

        # 2. 목차(TOC) 추출 및 검증
        toc_match = re.search(r"# 2\. Table of Contents \(TOC\)\n(.*?)(?=\n#|$)", content, re.DOTALL)
        if not toc_match:
            results.append(" 🏗️ [PLAN FAIL] 필수 섹션 '# 2. Table of Contents (TOC)'가 누락되었습니다. ")
        else:
            # 목차 리스트 항목 추출 (예: - 항목명)
            toc_items = re.findall(r"- (.*)", toc_match.group(1))
            if not toc_items:
                results.append(" 🏗️ [PLAN FAIL] TOC 내에 정의된 기획 항목이 없습니다. ")
            else:
                # 3. 상세 기획 헤더(##)와 TOC 대조
                detail_headers = re.findall(r"^## (.*)", content, re.MULTILINE)
                for item in toc_items:
                    item_clean = item.strip()
                    if item_clean not in detail_headers:
                        results.append(f" 🏗️ [PLAN FAIL] TOC 항목 '{item_clean}'에 대한 상세 기획(## {item_clean})이 발견되지 않았습니다. ")

        # 4. 코드 생략 금지 (P-0)
        if "..." in content or "중략" in content:
            results.append(" 🚫 [GLOBAL FAIL] 기획 문서 내에 '...'이나 '중략'을 사용하지 말고 모든 정책을 명시하십시오. ")

        return results
