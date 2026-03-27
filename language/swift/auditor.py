#
#  auditor.py - Recursive Swift Code Auditor
#

import re
import os
import importlib.util

class SwiftAuditor:
    def __init__(self, logger=None):
        self.logger = logger

    def log(self, msg, level=1):
        if self.logger:
            self.logger.log(msg, level)

    def _get_axioms_for_path(self, file_path: str):
        """
        파일 경로를 분석하여 가장 적합한 Axioms 클래스를 재귀적으로 로드합니다.
        """
        # 프로젝트 루트 경로 탐색 (실제 환경에 맞춰 조정 필요)
        base_path = "/Users/silex/workspace/private/MCP/tenants/projects/golfzon"
        
        target_axioms = None
        
        if "gdr" in file_path.lower():
            module_path = f"{base_path}/gdr/axioms.py"
        elif "auth" in file_path.lower():
            module_path = f"{base_path}/libraries/auth/axioms.py"
        elif "nasmo" in file_path.lower():
            module_path = f"{base_path}/libraries/nasmo/axioms.py"
        elif "vision" in file_path.lower():
            module_path = f"{base_path}/libraries/vision/axioms.py"
        elif "common" in file_path.lower():
            module_path = f"{base_path}/libraries/common/axioms.py"
        else:
            from language.swift.axioms import SwiftAxioms
            return SwiftAxioms

        try:
            # 동적 모듈 로드
            spec = importlib.util.spec_from_file_location("axioms", module_path)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            return module.Axioms
        except Exception as e:
            self.log(f"공리 로드 실패 ({module_path}): {str(e)}", 2)
            from language.swift.axioms import SwiftAxioms
            return SwiftAxioms

    def audit(self, file_path: str, content: str) -> list[str]:
        results = []
        is_view_controller = "ViewController" in file_path
        is_view_model = "ViewModel" in file_path
        
        # 1. 적합한 공리 클래스 로드 (Recursive Inheritance)
        axiom_class = self._get_axioms_for_path(file_path)
        all_rules = axiom_class.get_rules()
        
        self.log(f"Swift 감사 시작 - 파일: {os.path.basename(file_path)}", 1)
        self.log(f"로드된 공리 계층: {axiom_class.__name__} (총 규칙: {len(all_rules)}개)", 1)

        # 2. Combine Naming Convention Check
        subject_pattern = r"(let|var)\s+\w+Subject\s*[:=]\s*(PassthroughSubject|CurrentValueSubject)"
        if re.search(subject_pattern, content):
            results.append("❌ FAIL: Axiom (Standardized Combine Naming) - 'Subject' 접미사가 포함된 변수가 발견되었습니다. ⛓️")

        # 3. Dumb-View Integrity Check (ViewController 전용)
        if is_view_controller:
            logic_keywords = len(re.findall(r"\b(if|switch|guard)\b", content))
            if logic_keywords > 15:
                results.append(f"⚠️ WARNING: Axiom (Strict MVVM) - {logic_keywords}개의 조건문이 발견되었습니다. Dumb View 원칙을 확인하십시오.")
            
            if "!" in content and "IBOutlet" not in content:
                results.append("❌ FAIL: Axiom (No Forced Unwrapping) - 강제 언래핑('!') 사용이 발견되었습니다. 🛡️")

        # 4. Business Specification Check (ViewModel 전용)
        if is_view_model:
            has_input = "struct Input" in content
            has_output = "struct Output" in content
            has_transform = "func transform" in content
            
            if not (has_input and has_output and has_transform):
                results.append("❌ FAIL: Axiom (Business Specification) - Input/Output 구조체 또는 transform() 메서드가 누락되었습니다. 🏗️")
            else:
                results.append("💡 [Dependency Reminder] Output 수정 시 ViewController 바인딩 코드 전수 업데이트 의무 준수 확인.")

        # 5. Mechanical Integrity (Global Axiom 5)
        if "..." in content or "중략" in content:
            results.append("❌ FAIL: Axiom 5 (Mechanical Integrity) - 코드 내에 '...' 또는 '중략'을 사용하지 마십시오. 완전한 리터럴 텍스트가 필요합니다. 🛠️🛑")

        # 6. Safety-First (fatalError 금지)
        if "fatalError" in content:
            results.append("❌ FAIL: Axiom (Safety-First) - fatalError() 사용이 금지됩니다. 누락 시 유휴 상태를 유지하십시오. 🚑")

        return results
