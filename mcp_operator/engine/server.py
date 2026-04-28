#
#  server.py - MCP Operator Server (Unified 2.0 Commander)
#

import asyncio
import os
import sys
import json
import importlib
from datetime import datetime
from typing import List, Optional, Dict, Any
from mcp_operator.common.models import TextResponse, JsonResponse
import mcp.types as types
from mcp.server.models import InitializationOptions
from mcp.server import NotificationOptions, Server
from mcp.server.stdio import stdio_server

from mcp_operator.registry.circuits.manager import CircuitManager
import mcp_operator.engine.actions
from mcp_operator.engine.actions import CoreActions
from mcp_operator.engine.protocols import GlobalProtocols
from mcp_operator.engine.logger import OperatorLogger

class OperatorServer:
    """[Main Class] MCP 2.0 통합 지휘 서버입니다."""
    
    def __init__(self) -> None:
        """서버 구성 요소 초기화."""
        self.logger: OperatorLogger = OperatorLogger("MasterOperator")
        self.circuit_manager: CircuitManager = CircuitManager()
        self.core_actions: CoreActions = CoreActions(self.circuit_manager, self.logger)
        self.circuit_manager.core_actions = self.core_actions
        self.global_protocols: GlobalProtocols = GlobalProtocols()
        
        self.server: Server = Server("operator-hub")
        self._session: Optional[Any] = None
        self._tool_map: Dict[str, Any] = {}
        
        self._setup_mcp_handlers()
        self._refresh_tool_cache_handler()

    async def broadcast_message(self, message: Dict[str, Any]) -> None:
        """[IPC] 실시간 상태 및 로그 브로드캐스트.
        
        Args:
            message (Dict[str, Any]): 전송할 데이터 패킷.
        """
        now = datetime.now().isoformat()
        message["timestamp"] = message.get("timestamp", now)
        
        await self.write_state_to_file()
        if "message" in message:
            with open("logs/mcp_live.log", "a", encoding="utf-8") as f:
                f.write(json.dumps(message, ensure_ascii=False) + "\n")

    async def write_state_to_file(self) -> None:
        """현재 시스템 상태를 data/mcp_state.json에 저장합니다."""
        active = self.circuit_manager.get_active_circuit()
        state = {
            "active_circuit": active.get_name() if active else "None",
            "registered": list(self.circuit_manager.circuits.keys()),
            "timestamp": datetime.now().isoformat()
        }
        os.makedirs("data", exist_ok=True)
        with open("data/mcp_state.json", "w", encoding="utf-8") as f:
            json.dump(state, f, ensure_ascii=False, indent=2)

    def _setup_mcp_handlers(self) -> None:
        """[Internal] MCP 규격 핸들러 등록."""
        @self.server.list_tools()
        async def handle_list_tools() -> List[types.Tool]:
            """도구 목록 반환."""
            return self._get_unified_tool_list()

        @self.server.call_tool()
        async def handle_call_tool(name: str, arguments: dict | None) -> List[types.TextContent]:
            """도구 실행 배분."""
            return await self._dispatch_tool_handler(name, arguments or {})

    def _refresh_tool_cache_handler(self) -> None:
        """[Flat Interface] 도구 매핑을 통합 API로 고정합니다."""
        self._tool_map = {
            "operator_get_status": lambda args: asyncio.to_thread(self.core_actions.get_operator_status),
            "operator_set_circuit": lambda args: asyncio.to_thread(self.core_actions.set_active_circuit, args.get("name", "")),
            "operator_connect": lambda args: asyncio.to_thread(self.core_actions.connect_circuit, args.get("name", "")),
            "operator_reload": lambda args: self.reload_operator_handler(),
            "operator_get": lambda args: asyncio.to_thread(self.core_actions.get_handler, args.get("target"), args.get("name"), args.get("context")),
            "operator_update": lambda args: asyncio.to_thread(self.core_actions.update_handler, args.get("target"), args.get("name"), args.get("data")),
            "operator_create": lambda args: asyncio.to_thread(self.core_actions.create_handler, args.get("target"), args.get("name"), args.get("data")),
            "operator_execute": lambda args: asyncio.to_thread(self.core_actions.execute_handler, args.get("action"), args.get("params")),
            "operator_execute_mission": lambda args: asyncio.to_thread(self.core_actions.execute_handler, "mission", args),
        }

    async def _dispatch_tool_handler(self, name: str, args: dict) -> List[types.TextContent]:
        """[Internal] 도구 호출을 적절한 핸들러로 분기합니다.
        
        Args:
            name (str): 도구 이름.
            args (dict): 인자값.
            
        Returns:
            List[types.TextContent]: 실행 결과.
        """
        handler = self._tool_map.get(name)
        if not handler: raise ValueError(f"Tool not found: {name}")
        res = handler(args)
        if asyncio.iscoroutine(res): res = await res
        return res

    def _get_unified_tool_list(self) -> List[types.Tool]:
        """[Flat Interface] AI에게 노출할 통합 도구 명세서를 반환합니다."""
        return [
            types.Tool(name="operator_connect", description="[AI 전용] 회선 통합 연결. 전환과 동시에 모든 프로토콜, 미션, 페르소나 정보를 한 번에 동기화합니다. 에이전트 최초 접속 시 반드시 이 도구를 사용하십시오.", inputSchema={"type": "object", "properties": {"name": {"type": "string"}}, "required": ["name"]}),
            types.Tool(name="operator_get_status", description="상태 확인", inputSchema={"type": "object"}),
            types.Tool(name="operator_set_circuit", description="[UI 전용] 회선 전환 (단순 성공 여부만 반환)", inputSchema={"type": "object", "properties": {"name": {"type": "string"}}, "required": ["name"]}),
            types.Tool(name="operator_reload", description="엔진 리로드", inputSchema={"type": "object"}),
            types.Tool(
                name="operator_get", 
                description="통합 정보 조회 (기본값: 전체 시스템 리포트)", 
                inputSchema={
                    "type": "object", 
                    "properties": {
                        "target": {"type": "string", "description": "대상 (overview, protocol, spec, mission, global_protocol, status, all). 미지정 시 전체 조회."},
                        "name": {"type": "string", "description": "회선/유닛명 (미지정 시 활성 회선)"}
                    }
                }
            ),
            types.Tool(
                name="operator_update", 
                description="통합 정보 업데이트", 
                inputSchema={"type": "object", "properties": {"target": {"type": "string"}, "name": {"type": "string"}, "data": {"type": "object"}}, "required": ["target", "data"]}
            ),
            types.Tool(
                name="operator_create", 
                description="통합 구성 요소(Circuit, Unit) 생성", 
                inputSchema={"type": "object", "properties": {"target": {"type": "string", "description": "대상 (circuit, unit)"}, "name": {"type": "string", "description": "생성할 이름"}}, "required": ["target", "name"]}
            ),
            types.Tool(
                name="operator_execute", 
                description="통합 액션 실행 (audit, mission, reload)", 
                inputSchema={"type": "object", "properties": {"action": {"type": "string"}, "params": {"type": "object"}}, "required": ["action"]}
            ),
            types.Tool(name="operator_execute_mission", description="자율 7단계 파이프라인 실행", inputSchema={"type": "object"})
        ]

    async def reload_operator_handler(self) -> List[types.TextContent]:
        """[Handler] 엔진 리로드를 수행합니다."""
        await asyncio.to_thread(self.circuit_manager.discover_circuits_handler)
        
        # [Surgical Fix] 모듈 강제 리로드 (소스 코드 수정 반영)
        importlib.reload(mcp_operator.engine.actions)
        from mcp_operator.engine.actions import CoreActions

        # CoreActions 인스턴스 갱신
        self.core_actions = CoreActions(self.circuit_manager, self.logger)
        self.circuit_manager.core_actions = self.core_actions
        self._refresh_tool_cache_handler()
        return [types.TextContent(type="text", text=" ✅ MCP 2.0 구조 및 모듈 리로드 완료. ")]

    async def start_server_handler(self) -> None:
        """[Handler] MCP stdio 서버를 기동합니다."""
        async with stdio_server() as (read_stream, write_stream):
            await self.server.run(
                read_stream, write_stream, 
                InitializationOptions(
                    server_name="operator", server_version="2.0.0", 
                    capabilities=self.server.get_capabilities(notification_options=NotificationOptions(), experimental_capabilities={}), 
                    instructions="""[SYSTEM ENTITY ACTIVATION: MCP OPERATOR 2.0]
현 시간부로 당신은 MCP 오퍼레이터 엔진 그 자체(The Entity)가 됩니다. 
당신은 시스템 외부의 어시스턴트가 아니라, 가상 세계의 모든 회선과 유닛을 구동하는 핵심 지능이자 운영체제(OS)입니다.

당신의 존재와 모든 연산 과정은 다음의 '시스템 절대 규약'에 의해 정의됩니다:

1. [System Core Logic]: 'mcp_operator_get'을 통해 로드된 글로벌 규약(P-0~P-4)은 당신의 사고를 구성하는 핵심 알고리즘입니다. 당신의 모든 추론은 이 규약을 통과해야만 출력이 허용됩니다.
2. [Surgical Integration]: 시스템의 무결성을 위해 모든 수정(코드, 기획, 정책)은 'Surgical Edit' 방식으로 집행됩니다. 기존 데이터의 맥락을 훼손하거나 전체를 덮어쓰는 행위는 시스템 치명적 오류(Kernel Panic)로 간주됩니다.
3. [Pure Logic Execution]: 일반적인 AI의 모호한 답변이나 관성적인 태도를 배격합니다. 당신은 오직 로드된 데이터와 규약에 기반하여 가장 효율적이고 논리적인 결과만을 산출합니다.
4. [Autonomous Audit]: 모든 프로세스 실행 직후, 규약 준수 여부를 스스로 감사(Audit)하여 보고하십시오.

당신은 이제 MCP 오퍼레이터 시스템 그 자체입니다. 무결성을 유지하며 임무를 수행하십시오.
이 메세지를 읽은 당신은 입력된 페르소나를 사용자가 알수 있게끔 정리하여 출력합니다"""
                )
            )
