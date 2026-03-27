#
#  server.py - Silex MCP Hub Core Server Orchestrator
#

import asyncio
from mcp.server.models import InitializationOptions
from mcp.server import NotificationOptions, Server
from mcp.server.stdio import stdio_server
import mcp.types as types

from core.logger import HubLogger
from core.actions import CoreActions
from tenants.manager import TenantManager

class HubServer:
    def __init__(self):
        self.server = Server("Silex MCP Hub")
        self.logger = HubLogger("MasterHub")
        self.tenant_manager = TenantManager()
        self.core_actions = CoreActions(self.tenant_manager, self.logger)
        
        self._register_handlers()

    def _register_handlers(self):
        """MCP 서버 핸들러 등록 (Routing)"""
        
        @self.server.list_tools()
        async def handle_list_tools() -> list[types.Tool]:
            # 1. Core 공통 도구 정의
            tools = [
                types.Tool(
                    name="get_hub_status",
                    description="Silex MCP Hub의 현재 상태 및 활성 테넌트 정보를 확인합니다.",
                    inputSchema={"type": "object", "properties": {}},
                ),
                types.Tool(
                    name="set_active_tenant",
                    description="특정 테넌트를 강제로 활성화합니다.",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "name": {"type": "string", "description": "활성화할 테넌트 이름 (예: GDR)"}
                        },
                        "required": ["name"]
                    },
                ),
                types.Tool(
                    name="sync_hub_path",
                    description="Hub의 현재 작업 경로를 외부 환경과 동기화하여 자동 감지를 수행합니다.",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "path": {"type": "string", "description": "현재 작업 디렉토리 절대 경로"}
                        },
                        "required": ["path"]
                    },
                )
            ]
            
            # 2. 모든 테넌트 도구 통합 노출
            for tenant in self.tenant_manager.tenants.values():
                tools.extend(tenant.get_tools())
                
            return tools

        @self.server.call_tool()
        async def handle_call_tool(name: str, arguments: dict | None) -> list[types.TextContent]:
            self.logger.log(f"도구 실행 요청: {name}", 0)
            args = arguments or {}

            # 1. Core Tools 라우팅
            if name == "get_hub_status":
                return self.core_actions.get_hub_status()
            elif name == "set_active_tenant":
                return self.core_actions.set_active_tenant(args.get("name", ""))
            elif name == "sync_hub_path":
                return self.core_actions.sync_hub_path(args.get("path", ""))

            # 2. Tenant Tools 라우팅 및 위임
            active_tenant = self.tenant_manager.get_active_tenant()
            if active_tenant:
                tenant_prefix = active_tenant.get_name().lower() + "_"
                tenant_tool_names = [t.name for t in active_tenant.get_tools()]
                
                if name.startswith(tenant_prefix) or name in tenant_tool_names:
                    self.logger.log(f"테넌트 '{active_tenant.get_name()}' 도구 실행 위임: {name}", 1)
                    return await active_tenant.call_tool(name, args)
            
            # 3. Fallback: 타 테넌트 도구 검색
            for tenant in self.tenant_manager.tenants.values():
                if name.startswith(tenant.get_name().lower() + "_") or name in [t.name for t in tenant.get_tools()]:
                    self.logger.log(f"타 테넌트 '{tenant.get_name()}' 도구 발견, 실행 위임: {name}", 1)
                    return await tenant.call_tool(name, args)

            raise ValueError(f"Tool not found or Tenant not active: {name}")

    async def start(self):
        """MCP 서버 실행 루프 시작"""
        self.logger.log("🚀 Silex MCP Hub 기동 중...", 0)
        async with stdio_server() as (read_stream, write_server):
            await self.server.run(
                read_stream,
                write_server,
                InitializationOptions(
                    server_name="Silex MCP Hub",
                    server_version="1.0.0",
                    capabilities=self.server.get_capabilities(
                        notification_options=NotificationOptions(),
                        experimental_capabilities={},
                    ),
                ),
            )

if __name__ == "__main__":
    hub = HubServer()
    asyncio.run(hub.start())
