#
#  auditor.py - AST-based Python & MCP Code Auditor
#

import ast
import os
from typing import List, Optional

class ASTAuditor(ast.NodeVisitor):
    """
    [사용자] 파이썬 코드를 구조적으로 분석하여 규약 준수 여부를 판정하는 AST 감사기입니다.
    """
    def __init__(self, file_path: str):
        self.file_path = file_path
        self.violations = []

    def visit_FunctionDef(self, node: ast.FunctionDef):
        # 1. Strict Type Hinting (Protocol P-1)
        if node.returns is None:
            self.violations.append(f" FAIL: Protocol P-1 (Strict Type Hinting) - 함수 '{node.name}'의 반환 타입을 명시하십시오.")

        # 3. Async/Await (Protocol P-3)
        if "/core/" in self.file_path and not isinstance(node, ast.AsyncFunctionDef):
            self.violations.append(f" WARNING: Protocol P-3 (Async IO) - 코어 로직 함수 '{node.name}'은 비동기(async def) 사용을 권장합니다.")

        # 5. Docstring Mandatory (Protocol P-5)
        docstring = ast.get_docstring(node)
        if not docstring:
            self.violations.append(f" Protocol P-5 (Standard Docstrings) - 함수 '{node.name}'에 Docstring 작성을 권장합니다.")
        
        self.generic_visit(node)

    def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef):
        # Async 함수도 동일한 규칙 적용
        self.visit_FunctionDef(node)

    def visit_ClassDef(self, node: ast.ClassDef):
        # 2. Pydantic Usage (Protocol P-2)
        if ("/shared/" in self.file_path or "/models/" in self.file_path):
            has_pydantic = any(isinstance(base, ast.Name) and base.id == "BaseModel" for base in node.bases)
            if not has_pydantic:
                self.violations.append(f" FAIL: Protocol P-2 (Pydantic Usage) - 클래스 '{node.name}'은 Pydantic BaseModel을 사용해야 합니다.")

        # 5. Docstring Mandatory (Protocol P-5)
        docstring = ast.get_docstring(node)
        if not docstring:
            self.violations.append(f" Protocol P-5 (Standard Docstrings) - 클래스 '{node.name}'에 Docstring 작성을 권장합니다.")

        self.generic_visit(node)

    def visit_Name(self, node: ast.Name):
        # 4. Naming Convention (Protocol P-4)
        bad_names = ["vc", "nav", "topVC", "vc_controller"]
        if node.id in bad_names:
            self.violations.append(f" FAIL: Protocol P-4 (Clean Naming) - 축약어 '{node.id}' 대신 풀네임을 사용하십시오.")
        
        self.generic_visit(node)

    def visit_Call(self, node: ast.Call):
        # S-1. Security Guard (위험 함수 탐지)
        if isinstance(node.func, ast.Name):
            forbidden = ["eval", "exec", "os.system"]
            if node.func.id in forbidden:
                self.violations.append(f" CRITICAL: Protocol S-1 (Security Guard) - 위험한 함수 호출 '{node.func.id}()'이 감지되어 차단되었습니다.")
        elif isinstance(node.func, ast.Attribute):
            if isinstance(node.func.value, ast.Name) and node.func.value.id == "os" and node.func.attr == "system":
                self.violations.append(" CRITICAL: Protocol S-1 (Security Guard) - 위험한 호출 'os.system()'이 감지되어 차단되었습니다.")
        
        self.generic_visit(node)

class PythonAuditor:
    def __init__(self, logger=None):
        self.logger = logger

    def log(self, msg, level=1):
        if self.logger:
            self.logger.log(msg, level)

    def audit(self, file_path: str, content: str) -> List[str]:
        self.log(f"AST 정밀 감사 시작 - 파일: {os.path.basename(file_path)}", 1)
        
        try:
            tree = ast.parse(content)
            visitor = ASTAuditor(file_path)
            visitor.visit(tree)
            
            # Mechanical Integrity (Global Protocol 0-1) - 이건 텍스트로 체크
            if "..." in content or "중략" in content:
                visitor.violations.append(" FAIL: Protocol 0-1 (Mechanical Integrity) - 코드 내에 '...' 또는 '중략'을 사용하지 마십시오.")
                
            for violation in visitor.violations:
                level = 2 if "FAIL" in violation or "CRITICAL" in violation else 1
                self.log(violation, level)
                
            return visitor.violations
            
        except SyntaxError as e:
            self.log(f" 문법 오류 발견: {e}", 2)
            return [f" CRITICAL: Syntax Error - {e}"]
        except Exception as e:
            self.log(f" 감사 중 오류 발생: {e}", 2)
            return [f" ERROR: Audit Failure - {e}"]
