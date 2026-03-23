#
#  main.py - Silex MCP Hub Orchestrator
#  Created by Gemini AIP on 2026. 03. 23.
#

import asyncio
import os
from mcp.server.models import InitializationOptions
from mcp.server import NotificationOptions, Server
from mcp.server.stdio import stdio_server
import mcp.types as types

from core.logger import HubLogger
from tenants.manager import TenantManager

# --- [대장님 🎯] 마스터 엔진 및 로거 설정 ---
server = Server("Silex MCP Hub")
logger = HubLogger("MasterHub") # 로거 다시 활성화 🚀
tenant_manager = TenantManager()

@server.list_tools()
async def handle_list_tools() -> list[types.Tool]:
    """
    Core 및 모든 등록된 Tenant의 도구 목록을 통합하여 반환합니다.
    (CLI의 동적 갱신 한계를 극복하기 위해 모든 도구를 Namespace로 구분하여 노출합니다.)
    """
    # 1. Core 공통 도구
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
    
    # 2. 모든 테넌트 도구 통합 (조용히 로드 🤫)
    for tenant in tenant_manager.tenants.values():
        tools.extend(tenant.get_tools())
        
    return tools

@server.call_tool()
async def handle_call_tool(name: str, arguments: dict | None) -> list[types.TextContent]:
    """
    요청된 도구를 Core 또는 Active Tenant에서 찾아 실행합니다.
    """
    logger.log(f"도구 실행 요청: {name}", 0)
    if arguments:
        logger.log(f"인자: {arguments}", 1)

    # 1. Core Tools 처리
    if name == "get_hub_status":
        active_name = "None"
        if t := tenant_manager.get_active_tenant(): active_name = t.get_name()
        
        res = f"🚀 Hub Status: Online\n📍 Path: {tenant_manager.current_path}\n🏢 Tenant: {active_name}"
        logger.log(f"상태 조회 결과: {active_name}", 1)
        return [types.TextContent(type="text", text=res)]

    elif name == "set_active_tenant":
        tenant_name = (arguments or {}).get("name", "")
        if tenant_manager.set_active_tenant(tenant_name):
            logger.log(f"테넌트 변경 성공: {tenant_name}", 1)
            return [types.TextContent(type="text", text=f"✅ {tenant_name} 테넌트가 성공적으로 활성화되었습니다!")]
        
        logger.log(f"테넌트 변경 실패 (찾을 수 없음): {tenant_name}", 1)
        return [types.TextContent(type="text", text=f"❌ '{tenant_name}' 테넌트를 찾을 수 없습니다.")]

    elif name == "sync_hub_path":
        target_path = (arguments or {}).get("path", "")
        tenant_manager.sync_path(target_path)
        active_name = "None"
        if t := tenant_manager.get_active_tenant(): active_name = t.get_name()
        
        logger.log(f"경로 동기화: {target_path} (테넌트: {active_name})", 1)
        return [types.TextContent(type="text", text=f"🔄 경로 동기화 완료: {target_path}\n🏢 감지된 테넌트: {active_name}")]

    # 2. Tenant Tools 처리
    if active_tenant := tenant_manager.get_active_tenant():
        # [대장님 🎯] 호출된 도구가 현재 활성 테넌트의 Namespace를 따르는지 엄격히 확인합니다!
        tenant_prefix = active_tenant.get_name().lower() + "_"
        if name.startswith(tenant_prefix):
            logger.log(f"테넌트 '{active_tenant.get_name()}' 도구 실행 위임: {name}", 1)
            return await active_tenant.call_tool(name, arguments or {})
        else:
            logger.log(f"⚠️ [격리 경고] 현재 활성 테넌트({active_tenant.get_name()})의 도구가 아닙니다: {name}", 1)
            return [types.TextContent(type="text", text=f"❌ '{name}' 도구는 현재 활성화된 '{active_tenant.get_name()}' 테넌트 전용 도구가 아닙니다.")]

    logger.log(f"❌ 테넌트 미활성 또는 도구 찾을 수 없음: {name}", 1)
    raise ValueError(f"Tool not found or Tenant not active: {name}")

async def run_server():
    async with stdio_server() as (read_stream, write_server):
        await server.run(
            read_stream,
            write_server,
            InitializationOptions(
                server_name="Silex MCP Hub",
                server_version="1.0.0",
                capabilities=server.get_capabilities(
                    notification_options=NotificationOptions(),
                    experimental_capabilities={},
                ),
            ),
        )

if __name__ == "__main__":
    try:
        asyncio.run(run_server())
    except Exception as e:
        logger.log(f"🔥 치명적 서버 에러 발생: {str(e)}", 0)
        import traceback
        logger.log(traceback.format_exc(), 1)
