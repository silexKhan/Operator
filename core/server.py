#
#  server.py - Autonomous Watcher Operator Server (Strict Clean Architecture)
#

import asyncio
import os
import sys
import inspect
from shared.models import ResponseHandler, TextResponse
import mcp.types as types
from mcp.server.models import InitializationOptions
from mcp.server import NotificationOptions, Server
from mcp.server.stdio import stdio_server

from circuits.manager import CircuitManager
from core.actions import CoreActions
from core.protocols import GlobalProtocols
from core.logger import OperatorLogger

class OperatorServer:
    """
    [Main Class] 오퍼레이터 시스템의 MCP 서버 엔트리포인트입니다. (Protocol P-1)
    """
    
    def __init__(self):
        """서버 구성 요소 초기화 및 지휘 지침 생성"""
        self.logger = OperatorLogger("MasterOperator")
        self.circuit_manager = CircuitManager()
        self.core_actions = CoreActions(self.circuit_manager, self.logger)
        self.server = Server("operator-hub")
        
        self.instructions = self._assemble_instructions_handler()
        self.last_circuit_keys = set(self.circuit_manager.circuits.keys())
        self._tool_map = {}
        
        self._setup_mcp_handlers()
        self._refresh_tool_cache_handler()

    # -------------------------------------------------------------------------
    # [Handlers] 서버 운영 및 이벤트 관리 (Protocol P-4)
    # -------------------------------------------------------------------------

    def _setup_mcp_handlers(self):
        """[Handler] MCP 규격 핸들러 등록"""
        
        @self.server.list_tools()
        async def handle_list_tools() -> list[types.Tool]:
            return self._get_merged_tool_list_handler()

        @self.server.list_prompts()
        async def handle_list_prompts() -> list[types.Prompt]:
            return [types.Prompt(name="operator_welcome", description="오퍼레이터 초기 대화 템플릿", arguments=[])]

        @self.server.get_prompt()
        async def handle_get_prompt(name: str, arguments: dict | None) -> types.GetPromptResult:
            return self._process_prompt_handler(name)

        @self.server.call_tool()
        async def handle_call_tool(name: str, arguments: dict | None) -> list[types.TextContent]:
            return await self._dispatch_tool_handler(name, arguments or {})

    async def reload_operator_handler(self) -> list[types.TextContent]:
        """[Handler] 엔진 리로드"""
        try:
            # [강제 리로드] 런타임 모듈 캐시 초기화
            import importlib
            import circuits.manager
            importlib.reload(circuits.manager)
            from circuits.manager import CircuitManager
            
            # 런타임 회선 재탐색
            self.circuit_manager = CircuitManager()
            await asyncio.to_thread(self.circuit_manager.discover_circuits_handler)
            
            # 액션 엔진 재인스턴스화
            self.core_actions = CoreActions(self.circuit_manager, self.logger)
            self.last_circuit_keys = set(self.circuit_manager.circuits.keys())
            self._refresh_tool_cache_handler()
            return TextResponse(" 지휘소 상태 동기화 완료! ")
        except Exception as e:
            print(f"[Reload Error] {str(e)}", file=sys.stderr)
            return TextResponse(f" 동기화 실패: {str(e)}")

    async def start_server_handler(self):
        """[Handler] 서버 기동"""
        self.logger.log(" Operator (교환) 자율 감시 모드 기동!", 0)
        asyncio.create_task(self._autonomous_watcher_loop())
        
        async with stdio_server() as (read_stream, write_stream):
            await self.server.run(
                read_stream, write_stream,
                InitializationOptions(
                    server_name="operator", server_version="1.0.0",
                    capabilities=self.server.get_capabilities(notification_options=NotificationOptions(), experimental_capabilities={}),
                    instructions=self.instructions
                )
            )

    # -------------------------------------------------------------------------
    # [Internal Helpers] (P-4)
    # -------------------------------------------------------------------------

    def _assemble_instructions_handler(self) -> str:
        """[Internal] 지휘 지침 조립"""
        base = "당신은 오퍼레이터(Operator) 시스템의 메인 지휘 AI입니다. 아래 전사 규약을 최우선 준수하십시오:\n\n"
        rules = "\n".join(GlobalProtocols.get_rules())
        return base + rules

    def _refresh_tool_cache_handler(self):
        """[Internal] 도구 캐시 갱신 (P-3, P-4)"""
        # [사용자] 람다 내에서 self.core_actions를 참조하여 최신화된 객체를 항상 사용합니다.
        self._tool_map = {
            "get_operator_status": lambda args: asyncio.to_thread(self.core_actions.get_operator_status),
            "set_active_circuit": lambda args: asyncio.to_thread(self.core_actions.set_active_circuit, args.get("name", "")),
            "sync_operator_path": lambda args: asyncio.to_thread(self.core_actions.sync_operator_path, args.get("path", "")),
            "reload_operator": lambda args: self.reload_operator_handler(),
            # mcp_operator_ 접두어 도구 브릿지
            "mcp_operator_browse_directory": lambda args: asyncio.to_thread(self.core_actions.browse_directory, args.get("path", ".")),
            "mcp_operator_get_blueprint": lambda args: asyncio.to_thread(self.core_actions.get_blueprint, args.get("domain", "")),
            "mcp_operator_get_spec_content": lambda args: asyncio.to_thread(self.core_actions.get_spec_content, args.get("spec_file", "")),
            "mcp_operator_get_circuit_protocols": lambda args: asyncio.to_thread(self.core_actions.get_circuit_protocols, args.get("circuit_name", "")),
            "mcp_operator_get_global_protocols": lambda args: asyncio.to_thread(self.core_actions.get_global_protocols),
            "mcp_operator_get_full_json_structure": lambda args: asyncio.to_thread(self.core_actions.get_full_json_structure)
        }
        # 회선별 전용 도구 동적 매핑
        for circuit in self.circuit_manager.circuits.values():
            for t in circuit.get_tools():
                if t.name not in self._tool_map: self._tool_map[t.name] = circuit

    async def _dispatch_tool_handler(self, name: str, args: dict) -> list[types.TextContent]:
        """[Internal] 도구 호출 배분"""
        handler = self._tool_map.get(name)
        if not handler: raise ValueError(f"Tool not found: {name}")
        
        # 1. 회선 객체의 직접 호출 (async)
        if hasattr(handler, "call_tool"): 
            return await handler.call_tool(name, args)
        
        # 2. 캐시된 핸들러(람다) 호출
        res = handler(args)
        # 만약 코루틴이면 대기 (asyncio.to_thread 또는 async handler 대응)
        if asyncio.iscoroutine(res): return await res
        return res

    def _process_prompt_handler(self, name: str) -> types.GetPromptResult:
        """[Internal] 프롬프트 처리"""
        if name == "operator_welcome":
            circuits = list(self.circuit_manager.circuits.keys())
            msg = f"오퍼레이터 시스템 연결됨. 가용 회선: {circuits}\n어떤 회선으로 셋팅할까요?"
            return types.GetPromptResult(
                description="인사말",
                messages=[types.PromptMessage(role="user", content=types.TextContent(type="text", text=msg))]
            )
        raise ValueError(f"Prompt not found: {name}")

    def _get_merged_tool_list_handler(self) -> list[types.Tool]:
        """[Internal] 도구 목록 병합"""
        tools = [
            types.Tool(name="get_operator_status", description="상태 확인", inputSchema={"type": "object"}),
            types.Tool(name="set_active_circuit", description="회선 전환", inputSchema={"type": "object", "properties": {"name": {"type": "string"}}, "required": ["name"]}),
            types.Tool(name="reload_operator", description="엔진 리로드", inputSchema={"type": "object"})
        ]
        seen = {t.name for t in tools}
        for circuit in self.circuit_manager.circuits.values():
            for t in circuit.get_tools():
                if t.name not in seen:
                    tools.append(t)
                    seen.add(t.name)
        return tools

    async def _autonomous_watcher_loop(self):
        """[Internal] 자율 감시 루프"""
        while True:
            await asyncio.sleep(15)
            try:
                await asyncio.to_thread(self.circuit_manager.discover_circuits_handler)
                current_keys = set(self.circuit_manager.circuits.keys())
                if current_keys != self.last_circuit_keys:
                    await self.reload_operator_handler()
            except: pass

