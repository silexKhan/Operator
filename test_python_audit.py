import sys
import os

# 프로젝트 루트를 path에 추가하여 모듈 임포트 가능하게 설정
project_root = "/Users/silex/workspace/private/MCP"
sys.path.append(project_root)

from mcp_operator.registry.units.python.auditor import PythonAuditor

def run_test():
    auditor = PythonAuditor()
    print(f"--- [TEST] 가이드라인 경로: {auditor.guide_path} ---")
    print(f"--- [TEST] 추출된 패턴: {auditor._get_required_patterns()} ---\n")

    # 1. FAIL 케이스: 가이드라인 무시 (Service, Repository 단어 없음)
    bad_code = """
class UserHandler:
    def get_data(self, uid: str) -> dict:
        \"\"\"사용자 데이터를 가져옵니다.\"\"\"
        return {"id": uid, "name": "Test"}
"""
    print("[SCENARIO 1] 가이드라인 위반 코드 테스트 (No Service/Repository)")
    results = auditor.audit("test_fail.py", bad_code)
    for r in results:
        print(r)

    print("\n" + "="*50 + "\n")

    # 2. PASS 케이스: 가이드라인 준수 (Service, Repository 패턴 적용)
    good_code = """
class UserRepository:
    def find_user(self, uid: str) -> dict:
        \"\"\"DB에서 사용자를 찾습니다.\"\"\"
        return {"id": uid}

class UserService:
    def __init__(self, repo: UserRepository):
        self.repo = repo
        
    def get_user(self, uid: str) -> dict:
        \"\"\"비즈니스 로직을 처리합니다.\"\"\"
        return self.repo.find_user(uid)
"""
    print("[SCENARIO 2] 가이드라인 준수 코드 테스트 (Service & Repository)")
    results = auditor.audit("test_pass.py", good_code)
    if not any("ARCH FAIL" in r for r in results):
        print(" ✅ 아키텍처 검증 통과!")
    for r in results:
        print(r)

if __name__ == "__main__":
    run_test()
