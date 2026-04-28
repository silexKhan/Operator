import ast
import os
import re
from typing import List, Optional

class PythonAuditor:
    """Python 소스 코드의 물리적 무결성 및 아키텍처 가이드 준수 여부를 검증하는 유닛입니다.
    
    자신의 하위 example/ 폴더의 가이드라인을 읽어와서 실제 코드와 대조합니다.
    """
    def __init__(self, logger=None, circuit_manager=None):
        self.logger = logger
        # 자신의 위치를 기준으로 유닛 경로 확보
        self.unit_path = os.path.dirname(os.path.abspath(__file__))
        self.guide_path = os.path.join(self.unit_path, "example", "architecture.md")

    def _get_required_patterns(self) -> List[str]:
        """가이드라인 문서에서 핵심 아키텍처 키워드를 추출합니다."""
        patterns = []
        if os.path.exists(self.guide_path):
            try:
                with open(self.guide_path, "r", encoding="utf-8") as f:
                    content = f.read()
                    # 가이드라인의 '계층 구조' 섹션에서 키워드 추출 (Service, Repository, Models 등)
                    found = re.findall(r"\*\*(Service|Repository|Models|BaseModel|Pydantic)\*\*", content)
                    patterns = list(set(found))
            except: pass
        return patterns

    def audit(self, file_path: str, content: str) -> List[str]:
        results = []
        if file_path == "MISSION_PIPELINE" or not content:
            return results

        try:
            tree = ast.parse(content)
            nodes = [n for n in ast.walk(tree) if isinstance(n, (ast.FunctionDef, ast.ClassDef, ast.AsyncFunctionDef))]
            
            if not nodes:
                results.append(" ❌ [PYTHON PHYSICAL FAIL] 실제 Python 선언문(def/class)이 발견되지 않았습니다.")
                return results

            # 1. 아키텍처 가이드라인 준수 여부 체크
            required_patterns = self._get_required_patterns()
            if required_patterns:
                all_names = " ".join([node.name for node in nodes if hasattr(node, "name")])
                for pattern in required_patterns:
                    # 'Models'는 BaseModel 등으로 대체될 수 있으므로 유연하게 체크
                    if pattern == "Models" or pattern == "Pydantic": continue 
                    
                    if pattern not in all_names:
                        results.append(f" 🏗️ [ARCH FAIL] 가이드라인의 '{pattern}' 패턴이 코드에서 발견되지 않았습니다. 아키텍처 설계를 확인하십시오. ")

            # 2. 타입 힌트 및 명세 준수 검사
            for node in nodes:
                if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    for arg in node.args.args:
                        if arg.arg != "self" and not arg.annotation:
                            results.append(f" ⚠️ [TYPE FAIL] 함수 '{node.name}'의 인자 '{arg.arg}'에 타입 힌트가 누락되었습니다. ")
                    if not node.returns:
                        results.append(f" ⚠️ [TYPE FAIL] 함수 '{node.name}'에 리턴 타입 힌트가 누락되었습니다. ")

            # 3. Docstring 존재 여부 확인
            for node in nodes:
                if ast.get_docstring(node) is None:
                    results.append(f" 📝 [STYLE FAIL] '{node.name}'의 Docstring이 누락되었습니다. ")

        except SyntaxError as se:
            results.append(f" 🚨 [SYNTAX ERROR] Python 문법 오류 (Line {se.lineno}): {se.msg}")
        except Exception as e:
            results.append(f" 🚨 [AUDIT ERROR] Python 분석 중 예외 발생: {str(e)}")
            
        return results
