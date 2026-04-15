#
#  server.py - Autonomous Watcher Operator Server (Strict Clean Architecture)
#

import asyncio
import os
import sys
import inspect
import json
import time
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
        # [Sync] 통합 지휘 API 위임을 위해 매니저에 코어 액션 참조 연결
        self.circuit_manager.core_actions = self.core_actions
        
        # [I18N] 다국어 지원 프로토콜 인스턴스화
        self.global_protocols = GlobalProtocols()
        
        self.server = Server("operator-hub")
        self._session = None # [사용자] MCP 세션 참조 보관용
        
        self.instructions = self._assemble_instructions_handler()
        self.last_circuit_keys = set(self.circuit_manager.circuits.keys())
        self._tool_map = {}
        
        self._setup_mcp_handlers()
        self._refresh_tool_cache_handler()
        
        # [사용자] 로거에 IPC 전송 함수 연결
        self.logger.set_broadcast_handler(self.broadcast_message)

    async def broadcast_message(self, message: dict):
        """[Handler] 메시지를 파일 시스템 IPC(JSON/Log)로 전송합니다."""
        # [Sync] 타임스탬프 형식을 ISO 문자열로 통일
        if "timestamp" not in message:
            message["timestamp"] = datetime.now().isoformat()

        # [IPC] 로그 메시지인 경우 실시간 로그 파일에 기록 (JSON Lines 형식)
        if message.get("type") == "LOG" or "message" in message:
            try:
                os.makedirs("logs", exist_ok=True)
                log_entry = {
                    "timestamp": message.get("timestamp", datetime.now().isoformat()),
                    "level": message.get("level", "INFO"),
                    "category": message.get("category", "SYSTEM"),
                    "message": message.get("message", "")
                }
                with open("logs/mcp_live.log", "a", encoding="utf-8") as f:
                    f.write(json.dumps(log_entry, ensure_ascii=False) + "\n")
            except Exception as e:
                print(f" ❌ [IPC Error] 로그 파일 기록 실패: {str(e)}", file=sys.stderr)

        # [IPC] 상태 파일 업데이트 (모든 브로드캐스트 호출 시 실시간성 보장)
        await self.write_state_to_file()
        
        # [Debug Log] stderr 출력 유지 (Socket 대신 IPC 표기)
        now = datetime.now().strftime("%H:%M:%S.%f")[:-3]
        print(f" [{now}] [OPERATOR] [MasterOperator]    ├─ 💾 [IPC] Outgoing: {str(message)[:100]}...", file=sys.stderr)

    async def write_state_to_file(self, custom_status: str = "active"):
        """[Internal] 현재 시스템 상태를 파일에 동기화합니다. (IPC 전환)"""
        try:
            active = self.circuit_manager.get_active_circuit()
            # [Optimization] 비동기 쓰레드에서 상세 정보 조회
            active_details = await asyncio.to_thread(self.core_actions.get_active_circuit_details)
            
            state = {
                "active_circuit": active.get_name() if active else "None",
                "registered_circuits": list(self.circuit_manager.circuits.keys()),
                "active_units": getattr(self.circuit_manager, "active_units", []),
                "path": getattr(self.circuit_manager, "current_path", "Unknown"),
                "status": custom_status,
                "active_circuit_details": active_details,
                "timestamp": datetime.now().isoformat()
            }
            
            # [Sync] 파일 쓰기 (디렉토리 자동 생성)
            os.makedirs("data", exist_ok=True)
            with open("data/mcp_state.json", "w", encoding="utf-8") as f:
                json.dump(state, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f" ❌ [IPC Error] 상태 파일 기록 실패: {str(e)}", file=sys.stderr)

    async def broadcast_operator_status(self):
        """[Internal] 현재 오퍼레이터의 활성 상태를 동기화합니다. (IPC)"""
        # [Sync] broadcast_message를 호출하여 로그 기록(필요시) 및 상태 파일 업데이트 통합 수행
        await self.broadcast_message({"type": "STATUS_UPDATE"})

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

    def get_supported_languages_handler(self) -> list[types.TextContent]:
        """[Tool] 지원되는 언어 목록을 반환합니다."""
        supported = self.global_protocols.get_supported_languages()
        current = self.global_protocols.get_current_language()
        
        info = {
            "supported": supported,
            "current": current
        }
        return [types.TextContent(type="text", text=json.dumps(info, ensure_ascii=False, indent=2))]

    async def set_language_handler(self, lang_code: str) -> list[types.TextContent]:
        """[Tool] 시스템 언어를 변경합니다."""
        success = self.global_protocols.set_language(lang_code)
        if success:
            # [I18N] 언어 변경 시 지휘 지침 즉시 갱신
            self.instructions = self._assemble_instructions_handler()
            
            # [Sync] UI에 언어 변경 알림 전송
            msg = self.global_protocols.get_message("INIT_SUCCESS")
            await self.broadcast_message({
                "type": "LOG",
                "level": "INFO",
                "message": f"Language changed to: {lang_code}. {msg}",
                "category": "SYSTEM"
            })
            
            return [types.TextContent(type="text", text=f"Language switched to '{lang_code}' successfully.")]
        else:
            return [types.TextContent(type="text", text=f"Failed to switch language. '{lang_code}' is not supported.")]

    async def reload_operator_handler(self) -> list[types.TextContent]:
        """[Handler] 엔진 리로드 수행 (In-process Reload)"""
        try:
            self.logger.log(" 🔄 [SYSTEM] 내부 엔진 리로드를 시작합니다...", 1)
            
            # 1. 회선 매니저를 통한 물리적 파일 재탐색 및 모듈 리로드
            await asyncio.to_thread(self.circuit_manager.discover_circuits_handler)
            
            # 2. 서버 도구 캐시 갱신
            self._refresh_tool_cache_handler()
            
            # 3. 변경된 지휘 지침 갱신
            self.instructions = self._assemble_instructions_handler()
            
            # 4. 상태 업데이트 알림
            await self.broadcast_operator_status()
            
            return [types.TextContent(type="text", text=" ✅ 엔진 리로드가 성공적으로 완료되었습니다. (연결 유지) ")]
        except Exception as e:
            self.logger.log(f" 🚨 [SYSTEM] 리로드 중 오류 발생: {str(e)}", 2)
            return [types.TextContent(type="text", text=f" 리로드 실패: {str(e)} ")]

    async def start_server_handler(self):
        """[Handler] 서버 기동"""
        # [IPC] 서버 기동 시 초기 상태 파일 생성
        await self.write_state_to_file(custom_status="starting")
        
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
        rules = "\n".join(self.global_protocols.get_rules())
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
            "mcp_operator_get_spec_content": lambda args: asyncio.to_thread(self.core_actions.get_spec_content, args.get("spec_file", "")),
            "mcp_operator_get_circuit_protocols": lambda args: asyncio.to_thread(self.core_actions.get_circuit_protocols, args.get("circuit_name", "")),
            "mcp_operator_get_global_protocols": lambda args: asyncio.to_thread(self.core_actions.get_global_protocols),
            "mcp_operator_get_full_json_structure": lambda args: asyncio.to_thread(self.core_actions.get_full_json_structure),
            # [I18N] 다국어 지원 도구
            "get_supported_languages": lambda args: self.get_supported_languages_handler(),
            "set_language": lambda args: self.set_language_handler(args.get("lang_code", ""))
        }
        # 회선별 전용 도구 동적 매핑
        for circuit in self.circuit_manager.circuits.values():
            for t in circuit.get_tools():
                if t.name not in self._tool_map: self._tool_map[t.name] = circuit

    async def _dispatch_tool_handler(self, name: str, args: dict) -> list[types.TextContent]:
        """[Internal] 도구 호출 배분"""
        # [사용자] 현재 세션을 캡처하여 필요한 경우 알림을 보낼 수 있게 합니다.
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
        
        # [Sync] 상태 변경이 발생하는 도구인 경우 IPC를 통해 즉시 상태 파일 갱신
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
