#
#  sentinel.py - Physical Action Enforcement Unit (Auto-pilot Sentinel)
#

import os
import shutil
import datetime
from typing import Dict, List, Any, Optional
from mcp_operator.engine.logger import OperatorLogger
from mcp_operator.common.history import history_logger

class Sentinel:
    """
    [사용자] AI의 행동이 규약(Protocols)의 궤적을 벗어나지 않도록 
    물리적으로 구속하고 강제하는 우리의 '자동주행(Auto-pilot)' 센티널 유닛입니다. 
    """
    def __init__(self):
        self.logger = OperatorLogger("Sentinel")
        # 프로젝트 루트 경로 확보
        self.project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

    def check_clean_desk(self) -> bool:
        """
        [Protocol S-10] docs/active/ 폴더가 비어 있는지 확인합니다.
        """
        active_dir = os.path.join(self.project_root, "docs", "active")
        if not os.path.exists(active_dir):
            os.makedirs(active_dir)
            return True
            
        files = os.listdir(active_dir)
        if files:
            self.logger.log(f" ⚠️ 작업대(docs/active/)에 이전 미션의 문서가 남아있습니다. 아카이브 후 진행하십시오.", 2)
            return False
        return True

    def archive_mission(self, mission_name: str) -> bool:
        """
        [Protocol S-10] 완료된 미션 문서를 아카이브로 이동시킵니다.
        """
        active_dir = os.path.join(self.project_root, "docs", "active")
        date_str = datetime.datetime.now().strftime("%Y%m%d")
        archive_name = f"{date_str}_{mission_name.replace(' ', '_')}"
        archive_dir = os.path.join(self.project_root, "docs", "archive", archive_name)

        if not os.path.exists(active_dir) or not os.listdir(active_dir):
            self.logger.log(" ℹ️ 아카이브할 문서가 없습니다.", 1)
            return False

        try:
            os.makedirs(archive_dir, exist_ok=True)
            for item in os.listdir(active_dir):
                s = os.path.join(active_dir, item)
                d = os.path.join(archive_dir, item)
                shutil.move(s, d)
            
            self.logger.log(f" ✅ 아카이브 성공: docs/archive/{archive_name}", 1)
            return True
        except Exception as e:
            self.logger.log(f" 🚨 아카이브 중 오류 발생: {str(e)}", 2)
            return False

    def validate_action(self, circuit_name: str, action_type: str, data: Any, auditor: Any) -> Dict[str, Any]:
        """
        [사용자] 행동 실행 전 규약 준수 여부를 최종 판정합니다. 
        """
        self.logger.log(f" 🛡️ 센티널 작동 중: {circuit_name} ({action_type})", 0)
        
        report = []
        file_path = data.get("file_path", "unknown") if isinstance(data, dict) else "unknown"

        # 1. Auditor를 통한 소스 코드 정밀 감사 (데이터가 코드인 경우)
        if auditor and isinstance(data, dict) and "content" in data and "file_path" in data:
            audit_results = auditor.audit(data["file_path"], data["content"])
            for result in audit_results:
                if "FAIL" in result or "CRITICAL" in result:
                    report.append(result)
                    severity = "CRITICAL" if "CRITICAL" in result else "FAIL"
                    history_logger.log_audit(circuit_name, file_path, severity, result)

        # 2. [Harness Insight] 기술적 무결성 체크 (임시: Python AST 레벨 등)
        # TODO: 추후 Linter 연동 시 이 영역에서 하드웨어 레벨 검증 수행

        # 3. 기존 PROTOCOL_UPDATE 규격 체크
        if action_type == "PROTOCOL_UPDATE":
            rules = data if isinstance(data, list) else []
            for rule in rules:
                if not any(rule.startswith(e) for e in ["", "", "", "", "", "", "", ""]):
                    msg = f" 🚫 규격 위반: 규칙은 지정된 이모지로 시작해야 합니다. ('{rule[:10]}...')"
                    report.append(msg)
                    history_logger.log_audit(circuit_name, "protocols.json", "FAIL", msg)
                if "Protocol" not in rule:
                    msg = f" 🏷️ 명명 위반: 규칙명에 'Protocol' 키워드가 포함되어야 합니다. ('{rule[:10]}...')"
                    report.append(msg)
                    history_logger.log_audit(circuit_name, "protocols.json", "FAIL", msg)

        if report:
            self.logger.log(f" 🚨 센티널 차단 작동: {len(report)}건의 위반 발견", 2)
            # [Harness Insight] AI에게 줄 구체적인 수정 가이드(Self-Correction) 생성
            correction_guide = "\n".join([f"- {r}" for r in report])
            return {
                "approved": False,
                "reason": "규약(Protocols) 위반으로 인해 실행을 차단했습니다. 아래 가이드에 따라 수정 후 재시도하십시오.",
                "violations": report,
                "correction_guide": correction_guide,
                "should_commit": False
            }

        # [Harness Insight] 무결성 100% 통과 시 자동 커밋 승인 플래그 전송
        self.logger.log(f" ✅ 센티널 통과: 무결성 검증 완료. 자동 커밋을 승인합니다.", 1)
        return {
            "approved": True,
            "should_commit": True,
            "commit_message": f"feat({circuit_name}): {action_type} for {file_path} (Auto-pilot Verified)"
        }
