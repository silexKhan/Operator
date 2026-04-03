#
#  server.py - Autonomous Watcher Operator Server (Strict Clean Architecture)
#

import asyncio
import os
import sys
import inspect
import json
import websockets
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
        
        # 메시지에 공통 타임스탬프 추가
        if "timestamp" not in message:
            message["timestamp"] = asyncio.get_event_loop().time()
            
        data = json.dumps(message, ensure_ascii=False)
        
        # [Socket Log] 송신 로그 강화
        self.logger.log(f" 📤 [Socket] Outgoing (to {len(self.ws_clients)} clients): {data[:100]}...", 1)
        
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
        status_packet = {
            "type": "STATUS_UPDATE",
            "active_circuit": active.get_name() if active else "None",
            "registered_circuits": list(self.circuit_manager.circuits.keys()),
            "active_units": getattr(self.circuit_manager, "active_units", []),
            "path": getattr(self.circuit_manager, "current_path", "Unknown")
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
            await websocket.send(json.dumps({
                "type": "INIT",
                "timestamp": asyncio.get_event_loop().time(),
                "data": {
                    "active_circuit": active.get_name() if active else "None",
                    "circuits": list(self.circuit_manager.circuits.keys()),
                    "path": getattr(self.circuit_manager, "current_path", "Unknown")
                }
            }, ensure_ascii=False))

            async for message in websocket:
                try:
                    # [Socket Log] 무한 루프 방지를 위해 직접 stderr 출력
                    now = datetime.now().strftime("%H:%M:%S.%f")[:-3]
                    print(f" [{now}] [OPERATOR] [Socket] 📥 Incoming: {message[:100]}...", file=sys.stderr)
                    
                    data = json.loads(message)
                    if data.get("type") == "COMMAND":
                        action = data.get("action")
                        
                        # [Terminal Output] Gemini CLI 터미널에 즉각적인 시각적 피드백 제공
                        self.logger.log(f" 📡 [Uplink] 웹 UI로부터 '{action}' 명령 수신", 0)

                        # [Web UI Feedback] 명령을 수신했음을 웹 UI에 먼저 알림 (level: plain으로 CSS 우회)
                        await self.broadcast_message({
                            "type": "LOG",
                            "level": "plain",
                            "category": "UPLINK",
                            "message": f"▶ 명령 처리 중: {action}..."
                        })

                        # [MCP Notification] Gemini CLI(Host)에게 알림 전송
                        if self._session:
                            try:
                                asyncio.create_task(self._session.send_log_message(
                                    level="warning",
                                    data=f"🚀 [Uplink] 웹 UI 요청: {action}"
                                ))
                            except: pass

                        if action == "get_operator_status":
                            # 실제 상태 조회 실행
                            status_res = self.core_actions.get_operator_status()
                            res_text = status_res[0].text if isinstance(status_res, list) else str(status_res)
                            
                            # 결과를 웹 UI로 브로드캐스트 (level: plain으로 CSS 우회)
                            await self.broadcast_message({
                                "type": "LOG",
                                "level": "plain",
                                "category": "OPERATOR",
                                "message": f"✔ 결과 수신: {res_text}"
                            })
                            # 상태 정보도 함께 갱신
                            await self.broadcast_operator_status()

                        elif action == "set_active_circuit":
                            # 웹에서 직접 회선 전환 요청 시
                            circuit_name = data.get("name")
                            if circuit_name:
                                res = self.core_actions.set_active_circuit(circuit_name)
                                await self.broadcast_operator_status()
                                await self.broadcast_message({
                                    "type": "LOG",
                                    "level": "plain",
                                    "category": "OPERATOR",
                                    "message": f"Circuit switched to: {circuit_name}"
                                })

                except json.JSONDecodeError:
                    pass
                except Exception as e:
                    self.logger.log(f" ❌ [Socket] 업링크 명령 처리 중 에러: {str(e)}", 0)
        finally:
            self.ws_clients.remove(websocket)
            self.logger.log(f" 🔌 [Socket] 호버크래프트 업링크 해제 (Active: {len(self.ws_clients)})", 0)

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

