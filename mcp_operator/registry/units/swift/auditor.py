#
#  auditor.py - Recursive Swift Code Auditor (Strict Implementation)
#

import re
import os
from typing import List, Optional

class SwiftAuditor:
    """
    [Swift Specialist] Swift 언어의 결벽증적 타입 안전성과 Protocol 기반 설계를 검증하는 유닛입니다.
    자신의 하위 example/ 가이드라인을 물리적으로 참조합니다.
    """
    def __init__(self, logger=None, circuit_manager=None, manager=None):
        self.logger = logger
        self.manager = circuit_manager or manager
        self.unit_path = os.path.dirname(os.path.abspath(__file__))
        self.guide_path = os.path.join(self.unit_path, "example", "architecture.md")

    def _get_required_patterns(self) -> List[str]:
        """가이드라인 문서에서 핵심 아키텍처 키워드를 추출합니다."""
        patterns = []
        if os.path.exists(self.guide_path):
            try:
                with open(self.guide_path, "r", encoding="utf-8") as f:
                    content = f.read()
                    # 가이드라인의 핵심 키워드 추출
                    found = re.findall(r"\*\*(MVVM|Input|Output|Protocol|createInput|Dummy View|Combine)\*\*", content)
                    patterns = list(set(found))
            except: pass
        return patterns

    def log(self, message: str, level: int = 0):
        if self.logger:
            self.logger.log(message, level)

    def audit(self, file_path: str, content: str) -> List[str]:
        results = []
        if not file_path.endswith(".swift") or not content:
            return results

        self.log(f"Swift 전문 유닛 감사 시작 - 파일: {os.path.basename(file_path)}", 1)
        
        required_patterns = self._get_required_patterns()
        is_view_controller = "ViewController" in file_path
        is_view_model = "ViewModel" in file_path

        # 1. 아키텍처 및 관심사 분리 체크 (createInput)
        if is_view_controller:
            if "createInput" in required_patterns and "func createInput" not in content:
                results.append(" 🏗️ [ARCH FAIL] Dummy View 원칙에 따른 'createInput()' 메서드가 누락되었습니다. 관심사를 분리하십시오. ")
        
        if is_view_model:
            if "Input" in required_patterns and "struct Input" not in content:
                results.append(" 🏗️ [ARCH FAIL] ViewModel 내 'struct Input' 정의가 누락되었습니다. ")
            if "Output" in required_patterns and "struct Output" not in content:
                results.append(" 🏗️ [ARCH FAIL] ViewModel 내 'struct Output' 정의가 누락되었습니다. ")

        # 2. Combine 절제 사용 체크 (Conservative Combine)
        if "Combine" in required_patterns or "sink" in content:
            # 복잡한 체이닝 여부를 단순하게 체크 (점 연산자가 한 줄에 너무 많은지 등)
            lines = content.split('\n')
            for i, line in enumerate(lines):
                if line.count('.') > 4 and "sink" not in line:
                    results.append(f" 🧩 [STYLE FAIL] Line {i+1}: 과도한 Combine 연산자 체이닝이 의심됩니다. 가독성을 위해 분리하십시오. ")

        # 3. 강제 언래핑 금지 (Strict Typing)
        clean_content = re.sub(r"//.*", "", content)
        clean_content = re.sub(r"/\*.*?\*/", "", clean_content, flags=re.DOTALL)
        if "!" in clean_content and "@IBOutlet" not in clean_content and "as!" not in clean_content:
            results.append(" [CRITICAL] SWIFT-V1: 강제 언래핑('!') 금지. Optional Binding을 사용하십시오. ")

        # 4. 메모리 안전성
        if "{" in content and "self." in content and "[weak self]" not in content:
            if re.search(r"\{.*self\.", content, re.DOTALL):
                results.append(" [ERROR] SWIFT-V3: 클로저 내 self 참조 시 [weak self] 누락이 의심됩니다. ")

        return results
