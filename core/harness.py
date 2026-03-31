#
#  harness.py - Physical Action Enforcement Unit 📞⚡️
#

from typing import Dict, List, Any, Optional
from core.logger import OperatorLogger

class ActionHarness:
    """
    [대장님 🎯] AI의 행동이 규약(Protocols)의 궤적을 벗어나지 않도록 
    물리적으로 구속하고 강제하는 하네스 유닛입니다. 🛡️⚡️
    """
    def __init__(self):
        self.logger = OperatorLogger("ActionHarness")

    def validate_action(self, circuit_name: str, action_type: str, data: Any, auditor: Any) -> Dict[str, Any]:
        """
        [대장님 🎯] 행동 실행 전 규약 준수 여부를 최종 판정합니다. ⚖️
        """
        self.logger.log(f"🕵️‍♂️ 하네스 작동 중: {circuit_name} ({action_type})", 0)
        
        if not auditor:
            return {"approved": True}

        report = []
        if action_type == "PROTOCOL_UPDATE":
            rules = data if isinstance(data, list) else []
            for rule in rules:
                if not any(rule.startswith(e) for e in ["🛡️", "⚖️", "⚡️", "🧩", "🛠️", "💡", "📱", "🌐"]):
                    report.append(f"❌ 규격 위반: 규칙은 지정된 이모지로 시작해야 합니다. ('{rule[:10]}...')")
                if "Protocol" not in rule:
                    report.append(f"❌ 명명 위반: 규칙명에 'Protocol' 키워드가 포함되어야 합니다. ('{rule[:10]}...')")

        if report:
            return {
                "approved": False,
                "reason": "규약(Protocols) 위반으로 인해 하네스가 작동하여 실행을 차단했습니다. 🛡️⚡️",
                "violations": report
            }

        return {"approved": True}
