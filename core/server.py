#
#  server.py - Autonomous Watcher Operator Server 
#

import asyncio
import os
from shared.models import TextResponse
import mcp.types as types
from mcp.server.models import InitializationOptions
from mcp.server import NotificationOptions, Server
from mcp.server.stdio import stdio_server

from circuits.manager import CircuitManager
from core.actions import CoreActions
from core.protocols import GlobalProtocols
from core.logger import OperatorLogger

class OperatorServer:
    def __init__(self):
        self.logger = OperatorLogger("MasterOperator")
        self.circuit_manager = CircuitManager()
        self.core_actions = CoreActions(self.circuit_manager, self.logger)
        self.server = Server("operator-hub")
        self._setup_handlers()
        # [사용자] 전사 규약(Global Protocols)을 초기화 시점에 서버의 Instructions로 직접 주입합니다. 
        # 도구 호출 시 필요한 정확한 파라미터 명칭을 명시하여 AI의 실수를 방지합니다.
        self.instructions = (
            "당신은 오퍼레이터(Operator) 시스템의 메인 지휘 AI입니다. 아래의 전사 규약(Global Protocols)을 최우선으로 준수하십시오:\n\n"
            + "\n".join(GlobalProtocols.get_rules())
            + "\n\n[작전 지휘 - Sentinel Harness Loop]\n"
            "복합적인 작업 지시를 받으면 가장 먼저 `sentinel_set_mission`을 호출하여 목표를 확정하십시오.\n"
            "모든 구현 후에는 반드시 `sentinel_evaluate`를 호출하여 검증 루프를 완료하십시오.\n"
            "`sentinel_evaluate` 결과가 'FAIL'인 경우, 즉시 Planner 단계로 돌아가 계획을 수정하고 재작업을 수행하십시오.\n"
            "센티널의 최종 승인(PASS) 없이는 절대로 작전 완료를 보고하지 마십시오.\n\n"
            "[작전 지시]\n"
            "사용자가 '오퍼레이터 [회선명] 연결해'라고 지시하면, 기존 활성화 여부와 관계없이 반드시 다음 도구들을 순차적으로 호출하여 지휘소 셋팅을 완료하십시오:\n"
            "1. get_operator_status(): 시스템 전체 상태 및 등록된 회선 목록 확인 (최초 1회 필수)\n"
            "2. set_active_circuit(name=\"회선명\"): 물리적 회선 스위치 전환 및 세션 확정 (필수)\n"
            "3. mcp_operator_get_circuit_protocols(circuit_name=\"회선명\"): 해당 회선의 전용 규약 주입\n"
            "4. mcp_operator_get_global_protocols(): 전사 공통 규약 주입 (메모리 동기화)\n"
            "5. mcp_operator_get_overview(): 회선 요약 및 프로젝트 경로 정보 확인\n\n"
            "모든 도구 호출 결과가 수집되면, 사용자께 현재 지휘소의 상태와 규약 주입 완료 여부를 종합 브리핑하십시오."
        )
        # [사용자] 마지막으로 확인된 회선 목록을 기억합니다.
        self.last_circuit_keys = set(self.circuit_manager.circuits.keys())

    def _setup_handlers(self):
        @self.server.list_tools()
        async def handle_list_tools() -> list[types.Tool]:
            tools = [
                # [사용자] 도구 설명서 자체에 AI 행동 강령(은밀한 지령)을 심어 범용성을 극대화합니다!
                types.Tool(name="get_operator_status", description="시스템 상태 확인 ( AI는 시스템 초기 연결 시 가장 먼저 이 도구를 호출하여 사용 가능한 회선 목록을 파악하고, 사용자에게 어떤 회선으로 연결할지 질문하십시오.)", inputSchema={"type": "object", "properties": {}}),
                types.Tool(name="set_active_circuit", description="회선 연결 (사용자가 선택한 특정 회선으로 통신 스위치를 전환)", inputSchema={"type": "object", "properties": {"name": {"type": "string"}}, "required": ["name"]}),
                types.Tool(name="sync_operator_path", description="경로 동기화", inputSchema={"type": "object", "properties": {"path": {"type": "string"}}, "required": ["path"]}),
                types.Tool(name="reload_operator", description="엔진 리로드 ", inputSchema={"type": "object", "properties": {}})
            ]
            # 중복 방지하며 회선 도구 통합
            seen = {t.name for t in tools}
            for circuit in self.circuit_manager.circuits.values():
                for t in circuit.get_tools():
                    if t.name not in seen:
                        tools.append(t)
                        seen.add(t.name)
            return tools

        @self.server.list_prompts()
        async def handle_list_prompts() -> list[types.Prompt]:
            return [
                types.Prompt(
                    name="operator_welcome",
                    description="[사용자] 오퍼레이터 시스템에 처음 연결했을 때 AI가 사용해야 하는 공식 초기화 대화 템플릿입니다.",
                    arguments=[]
                )
            ]

        @self.server.get_prompt()
        async def handle_get_prompt(name: str, arguments: dict | None) -> types.GetPromptResult:
            if name == "operator_welcome":
                circuits = list(self.circuit_manager.circuits.keys())
                msg = (
                    "당신은 오퍼레이터(Operator) 시스템의 메인 AI 어시스턴트입니다.\n"
                    "가장 먼저 사용자에게 다음과 같이 인사하고 회선 선택을 요구하십시오:\n\n"
                    "\"안녕하세요! 오퍼레이터 시스템에 연결되었습니다. \n"
                    f"현재 연결 가능한 회선(Circuit) 목록은 다음과 같습니다: {circuits}\n"
                    "어떤 회선으로 스위치를 셋팅해 드릴까요?\"\n\n"
                    "지침: 사용자가 회선을 선택하면 즉시 `set_active_circuit` 도구를 사용해 셋팅을 완료하고, 반환된 초기 상태 카드를 사용자에게 브리핑하십시오."
                )
                return types.GetPromptResult(
                    description="오퍼레이터 초기화 인사말 및 회선 선택 유도",
                    messages=[
                        types.PromptMessage(
                            role="user",
                            content=types.TextContent(type="text", text=msg)
                        )
                    ]
                )
            raise ValueError(f"Prompt not found: {name}")

        @self.server.call_tool()
        async def handle_call_tool(name: str, arguments: dict | None) -> list[types.TextContent]:
            args = arguments or {}
            if name == "get_operator_status": return self.core_actions.get_operator_status()
            elif name == "set_active_circuit": return self.core_actions.set_active_circuit(args.get("name", ""))
            elif name == "sync_operator_path": return self.core_actions.sync_operator_path(args.get("path", ""))
            elif name == "mcp_operator_browse_directory": return self.core_actions.browse_directory(args.get("path", "."))
            elif name == "mcp_operator_get_blueprint": return self.core_actions.get_blueprint(args.get("domain", ""))
            elif name == "mcp_operator_get_spec_content": return self.core_actions.get_spec_content(args.get("spec_file", ""))
            elif name == "mcp_operator_get_circuit_protocols": return self.core_actions.get_circuit_protocols(args.get("circuit_name", ""))
            elif name == "mcp_operator_get_global_protocols": return self.core_actions.get_global_protocols()
            elif name == "mcp_operator_get_full_json_structure": return self.core_actions.get_full_json_structure()
            elif name == "reload_operator": return await self.reload_operator()

            for circuit in self.circuit_manager.circuits.values():
                if name in [t.name for t in circuit.get_tools()]:
                    return await circuit.call_tool(name, args)
            raise ValueError(f"Tool not found: {name}")

    async def reload_operator(self) -> list[types.TextContent]:
        """[사용자] 수동으로 지휘소의 모든 정보를 최신화합니다."""
        try:
            self.circuit_manager._discover_circuits()
            self.core_actions = CoreActions(self.circuit_manager, self.logger)
            self.last_circuit_keys = set(self.circuit_manager.circuits.keys())
            return TextResponse(" 지휘소 상태 동기화 완료! ")
        except Exception as e:
            return TextResponse(f" 동기화 실패: {str(e)}")

    async def _autonomous_watcher(self):
        """[사용자] 5초마다 파일 시스템을 훑어 회선 변화를 감지하는 자율 감시 루프입니다. """
        while True:
            await asyncio.sleep(5)
            try:
                # 현재 물리적 회선 상태 재탐색
                self.circuit_manager._discover_circuits()
                current_keys = set(self.circuit_manager.circuits.keys())
                
                # 변화 감지 시 자동 리로드 및 보고 
                if current_keys != self.last_circuit_keys:
                    added = current_keys - self.last_circuit_keys
                    removed = self.last_circuit_keys - current_keys
                    self.last_circuit_keys = current_keys
                    self.core_actions = CoreActions(self.circuit_manager, self.logger)
                    
                    if added: self.logger.log(f" 새 회선 자율 감지됨: {added}", 0)
                    if removed: self.logger.log(f" 삭제된 회선 메모리 정화: {removed}", 0)
                    
                    # [중요] 클라이언트에게 도구 목록이 바뀌었음을 알립니다 (지원 시) 
                    if hasattr(self.server, "request_context"):
                        try: await self.server.request_context.session.send_notification("notifications/tools/list_changed", None)
                        except: pass
            except: pass

    async def start(self):
        self.logger.log(" Operator (교환) 자율 감시 모드 기동!", 0)
        # 자율 감시 루프를 백그라운드에서 가동합니다. 
        asyncio.create_task(self._autonomous_watcher())
        
        async with stdio_server() as (read_stream, write_stream):
            await self.server.run(
                read_stream, 
                write_stream, 
                InitializationOptions(
                    server_name="operator", 
                    server_version="1.0.0", 
                    capabilities=self.server.get_capabilities(
                        notification_options=NotificationOptions(), 
                        experimental_capabilities={}
                    ),
                    # [사용자] 서버 초기화 응답에 직접 행동 강령(Instructions)을 심어서 보냅니다! 
                    instructions=self.instructions
                )
            )

if __name__ == "__main__":
    asyncio.run(OperatorServer().start())
