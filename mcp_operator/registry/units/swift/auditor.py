#
#  auditor.py - Recursive Swift Code Auditor
#

import re
import os
from mcp_operator.engine.interfaces import BaseAuditor

class SwiftAuditor(BaseAuditor):
    def __init__(self, logger=None, circuit_manager=None):
        super().__init__(logger)
        self.circuit_manager = circuit_manager

    def _get_protocols_for_path(self, file_path: str):
        """
        파일 경로를 기반으로 회선(Circuit)이 정의한 프로토콜을 동적으로 가져옵니다. 
        """
        if self.circuit_manager:
            # 활성화된 회선이 있다면 해당 회선의 프로토콜을 우선적으로 가져옵니다. 
            # 이를 통해 웹에서 신규 생성된 어떤 회선도 즉각적인 규약 검증이 가능합니다.
            active = self.circuit_manager.get_active_circuit()
            if active:
                return active.get_protocols()
        
        # fallback: 기본 공통 Swift 프로토콜을 사용합니다.
        from mcp_operator.registry.units.swift.protocols import SwiftProtocols
        return SwiftProtocols

    def audit(self, file_path: str, content: str) -> list[str]:
        results = []
        is_view_controller = "ViewController" in file_path
        is_view_model = "ViewModel" in file_path
        
        # 1. 적합한 프로토콜 클래스 로드 (Recursive Inheritance)
        protocol_class = self._get_protocols_for_path(file_path)
        all_rules = protocol_class.get_rules()
        
        self.log(f"Swift 전문 유닛 감사 시작 - 파일: {os.path.basename(file_path)}", 1)
        self.log(f"로드된 유닛 프로토콜 계층: {protocol_class.__name__} (총 규칙: {len(all_rules)}개)", 1)

        # 2. Protocol S-5: Combine Naming Convention Check
        subject_pattern = r"(let|var)\s+\w+Subject\s*[:=]\s*(PassthroughSubject|CurrentValueSubject)"
        if re.search(subject_pattern, content):
            results.append(" FAIL: Protocol S-5 (Combine Naming) - 'Subject' 접미사가 포함된 변수가 발견되었습니다. ")

        # 3. Protocol S-1: Dumb-View Integrity Check (ViewController 전용)
        if is_view_controller:
            logic_keywords = len(re.findall(r"\b(if|switch|guard)\b", content))
            if logic_keywords > 15:
                results.append(f" WARNING: Protocol S-1 (Strict MVVM) - {logic_keywords}개의 조건문이 발견되었습니다. Dumb View 원칙을 확인하십시오.")
            
            if "!" in content and "IBOutlet" not in content:
                results.append(" FAIL: Protocol S-4 (No Forced Unwrapping) - 강제 언래핑('!') 사용이 발견되었습니다. ")

        # 4. Protocol S-2: Business Specification Check (ViewModel 전용)
        if is_view_model:
            has_input = "struct Input" in content
            has_output = "struct Output" in content
            has_transform = "func transform" in content
            
            if not (has_input and has_output and has_transform):
                results.append(" FAIL: Protocol S-2 (Business Specification) - Input/Output 구조체 또는 transform() 메서드가 누락되었습니다. ")
            else:
                results.append(" [Dependency Reminder] Output 수정 시 ViewController 바인딩 코드 전수 업데이트 의무 준수 확인.")

        # 5. Protocol 0-1: Mechanical Integrity (Global Protocol 0-1)
        if "..." in content or "중략" in content:
            results.append(" FAIL: Protocol 0-1 (Mechanical Integrity) - 코드 내에 '...' 또는 '중략'을 사용하지 마십시오. 완전한 리터럴 텍스트가 필요합니다. ")

        # 6. Protocol S-3: Safety-First (fatalError 금지)
        if "fatalError" in content:
            results.append(" FAIL: Protocol S-3 (Safety-First) - fatalError() 사용이 금지됩니다. 누락 시 유휴 상태를 유지하십시오. ")

        return results
