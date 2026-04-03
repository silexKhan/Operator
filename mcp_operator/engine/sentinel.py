#
#  sentinel.py - Physical Action Enforcement Unit (Auto-pilot Sentinel)
#

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

    def validate_action(self, circuit_name: str, action_type: str, data: Any, auditor: Any) -> Dict[str, Any]:
        """
        [사용자] 행동 실행 전 규약 준수 여부를 최종 판정합니다. 
        """
        self.logger.log(f" 센티널 작동 중: {circuit_name} ({action_type})", 0)
        
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

        # 2. 기존 PROTOCOL_UPDATE 규격 체크
        if action_type == "PROTOCOL_UPDATE":
            rules = data if isinstance(data, list) else []
            for rule in rules:
                if not any(rule.startswith(e) for e in ["", "", "", "", "", "", "", ""]):
                    msg = f" 규격 위반: 규칙은 지정된 이모지로 시작해야 합니다. ('{rule[:10]}...')"
                    report.append(msg)
                    history_logger.log_audit(circuit_name, "protocols.json", "FAIL", msg)
                if "Protocol" not in rule:
                    msg = f" 명명 위반: 규칙명에 'Protocol' 키워드가 포함되어야 합니다. ('{rule[:10]}...')"
                    report.append(msg)
                    history_logger.log_audit(circuit_name, "protocols.json", "FAIL", msg)

        if report:
            self.logger.log(f" 센티널 차단 작동: {len(report)}건의 위반 발견", 2)
            return {
                "approved": False,
                "reason": "규약(Protocols) 또는 보안(Security) 위반으로 인해 센티널이 작동하여 실행을 차단했습니다. ",
                "violations": report
            }

        return {"approved": True}
