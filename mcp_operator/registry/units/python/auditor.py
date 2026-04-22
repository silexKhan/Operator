import ast
import os

class PythonAuditor:
    """Python 소스 코드의 물리적 무결성을 검증하는 전문 유닛입니다.
    
    단순 텍스트 매칭이 아닌 AST(Abstract Syntax Tree) 분석을 통해 
    AI의 '키워드 기만'을 방지하고 실제 구현 여부를 증명합니다.
    """
    def __init__(self, logger=None, circuit_manager=None):
        self.logger = logger

    def audit(self, file_path: str, content: str) -> list[str]:
        results = []
        
        # MISSION_PIPELINE 호출 시에는 공통 로직이 아니므로 스킵
        if file_path == "MISSION_PIPELINE" or not content:
            return results

        try:
            # 1. AST 파싱을 통한 구문 무결성 확인
            tree = ast.parse(content)
            
            # 2. 물리적 선언 존재 확인 (주석 기만 방지)
            # 함수 정의(FunctionDef), 클래스 정의(ClassDef), 비동기 함수(AsyncFunctionDef)를 모두 체크
            nodes = [n for n in ast.walk(tree) if isinstance(n, (ast.FunctionDef, ast.ClassDef, ast.AsyncFunctionDef))]
            
            if not nodes:
                results.append(" ❌ [PYTHON PHYSICAL FAIL] 실제 Python 선언문(def/class)이 발견되지 않았습니다. 주석이나 문자열만으로는 구현으로 인정되지 않습니다. ")
                return results

            # 3. 타입 힌트(Type Hints) 및 명세 준수 정밀 검사
            for node in nodes:
                if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    # 인자 타입 힌트 확인
                    for arg in node.args.args:
                        if arg.arg != "self" and not arg.annotation:
                            results.append(f" ⚠️ [TYPE FAIL] 함수 '{node.name}'의 인자 '{arg.arg}'에 타입 힌트가 누락되었습니다. ")
                    
                    # 리턴 타입 힌트 확인
                    if not node.returns:
                        results.append(f" ⚠️ [TYPE FAIL] 함수 '{node.name}'에 리턴 타입 힌트가 누락되었습니다. (-> Any 라도 명시하십시오) ")

            # 4. Docstring 존재 여부 확인
            for node in nodes:
                if ast.get_docstring(node) is None:
                    results.append(f" 📝 [STYLE FAIL] '{node.name}'의 Docstring이 누락되었습니다. 명확한 설명을 추가하십시오. ")

        except SyntaxError as se:
            results.append(f" 🚨 [SYNTAX ERROR] Python 문법 오류가 발견되었습니다 (Line {se.lineno}): {se.msg}")
        except Exception as e:
            results.append(f" 🚨 [AUDIT ERROR] Python 분석 중 예외 발생: {str(e)}")
            
        return results
