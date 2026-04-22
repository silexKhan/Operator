#
#  auditor.py - Autonomous Mission Pipeline Commander
#

import os
import json
from mcp_operator.common.utils import get_project_root
from mcp_operator.engine.interfaces import BaseAuditor

class SentinelAuditor(BaseAuditor):
    """자율 7단계 파이프라인을 지휘하고 무결성을 검증하는 지휘관 유닛입니다.

    단순 감사를 넘어 기획, 설계, TDD, 구현, 검증의 전 과정을 통제하며
    대장님(사용자)의 의도가 완벽히 반영되도록 파이프라인을 드라이브합니다.
    """

    def __init__(self, logger: object = None, circuit_manager: object = None) -> None:
        super().__init__(logger)
        self.circuit_manager = circuit_manager
        # 프로젝트 루트 경로 확보 (공통 유틸리티 사용)
        self.project_root: str = get_project_root()

    def audit(self, file_path: str, content: str = "") -> list[str]:
        """7단계 파이프라인 준수 여부를 감사하고 다음 단계 지침을 하달합니다."""
        results: list[str] = []
        mission_path: str = os.path.join(self.project_root, "mission.json")
        docs_active_dir: str = os.path.join(self.project_root, "docs", "active")
        
        # docs/active 폴더 보장
        os.makedirs(docs_active_dir, exist_ok=True)

        # 1. 미션 설정 여부 확인 (Step 0)
        if not os.path.exists(mission_path):
            results.append(" 🚨 [COMMANDER] 미션이 설정되지 않았습니다. 'sentinel_set_mission'으로 목적을 먼저 정의하십시오. ")
            return results

        try:
            with open(mission_path, "r", encoding="utf-8") as f:
                mission_data: dict = json.load(f)
                objective: str = mission_data.get("objective", "")
                criteria: list[str] = mission_data.get("criteria", [])
                status: str = mission_data.get("status", "IN_PROGRESS")

            # 2. [Step 1 & 2] 기획 및 설계 문서 강제 (Planning & Design Wall)
            # Sentinel은 문서가 없으면 직접 작성을 명령합니다.
            required_docs = {
                "PRD.md": {"rule": "Protocol S-3 (Planning Automation)", "desc": "기획서 (목적/흐름/예외/검증)"},
                "ADR.md": {"rule": "Protocol S-4 (Design Spec)", "desc": "기술 결정서 (Decision/Reason/Trade-off)"},
                "UI_GUIDE.md": {"rule": "Protocol S-4 (Design Spec)", "desc": "UI 가이드 (Hex/Tailwind/Spacing)"}
            }

            missing_docs = []
            for doc_name, spec in required_docs.items():
                doc_path = os.path.join(docs_active_dir, doc_name)
                if not os.path.exists(doc_path):
                    missing_docs.append(f"{doc_name} ({spec['desc']})")
            
            if missing_docs:
                results.append(f" 📑 [STEP 1-2: Documentation] 필수 문서가 누락되었습니다: {', '.join(missing_docs)}")
                results.append(f" 💡 [GUIDE] Sentinel은 자율 지휘 모드입니다. 지금 즉시 'docs/active/' 폴더에 위 문서들의 초안을 작성하십시오. ")
                return results

            # 3. [Step 3] TDD Fencing (Test Scaffolding)
            # 실제 코드를 수정하기 전에 테스트 파일이 먼저 생성되었는지 확인합니다.
            test_files = [f for f in os.listdir(self.project_root) if "test" in f.lower() or "spec" in f.lower()]
            if not test_files and status != "PASS":
                results.append(" 🧪 [STEP 3: TDD] 구현 전 테스트 스캐폴딩이 발견되지 않았습니다. (Protocol S-5)")
                results.append(" 💡 [GUIDE] 먼저 'Red Phase'로 진입하여 실패하는 테스트 코드를 작성하십시오. ")

            # 4. [Step 4-5] 구현 및 감사 (Audit)
            for criterion in criteria:
                if criterion.lower() not in content.lower() and status != "PASS":
                     results.append(f" ⚠️ [STEP 4: Dev] 미션 기준 [{criterion}] 누락 위험이 감지되었습니다. (Protocol S-1)")

            # 금지 표현 검사 (Global Protocol 0-1)
            forbidden_words: list[str] = ["." + ".." , "중" + "략", "생" + "략"]
            for word in forbidden_words:
                if word in content:
                    results.append(f" ❌ [STEP 5: Audit] 부적절한 구현({word})이 발견되었습니다. 생략 없이 모든 코드를 작성하십시오. ")

            # 5. [Step 7] Clean Desk 제안
            if status == "PASS":
                results.append(" 🧹 [STEP 7: Archive] 모든 검증이 완료되었습니다. 'docs/active/'의 문서들을 'docs/archive/'로 이동시켜 작업을 정리하십시오. ")

        except Exception as e:
            results.append(f" 🚨 [SENTINEL ERROR] 파이프라인 엔진 오류: {str(e)}")

        return results
