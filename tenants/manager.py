#
#  manager.py - Tenant Management & Discovery
#

import os
from tenants.base import BaseTenant
from typing import Optional
from core.logger import HubLogger

class TenantManager:
    def __init__(self):
        self.logger = HubLogger("TenantManager")
        self.tenants = {}
        self.active_tenant_override = None
        self.current_path = os.getcwd()
        self._discover_tenants()

    def _discover_tenants(self):
        self.logger.log("테넌트 검색 시작", 0)
        # [대장님 🎯] 추후 동적 로딩 구현 예정. 일단 수동 등록.
        try:
            from tenants.gdr.actions import GDRTenant
            gdr = GDRTenant()
            self.tenants[gdr.get_name().lower()] = gdr
            self.logger.log(f"테넌트 등록 완료: {gdr.get_name()}", 1)
        except Exception as e:
            self.logger.log(f"테넌트 등록 실패: {str(e)}", 1)

    def set_active_tenant(self, name: str) -> bool:
        """수동으로 테넌트를 강제 활성화합니다."""
        name_lower = name.lower()
        if name_lower in self.tenants:
            self.active_tenant_override = name_lower
            self.logger.log(f"테넌트 강제 활성화: {name_lower}", 0)
            return True
        self.logger.log(f"활성화 실패 (알 수 없는 테넌트): {name}", 0)
        return False

    def sync_path(self, path: str):
        """외부(Gemini CLI)의 현재 경로와 동기화합니다."""
        if os.path.exists(path):
            self.current_path = path
            self.logger.log(f"작업 경로 동기화: {path}", 0)
        else:
            self.logger.log(f"경로 동기화 실패 (존재하지 않음): {path}", 0)

    def get_active_tenant(self, path: Optional[str] = None) -> Optional[BaseTenant]:
        # 1. 수동 설정(Override)이 있으면 최우선 반환
        if self.active_tenant_override:
            return self.tenants.get(self.active_tenant_override)

        # 2. 경로 기반 자동 감지
        target_path = (path or self.current_path).upper()
        
        # [대장님 🎯] 경로에 GDR이 포함되어 있으면 즉시 GDR 테넌트를 깨웁니다!
        if "/GDR" in target_path or target_path.endswith("/GDR"):
            return self.tenants.get("gdr")
            
        return None
