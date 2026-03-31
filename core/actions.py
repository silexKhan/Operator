#
#  actions.py - Operator Core Action Implementations 📞⚡️
#

import os
import mcp.types as types
from circuits.manager import CircuitManager
from core.logger import OperatorLogger

class CoreActions:
    """
    [대장님 🎯] 오퍼레이터 시스템의 핵심 명령을 수행하며, 모든 응답은 MCP 규격(TextContent)을 준수합니다. 🛡️⚡️
    """
    def __init__(self, manager: CircuitManager, logger: OperatorLogger):
        self.manager = manager
        self.logger = logger

    def get_operator_status(self) -> list[types.TextContent]:
        """[대장님 🎯] 시스템의 생동감 넘치는 상태를 보고합니다."""
        active = self.manager.get_active_circuit()
        active_name = active.get_name() if active else "None"
        
        res = (
            f"🚀 Operator Status: Online\n"
            f"📍 Path: {self.manager.current_path}\n"
            f"🏢 Active Circuit: {active_name}\n"
            f"📋 Total Registered: {list(self.manager.circuits.keys())}\n\n"
            f"🔍 Discovery Log:\n" + "\n".join(self.manager.discovery_log[-5:])
        )
        # [대장님 🎯] 문자열이 아닌 TextContent 객체 리스트로 반환합니다! 💎
        return [types.TextContent(type="text", text=res)]

    def set_active_circuit(self, name: str) -> list[types.TextContent]:
        """[대장님 🎯] 특정 회선에 정식으로 연결을 시도합니다."""
        if not name:
            return [types.TextContent(type="text", text="⚠️ 연결할 회선 이름을 입력해 주세요.")]
            
        if self.manager.set_active_circuit(name):
            res = f"✅ {name} 회선이 성공적으로 연결되었습니다!\n\n" + self.manager.get_circuit_context_card(self.manager.circuits[name.lower()])
            return [types.TextContent(type="text", text=res)]
        else:
            return [types.TextContent(type="text", text=f"❌ '{name}' 회선을 찾을 수 없습니다. 등록된 회선을 확인해 주세요.")]

    def sync_operator_path(self, path: str) -> list[types.TextContent]:
        """[대장님 🎯] 작업 경로를 동기화하고 주변 회선을 자동 탐색합니다."""
        if not os.path.exists(path):
            return [types.TextContent(type="text", text=f"❌ 존재하지 않는 경로입니다: {path}")]
            
        self.manager.sync_path(path)
        res = (
            f"📡 경로 동기화 완료: {path}\n"
            f"🔎 새로운 회선들을 감지했습니다: {list(self.manager.circuits.keys())}"
        )
        return [types.TextContent(type="text", text=res)]
