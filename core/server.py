#
#  server.py - Autonomous Watcher Operator Server 🛡️⚡️
#

import asyncio
import os
import mcp.types as types
from mcp.server.models import InitializationOptions
from mcp.server import NotificationOptions, Server
from mcp.server.stdio import stdio_server

from circuits.manager import CircuitManager
from core.actions import CoreActions
from core.logger import OperatorLogger

class OperatorServer:
    def __init__(self):
        self.logger = OperatorLogger("MasterOperator")
        self.circuit_manager = CircuitManager()
        self.core_actions = CoreActions(self.circuit_manager, self.logger)
        self.server = Server("operator-hub")
        self._setup_handlers()
        # [대장님 🎯] 마지막으로 확인된 회선 목록을 기억합니다.
        self.last_circuit_keys = set(self.circuit_manager.circuits.keys())

    def _setup_handlers(self):
        @self.server.list_tools()
        async def handle_list_tools() -> list[types.Tool]:
            tools = [
                types.Tool(name="get_operator_status", description="상태 확인", inputSchema={"type": "object", "properties": {}}),
                types.Tool(name="set_active_circuit", description="회선 연결", inputSchema={"type": "object", "properties": {"name": {"type": "string"}}, "required": ["name"]}),
                types.Tool(name="sync_operator_path", description="경로 동기화", inputSchema={"type": "object", "properties": {"path": {"type": "string"}}, "required": ["path"]}),
                types.Tool(name="reload_operator", description="엔진 리로드 🛡️⚡️", inputSchema={"type": "object", "properties": {}})
            ]
            # 중복 방지하며 회선 도구 통합
            seen = {t.name for t in tools}
            for circuit in self.circuit_manager.circuits.values():
                for t in circuit.get_tools():
                    if t.name not in seen:
                        tools.append(t)
                        seen.add(t.name)
            return tools

        @self.server.call_tool()
        async def handle_call_tool(name: str, arguments: dict | None) -> list[types.TextContent]:
            args = arguments or {}
            if name == "get_operator_status": return self.core_actions.get_operator_status()
            elif name == "set_active_circuit": return self.core_actions.set_active_circuit(args.get("name", ""))
            elif name == "sync_operator_path": return self.core_actions.sync_operator_path(args.get("path", ""))
            elif name == "reload_operator": return await self.reload_operator()

            for circuit in self.circuit_manager.circuits.values():
                if name in [t.name for t in circuit.get_tools()]:
                    return await circuit.call_tool(name, args)
            raise ValueError(f"Tool not found: {name}")

    async def reload_operator(self) -> list[types.TextContent]:
        """[대장님 🎯] 수동으로 지휘소의 모든 정보를 최신화합니다."""
        try:
            self.circuit_manager._discover_circuits()
            self.core_actions = CoreActions(self.circuit_manager, self.logger)
            self.last_circuit_keys = set(self.circuit_manager.circuits.keys())
            return [types.TextContent(type="text", text="✅ 지휘소 상태 동기화 완료! 🛡️⚡️")]
        except Exception as e:
            return [types.TextContent(type="text", text=f"❌ 동기화 실패: {str(e)}")]

    async def _autonomous_watcher(self):
        """[대장님 🎯] 5초마다 파일 시스템을 훑어 회선 변화를 감지하는 자율 감시 루프입니다. 🕵️‍♂️✨"""
        while True:
            await asyncio.sleep(5)
            try:
                # 현재 물리적 회선 상태 재탐색
                self.circuit_manager._discover_circuits()
                current_keys = set(self.circuit_manager.circuits.keys())
                
                # 변화 감지 시 자동 리로드 및 보고 📡
                if current_keys != self.last_circuit_keys:
                    added = current_keys - self.last_circuit_keys
                    removed = self.last_circuit_keys - current_keys
                    self.last_circuit_keys = current_keys
                    self.core_actions = CoreActions(self.circuit_manager, self.logger)
                    
                    if added: self.logger.log(f"🆕 새 회선 자율 감지됨: {added}", 0)
                    if removed: self.logger.log(f"🗑️ 삭제된 회선 메모리 정화: {removed}", 0)
                    
                    # [중요] 클라이언트에게 도구 목록이 바뀌었음을 알립니다 (지원 시) 🔔
                    if hasattr(self.server, "request_context"):
                        try: await self.server.request_context.session.send_notification("notifications/tools/list_changed", None)
                        except: pass
            except: pass

    async def start(self):
        self.logger.log("🚀 Operator (교환) 자율 감시 모드 기동!", 0)
        # 자율 감시 루프를 백그라운드에서 가동합니다. 🛡️⚡️
        asyncio.create_task(self._autonomous_watcher())
        
        async with stdio_server() as (read_stream, write_stream):
            await self.server.run(read_stream, write_stream, InitializationOptions(server_name="operator", server_version="1.0.0", capabilities=self.server.get_capabilities(notification_options=NotificationOptions(), experimental_capabilities={})))

if __name__ == "__main__":
    asyncio.run(OperatorServer().start())
