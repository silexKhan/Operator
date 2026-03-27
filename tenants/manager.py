#
#  manager.py - Advanced Multi-Tenant Discovery (Org-based)
#

import os
import importlib
import inspect
import json
from tenants.base import BaseTenant
from typing import Optional, Dict
from core.logger import HubLogger

class TenantManager:
    STATE_FILE = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "state.json")

    def __init__(self):
        self.logger = HubLogger("TenantManager")
        self.tenants: Dict[str, BaseTenant] = {}
        self.active_tenant_override: Optional[str] = None
        self.current_path = os.getcwd()
        self._discover_tenants()
        self._load_state()

    def _load_state(self):
        """저장된 상태를 로드합니다."""
        if os.path.exists(self.STATE_FILE):
            try:
                with open(self.STATE_FILE, "r") as f:
                    state = json.load(f)
                    self.active_tenant_override = state.get("active_tenant")
                    self.current_path = state.get("current_path", self.current_path)
                    self.logger.log(f"💾 상태 로드 완료: {self.active_tenant_override}", 1)
            except Exception as e:
                self.logger.log(f"⚠️ 상태 로드 실패: {str(e)}", 1)

    def _save_state(self):
        """현재 상태를 파일에 저장합니다."""
        try:
            state = {
                "active_tenant": self.active_tenant_override,
                "current_path": self.current_path
            }
            with open(self.STATE_FILE, "w") as f:
                json.dump(state, f, indent=4)
        except Exception as e:
            self.logger.log(f"⚠️ 상태 저장 실패: {str(e)}", 1)

    def _discover_tenants(self):
        self.logger.log("🏢 멀티 테넌트 검색 시작 (Organization-based)", 0)
        
        # 검색 대상 루트 디렉토리 정의
        base_dir = os.path.dirname(os.path.abspath(__file__))
        search_roots = ["projects", "libraries"]
        
        for root in search_roots:
            root_path = os.path.join(base_dir, root)
            if not os.path.exists(root_path): continue
            
            # 모든 하위 폴더를 탐색하며 actions.py가 있는지 확인
            for dirpath, _, filenames in os.walk(root_path):
                if "actions.py" in filenames:
                    # 파일 시스템 경로를 모듈 경로로 변환 (예: tenants.projects.golfzon.gdr.actions)
                    rel_path = os.path.relpath(dirpath, base_dir)
                    module_name = f"tenants.{rel_path.replace(os.sep, '.')}.actions"
                    
                    try:
                        self.logger.log(f"🔎 테넌트 모듈 로드 시도: {module_name} (Path: {dirpath})", 1)
                        module = importlib.import_module(module_name)
                        
                        # 모듈 내에서 BaseTenant를 상속받은 클래스 찾기
                        for name, obj in inspect.getmembers(module):
                            if inspect.isclass(obj) and issubclass(obj, BaseTenant) and obj is not BaseTenant:
                                tenant_instance = obj()
                                tenant_key = tenant_instance.get_name().lower()
                                self.tenants[tenant_key] = tenant_instance
                                self.logger.log(f"✅ 테넌트 등록 완료: {tenant_instance.get_name()} ({module_name})", 1)
                    except Exception as e:
                        # [대장님 🎯] 로드 실패 시 원인(에러 메시지)을 명확하게 로그로 남깁니다! 🛡️⚡️
                        import traceback
                        error_detail = traceback.format_exc()
                        self.logger.log(f"❌ 테넌트 로드 실패 ({module_name}): {str(e)}\n{error_detail}", 1)
                else:
                    # actions.py가 없는 폴더도 로그로 남겨 탐색 범위를 확인합니다.
                    if "__pycache__" not in dirpath:
                        self.logger.log(f"⚪️ 탐색 중 (No actions.py): {dirpath}", 1)

    def set_active_tenant(self, name: str) -> bool:
        """수동으로 테넌트를 강제 활성화합니다."""
        name_lower = name.lower()
        if name_lower in self.tenants:
            self.active_tenant_override = name_lower
            self._save_state()
            self.logger.log(f"🏢 테넌트 강제 활성화: {name_lower}", 0)
            return True
        self.logger.log(f"⚠️ 활성화 실패 (알 수 없는 테넌트): {name}", 0)
        return False

    def sync_path(self, path: str):
        """외부(Gemini CLI)의 현재 경로와 동기화하며 테넌트를 재검색합니다."""
        if os.path.exists(path):
            self.current_path = path
            self._save_state()
            self.logger.log(f"📍 작업 경로 동기화: {path}", 0)
            self._discover_tenants() # 재검색 실행 🚀
        else:
            self.logger.log(f"⚠️ 경로 동기화 실패 (존재하지 않음): {path}", 0)

    def get_active_tenants(self, path: Optional[str] = None) -> list[BaseTenant]:
        """현재 활성화된 메인 테넌트와 그 의존성 테넌트 리스트를 모두 반환합니다."""
        main_tenant = self.get_active_tenant(path)
        if not main_tenant:
            return []
        
        active_list = [main_tenant]
        
        # 의존성 테넌트들을 찾아 리스트에 추가 (대장님 지침 🎯)
        for dep_name in main_tenant.get_dependencies():
            if dep_tenant := self.tenants.get(dep_name.lower()):
                active_list.append(dep_tenant)
                
        return active_list

    def get_active_tenant(self, path: Optional[str] = None) -> Optional[BaseTenant]:
        # 1. 수동 설정(Override)이 있으면 최우선 반환
        if self.active_tenant_override:
            return self.tenants.get(self.active_tenant_override)

        # 2. 경로 기반 자동 감지 (대장님 스타일 🎯)
        target_path = (path or self.current_path).upper()
        
        # [대장님 🎯] 경로에 포함된 키워드로 테넌트를 지능적으로 판단
        for key, tenant in self.tenants.items():
            if f"/{key.upper()}" in target_path or target_path.endswith(f"/{key.upper()}"):
                return tenant
            
        return None
