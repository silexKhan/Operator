from mcp_operator.registry.units.planning.auditor import PlanningAuditor

def test_planning_audit():
    auditor = PlanningAuditor()
    
    # 1. FAIL 케이스: 목차(TOC)와 상세 섹션이 불일치함
    bad_plan = """
# 영화표 예매 시스템

# 1. User Workflow
목록보기 -> 선택 -> 결제

# 2. Table of Contents (TOC)
- 영화 목록 페이지
- 좌석 선택 페이지

# 3. Detailed Specifications
## 영화 목록 페이지
상세 내용...
(좌석 선택 페이지 누락)
"""
    print("[TEST 1] 불일치 기획서 테스트")
    results = auditor.audit("bad_plan.md", bad_plan)
    for r in results:
        print(r)

    print("\n" + "="*50 + "\n")

    # 2. PASS 케이스: 워크플로우와 목차, 상세 헤더가 모두 정렬됨
    good_plan = """
# 영화표 예매 시스템

# 1. User Workflow
목록보기 -> 선택 -> 결제

# 2. Table of Contents (TOC)
- 영화 목록 페이지
- 좌석 선택 페이지

# 3. Detailed Specifications
## 영화 목록 페이지
여기는 영화 목록에 대한 상세 기획입니다.

## 좌석 선택 페이지
여기는 좌석 선택에 대한 상세 기획입니다.
"""
    print("[TEST 2] 정합성 일치 기획서 테스트")
    results = auditor.audit("good_plan.md", good_plan)
    if not results:
        print(" ✅ 기획서 구조 검증 통과!")
    for r in results:
        print(r)

if __name__ == "__main__":
    test_planning_audit()
