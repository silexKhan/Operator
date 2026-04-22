#
#  auditor.py - Recursive Swift Code Auditor (Strict Implementation)
#

import re
import os
from mcp_operator.engine.interfaces import BaseUnit

class SwiftAuditor(BaseUnit):
    """
    [Swift Specialist] Swift 언어의 결벽증적 타입 안전성과 Protocol 기반 설계를 검증하는 유닛입니다.
    """
    def __init__(self, logger=None, manager=None):
        # BaseUnit은 BaseComponent와 BaseAuditor를 모두 초기화합니다.
        super().__init__(logger, manager)

    def get_name(self) -> str:
        return "swift"

    def get_path(self) -> str:
        return os.path.dirname(os.path.abspath(__file__))

    def _get_protocols_for_path(self, file_path: str):
        """
        파일 경로를 기반으로 유닛 고유의 프로토콜 또는 회선 프로토콜을 로드합니다.
        """
        # 기본적으로 유닛의 protocols.json 규칙을 사용
        from mcp_operator.registry.units.swift.protocols import SwiftProtocols
        return SwiftProtocols

    def audit(self, file_path: str, content: str) -> list[str]:
        results = []
        if not file_path.endswith(".swift"):
            return results

        is_view_controller = "ViewController" in file_path
        is_view_model = "ViewModel" in file_path
        
        # 1. 프로토콜 규칙 로드
        protocol_class = self._get_protocols_for_path(file_path)
        all_rules = protocol_class.get_rules()
        
        self.log(f"Swift 전문 유닛 감사 시작 - 파일: {os.path.basename(file_path)}", 1)

        # 2. SWIFT-V1: Strict Typing & No Forced Unwrapping
        # !IBOutlet 제외한 강제 언래핑 금지
        if "!" in content and "@IBOutlet" not in content:
            # 주석 처리된 부분 제외 정교한 검사
            clean_content = re.sub(r"//.*", "", content)
            clean_content = re.sub(r"/\*.*?\*/", "", clean_content, flags=re.DOTALL)
            if "!" in clean_content:
                results.append(" [CRITICAL] SWIFT-V1 (Strict Typing): 강제 언래핑('!')이 발견되었습니다. Optional Binding(if let, guard let)을 사용하십시오. ")

        # 3. SWIFT-V2: Protocol-Oriented Implementation (ViewModel 전용)
        if is_view_model:
            has_input = "struct Input" in content
            has_output = "struct Output" in content
            has_transform = "func transform" in content
            
            if not (has_input and has_output and has_transform):
                results.append(" [ERROR] SWIFT-V2 (Strict MVVM): Input/Output 구조체 또는 transform() 메서드가 누락되었습니다. ")

        # 4. SWIFT-V3: Memory Safety (Circular Reference)
        if "delegate =" in content or "self." in content:
            # closure 내부에서 self 사용 시 weak self 체크 (단순화된 정규식)
            if "{" in content and "self." in content and "[weak self]" not in content:
                # 클로저가 의심되는 구문에서만 경고
                if re.search(r"\{.*self\.", content, re.DOTALL):
                    results.append(" [ERROR] SWIFT-V3 (Memory Safety): 클로저 내 self 참조 시 [weak self] 누락이 의심됩니다. ")

        # 5. SWIFT-V4: Modern Async/Await
        if "completion:" in content or "completionHandler:" in content:
            results.append(" [WARNING] SWIFT-V4 (Modern Swift): Callback 방식 대신 async/await 도입을 검토하십시오. ")

        # 6. Global Protocol 0-1: No Omissions
        if "..." in content or "중략" in content:
            results.append(" [CRITICAL] Protocol 0-1: 코드 내 '...' 또는 '중략' 사용은 절대 금지됩니다. ")

        return results
