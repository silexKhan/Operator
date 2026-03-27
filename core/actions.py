#
#  actions.py - Core Hub Actions Implementation
#

import mcp.types as types
from tenants.manager import TenantManager
from core.logger import HubLogger

class CoreActions:
    def __init__(self, tenant_manager: TenantManager, logger: HubLogger):
        self.tenant_manager = tenant_manager
        self.logger = logger

    def get_hub_status(self) -> list[types.TextContent]:
        active_tenants = self.tenant_manager.get_active_tenants()
        tenant_names = [t.get_name() for t in active_tenants]
        active_display = " + ".join(tenant_names) if tenant_names else "None"
        
        registered_list = ", ".join(self.tenant_manager.tenants.keys())
        res = (
            f"🚀 Hub Status: Online\n"
            f"📍 Path: {self.tenant_manager.current_path}\n"
            f"🏢 Loaded Tenants: {active_display}\n"
            f"📋 Total Registered: [{registered_list}]"
        )
        self.logger.log(f"상태 조회 결과: {active_display}", 1)
        return [types.TextContent(type="text", text=res)]

    def set_active_tenant(self, name: str) -> list[types.TextContent]:
        if self.tenant_manager.set_active_tenant(name):
            self.logger.log(f"테넌트 변경 성공: {name}", 1)
            return [types.TextContent(type="text", text=f"✅ {name} 테넌트가 성공적으로 활성화되었습니다!")]
        
        self.logger.log(f"테넌트 변경 실패 (찾을 수 없음): {name}", 1)
        return [types.TextContent(type="text", text=f"❌ '{name}' 테넌트를 찾을 수 없습니다.")]

    def sync_hub_path(self, path: str) -> list[types.TextContent]:
        self.tenant_manager.sync_path(path)
        active_name = "None"
        if t := self.tenant_manager.get_active_tenant(): active_name = t.get_name()
        
        self.logger.log(f"경로 동기화: {path} (테넌트: {active_name})", 1)
        return [types.TextContent(type="text", text=f"🔄 경로 동기화 완료: {path}\n🏢 감지된 테넌트: {active_name}")]
