import sys
import os

# MCP 경로 추가
sys.path.append(os.path.join(os.getcwd(), "workspace/private/MCP"))

from units.python.auditor import PythonAuditor
from core.sentinel import Sentinel

def test_ast_auditor_security():
    print("\n--- [TEST 1] AST Auditor Security Guard Test ---")
    auditor = PythonAuditor()
    sentinel = Sentinel()

    # 1. 위험한 코드 시나리오 (os.system 호출 포함)
    dangerous_code = """
def hack_system():
    import os
    os.system('rm -rf /')  # 이 코드는 차단되어야 함
    return True
"""
    data = {
        "file_path": "test_script.py",
        "content": dangerous_code
    }
    
    result = sentinel.validate_action("test_circuit", "CODE_EXECUTION", data, auditor)
    
    print(f"Result Approved: {result['approved']}")
    if not result['approved']:
        print(f"Reason: {result['reason']}")
        for v in result['violations']:
            print(f" - {v}")
    
    assert result['approved'] == False
    assert any("CRITICAL" in v for v in result['violations'])
    print(">>> [SUCCESS] 위험 코드 차단 확인 완료!")

def test_ast_auditor_protocols():
    print("\n--- [TEST 2] AST Auditor Protocol P-1 (Type Hint) Test ---")
    auditor = PythonAuditor()
    sentinel = Sentinel()

    # 2. 타입 힌트 누락 시나리오
    bad_protocol_code = """
def process_data(data):  # -> 반환 타입이 없음
    \"\"\"데이터를 처리합니다.\"\"\"
    return data
"""
    data = {
        "file_path": "workspace/private/MCP/core/logic.py",
        "content": bad_protocol_code
    }
    
    result = sentinel.validate_action("test_circuit", "CODE_EXECUTION", data, auditor)
    
    print(f"Result Approved: {result['approved']}")
    if not result['approved']:
        print(f"Reason: {result['reason']}")
        for v in result['violations']:
            print(f" - {v}")

    assert result['approved'] == False
    assert any("P-1" in v for v in result['violations'])
    print(">>> [SUCCESS] 규약 위반(P-1) 탐지 확인 완료!")

if __name__ == "__main__":
    try:
        test_ast_auditor_security()
        test_ast_auditor_protocols()
        print("\n[FINAL RESULT] 모든 AST 정밀 감사 테스트 통과!")
    except Exception as e:
        print(f"\n[FINAL RESULT] 테스트 실패: {e}")
        sys.exit(1)
