#
#  server.py - Autonomous Watcher Operator Server (Strict Clean Architecture)
#

import asyncio
import os
import sys
import inspect
import json
import websockets
from datetime import datetime
from mcp_operator.common.models import ResponseHandler, TextResponse
import mcp.types as types
from mcp.server.models import InitializationOptions
from mcp.server import NotificationOptions, Server
from mcp.server.stdio import stdio_server

from mcp_operator.registry.circuits.manager import CircuitManager
from mcp_operator.engine.actions import CoreActions
from mcp_operator.engine.protocols import GlobalProtocols
from mcp_operator.engine.logger import OperatorLogger
from mcp_operator.engine.sentinel import Sentinel
from enum import Enum

class McpRawAction(str, Enum):
    """[Specification] 웹소켓 다이렉트 명령어 (P-6)"""
    GET_STATUS = "get_operator_status"
    SET_CIRCUIT = "set_active_circuit"
    SYNC_PATH = "sync_operator_path"
    RELOAD = "reload_operator"

class OperatorServer:
    """
    [Main Class] 오퍼레이터 시스템의 MCP 서버 엔트리포인트입니다. (Protocol P-1)
    """
    
    def __init__(self):
        """서버 구성 요소 초기화 및 지휘 지침 생성"""
        self.logger = OperatorLogger("MasterOperator")
        self.sentinel = Sentinel()
        self.circuit_manager = CircuitManager()
        self.core_actions = CoreActions(self.circuit_manager, self.logger)
        self.server = Server("operator-hub")
        self._session = None # [사용자] MCP 세션 참조 보관용
        
        self.instructions = self._assemble_instructions_handler()
        self.last_circuit_keys = set(self.circuit_manager.circuits.keys())
        self._tool_map = {}
        
        # [사용자] 웹소켓 클라이언트 관리용 집합
        self.ws_clients = set()
        
        self._setup_mcp_handlers()
        self._refresh_tool_cache_handler()
        
        # [사용자] 로거에 웹소켓 전송 함수 연결
        self.logger.set_broadcast_handler(self.broadcast_message)

    async def broadcast_message(self, message: dict):
        """[Handler] 연결된 모든 호버크래프트 UI에 신호를 전송합니다."""
        if not self.ws_clients: return

        # [Sync] 타임스탬프 형식을 ISO 문자열로 통일 (UI 파싱 오류 방지)
        if "timestamp" not in message:
            message["timestamp"] = datetime.now().isoformat()

        data = json.dumps(message, ensure_ascii=False)
        # [Socket Log] 무한 루프 방지를 위해 직접 stderr 출력 (logger.log 사용 금지)
        now = datetime.now().strftime("%H:%M:%S.%f")[:-3]
        print(f" [{now}] [OPERATOR] [MasterOperator]    ├─ 📤 [Socket] Outgoing (to {len(self.ws_clients)} clients): {data[:100]}...", file=sys.stderr)
        
        disconnected = set()
        for ws in self.ws_clients:
            try:
                await ws.send(data)
            except websockets.exceptions.ConnectionClosed:
                disconnected.add(ws)
        self.ws_clients -= disconnected

    async def broadcast_operator_status(self):
        """[Internal] 현재 오퍼레이터의 활성 상태를 모든 UI에 동기화합니다."""
        active = self.circuit_manager.get_active_circuit()
        active_details = await asyncio.to_thread(self.core_actions.get_active_circuit_details)
        
        status_packet = {
            "type": "STATUS_UPDATE",
            "active_circuit": active.get_name() if active else "None",
            "registered_circuits": list(self.circuit_manager.circuits.keys()),
            "active_units": getattr(self.circuit_manager, "active_units", []),
            "path": getattr(self.circuit_manager, "current_path", "Unknown"),
            "active_circuit_details": active_details
        }
        await self.broadcast_message(status_packet)

    async def ws_handler(self, websocket):
        """[Handler] 새로운 호버크래프트 UI 접속 처리"""
        self.ws_clients.add(websocket)
        remote_addr = websocket.remote_address
        self.logger.log(f" 🔌 [Socket] 호버크래프트 업링크 연결됨 (IP: {remote_addr}, Active: {len(self.ws_clients)})", 0)
        
        try:
            # [INIT] 접속 즉시 현재 시스템 가용 정보 전송
            active = self.circuit_manager.get_active_circuit()
            active_details = await asyncio.to_thread(self.core_actions.get_active_circuit_details)
            
            await websocket.send(json.dumps({
                "type": "INIT",
                "timestamp": datetime.now().isoformat(),
                "data": {
                    "active_circuit": active.get_name() if active else "None",
                    "circuits": list(self.circuit_manager.circuits.keys()),
                    "path": getattr(self.circuit_manager, "current_path", "Unknown"),
                    "active_circuit_details": active_details
                }
            }, ensure_ascii=False))

            async for message in websocket:
                try:
                    data = json.loads(message)
                    if data.get("type") != "COMMAND": continue
                    
                    action_raw = data.get("action")
                    print(f" [{datetime.now().strftime('%H:%M:%S')}] [UPLINK] 📥 Incoming: {action_raw}", file=sys.stderr)
                    
                    # [ACK] 명령 수신 즉시 응답 전송 (처리 유무 관계없이)
                    await websocket.send(json.dumps({
                        "type": "RESPONSE",
                        "action": action_raw,
                        "status": "RECEIVED",
                        "timestamp": datetime.now().isoformat()
                    }, ensure_ascii=False))

                    match action_raw:
                        case McpRawAction.GET_STATUS:
                            await self._handle_direct_status_request()
                        case McpRawAction.SET_CIRCUIT:
                            await self._handle_direct_circuit_switch(data.get("name"))
                        case _:
                            print(f" ⚠️ Unknown Command: {action_raw}", file=sys.stderr)

                except json.JSONDecodeError: pass
                except Exception as e:
                    self.logger.log(f" ❌ [Socket] 업링크 명령 처리 중 에러: {str(e)}", 0)
        finally:
            self.ws_clients.remove(websocket)
            self.logger.log(f" 🔌 [Socket] 호버크래프트 업링크 해제 (Active: {len(self.ws_clients)})", 0)

    async def _handle_direct_status_request(self):
        """[Internal] UI로부터의 직접 상태 요청 처리"""
        try:
            res = await asyncio.to_thread(self.core_actions.get_operator_status)
            status_text = res[0].text if res and len(res) > 0 else "상태 정보를 가져올 수 없습니다."
            
            await self.broadcast_message({
                "type": "LOG", "level": "plain", "category": "OPERATOR",
                "message": f"✔ 시스템 상태 동기화 완료\n{status_text}"
            })
            await self.broadcast_operator_status()
        except Exception as e:
            await self._broadcast_error(f"상태 조회 실패: {str(e)}")

    async def _handle_direct_circuit_switch(self, circuit_name: str):
        """[Internal] UI로부터의 직접 회선 전환 처리"""
        if not circuit_name: return
        try:
            res = await asyncio.to_thread(self.core_actions.set_active_circuit, circuit_name)
            context_card = res[0].text if res and len(res) > 0 else f"회선 '{circuit_name}'으로 전환되었습니다."
            
            await self.broadcast_message({
                "type": "LOG", "level": "plain", "category": "OPERATOR",
                "message": f"▶ {context_card}"
            })
            await self.broadcast_operator_status()
        except Exception as e:
            await self._broadcast_error(f"회선 전환 실패: {str(e)}")

    async def _broadcast_error(self, message: str):
        """[Internal] 에러 발생 시 UI로 즉시 브로드캐스트"""
        await self.broadcast_message({
            "type": "LOG", "level": "error", "category": "ERROR", "message": f"❌ {message}"
        })

    async def start_ws_server(self):
        """[Handler] 웹소켓 서버 가동 (Port: 3001)"""
        # [사용자] 0.0.0.0 바인딩으로 로컬 루프백(127.0.0.1) 및 호스트 이름(localhost) 모두 지원
        # reuse_address=True: 서버 재시작 시 포트 점유 에러 방지 (Windows 안정성 향상)
        async with websockets.serve(self.ws_handler, "0.0.0.0", 3001, reuse_address=True):
            await asyncio.Future() # 영구 실행

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
            import importlib
            import sys

            # [사용자] 구식 최상위 모듈 캐시만 제거하여 새로운 패키지 구조와의 충돌을 방지합니다.
            legacy_targets = ('circuits', 'core', 'shared', 'units')
            keys_to_del = [k for k in sys.modules.keys() if k.startswith(legacy_targets)]
            for k in keys_to_del:
                del sys.modules[k]

            # 매니저 모듈 강제 리로드 (회선 재탐색용)
            import mcp_operator.registry.circuits.manager
            importlib.reload(mcp_operator.registry.circuits.manager)
            from mcp_operator.registry.circuits.manager import CircuitManager

            # 런타임 회선 재탐색
            self.circuit_manager = CircuitManager()

            await asyncio.to_thread(self.circuit_manager.discover_circuits_handler)
            
            # 액션 엔진 재인스턴스화
            self.core_actions = CoreActions(self.circuit_manager, self.logger)
            self.last_circuit_keys = set(self.circuit_manager.circuits.keys())
            self._refresh_tool_cache_handler()
            return TextResponse(" 지휘소 상태 동기화 완료! ")
        except Exception as e:
            import traceback
            err_msg = traceback.format_exc()
            print(f"[Reload Error] {err_msg}", file=sys.stderr)
            return TextResponse(f" 동기화 실패: {str(e)}\n{err_msg[:500]}...")

    async def start_server_handler(self):
        """[Handler] 서버 기동"""
        # [사용자] 웹소켓 서버를 백그라운드 태스크로 가동
        asyncio.create_task(self.start_ws_server())
        
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
        # [사용자] 현재 세션을 캡처하여 웹소켓 업링크(ws_handler)에서 알림을 보낼 수 있게 합니다.
        try:
            self._session = self.server.request_context.get().session
        except: pass

        handler = self._tool_map.get(name)
        if not handler: raise ValueError(f"Tool not found: {name}")
        
        # 1. 회선 객체의 직접 호출 (async)
        if hasattr(handler, "call_tool"): 
            res = await handler.call_tool(name, args)
        else:
            # 2. 캐시된 핸들러(람다) 호출
            res = handler(args)
            # 만약 코루틴이면 대기 (asyncio.to_thread 또는 async handler 대응)
            if asyncio.iscoroutine(res): res = await res
        
        # [Sync] 상태 변경이 발생하는 도구인 경우 웹 UI에 즉시 동기화 패킷 전송
        if name in ["set_active_circuit", "sync_operator_path", "reload_operator"]:
            asyncio.create_task(self.broadcast_operator_status())
            
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

