#
#  manager.py - Circuit Switching & Line Discovery (Unified 2.0)
#

import os
import sys
import importlib
import inspect
import shutil
from typing import Optional, Dict, List, Any
from mcp_operator.registry.circuits.base import BaseCircuit
from mcp_operator.engine.logger import OperatorLogger
from mcp_operator.common.utils import get_project_root, read_json_safely, write_json_safely

class CircuitManager:
    """
    [Main Class] 모든 회선(Circuit)을 탐색하고 생명주기를 관리하는 중앙 교환기입니다.
    """
    
    def __init__(self) -> None:
        """CircuitManager 초기화 및 자동 탐색 시작"""
        self.logger: OperatorLogger = OperatorLogger("CircuitManager")
        self.circuits: Dict[str, BaseCircuit] = {}
        self.current_path: str = ""
        self.active_circuit_override: Optional[str] = None
        self.discovery_log: List[str] = []
        self.load_errors: Dict[str, str] = {}
        self.core_actions: Optional[Any] = None # 서버에서 주입
        
        self.state_file: str = os.path.join(get_project_root(), "data", "state.json")
        self._load_state_handler()
        self.discover_circuits_handler()

    def discover_circuits_handler(self) -> None:
        """[Handler] 전역 회선 등록소를 초기화하고 파일 스캔을 통해 회선을 재탐색합니다."""
        self.logger.log(" 전역 회선(Circuit) 등록소 탐색 시작", 0)
        self.circuits.clear()
        self.load_errors.clear()
        
        base_dir: str = os.path.dirname(os.path.abspath(__file__))
        registry_dir: str = os.path.join(base_dir, "registry")
        self._scan_circuits_recursive(registry_dir)

    def get_active_circuit(self) -> Optional[BaseCircuit]:
        """현재 활성화된 회선 객체를 반환합니다.
        
        Returns:
            Optional[BaseCircuit]: 활성 회선 객체 또는 None.
        """
        if self.active_circuit_override:
            return self.circuits.get(self.active_circuit_override)
        return None

    def set_active_circuit_handler(self, name: str) -> bool:
        """특정 회선으로 통신 스위치를 전환합니다.
        
        Args:
            name (str): 전환할 회선 이름.
            
        Returns:
            bool: 성공 여부.
        """
        name_lower = name.lower()
        if name_lower in self.circuits:
            self.active_circuit_override = name_lower
            self._save_state_handler()
            return True
        return False

    def sync_path_handler(self, path: str) -> None:
        """작업 경로를 동기화하고 변경 시 회선을 재탐색합니다.
        
        Args:
            path (str): 동기화할 경로.
        """
        if os.path.exists(path) and self.current_path != path:
            self.current_path = path
            self._save_state_handler()
            self.discover_circuits_handler()

    def create_new_circuit(self, name: str) -> bool:
        """새로운 회선을 물리적으로 생성합니다.
        
        Args:
            name (str): 생성할 회선 이름.
            
        Returns:
            bool: 성공 여부.
        """
        name_lower = name.lower().strip()
        target_dir = os.path.join(get_project_root(), "mcp_operator", "registry", "circuits", "registry", name_lower)
        if os.path.exists(target_dir): return False
        try:
            os.makedirs(target_dir, exist_ok=True)
            write_json_safely(os.path.join(target_dir, "overview.json"), {"name": name_lower})
            write_json_safely(os.path.join(target_dir, "protocols.json"), {"RULES": []})
            self.discover_circuits_handler()
            return True
        except: return False

    def create_new_unit(self, name: str) -> bool:
        """새로운 유닛을 물리적으로 생성합니다."""
        name_lower = name.lower().strip()
        target_dir = os.path.join(get_project_root(), "mcp_operator", "registry", "units", name_lower)
        if os.path.exists(target_dir): return False
        try:
            os.makedirs(target_dir, exist_ok=True)
            write_json_safely(os.path.join(target_dir, "protocols.json"), {"RULES": []})
            return True
        except: return False

    def delete_circuit(self, name: str) -> bool:
        """회선을 물리적으로 삭제합니다."""
        name_lower = name.lower().strip()
        target_dir = os.path.join(get_project_root(), "mcp_operator", "registry", "circuits", "registry", name_lower)
        if not os.path.exists(target_dir): return False
        try:
            shutil.rmtree(target_dir)
            self.discover_circuits_handler()
            return True
        except: return False

    # -------------------------------------------------------------------------
    # [Internal Helpers] (Protocol P-4)
    # -------------------------------------------------------------------------

    def _scan_circuits_recursive(self, base_dir: str) -> None:
        """디렉토리를 순회하며 규약 정의(JSON) 또는 구현체(Python)를 탐색합니다."""
        for dirpath, dirnames, filenames in os.walk(base_dir):
            skip_dirs = ['node_modules', '.next', '.venv', '.git', '__pycache__']
            dirnames[:] = [d for d in dirnames if d not in skip_dirs]
            if dirpath == base_dir: continue
            
            if "actions.py" in filenames:
                self._load_circuit_module(base_dir, dirpath)
            elif "protocols.json" in filenames or "overview.json" in filenames:
                self._load_default_component(base_dir, dirpath, is_circuit=True)

    def _load_default_component(self, base_dir: str, dirpath: str, is_circuit: bool = True) -> None:
        """커스텀 구현이 없는 경우 베이스 클래스 기반의 기본 객체를 생성합니다."""
        name = os.path.basename(dirpath)
        try:
            if is_circuit:
                instance = BaseCircuit(self)
                instance.get_name = lambda name=name: name
                instance.get_path = lambda dirpath=dirpath: dirpath
                self.circuits[name.lower()] = instance
                self.logger.log(f" 기본 회선 연결: {name}", 1)
        except Exception as e:
            self.logger.log(f" 기본 객체 생성 실패 ({name}): {str(e)}", 1)

    def _load_circuit_module(self, base_dir: str, dirpath: str) -> None:
        """발견된 디렉토리로부터 회선 모듈을 임포트하고 인스턴스화합니다."""
        rel_path = os.path.relpath(dirpath, base_dir)
        path_parts = rel_path.replace(os.sep, '.').strip('.')
        module_name = f"mcp_operator.registry.circuits.registry.{path_parts}.actions"
        
        try:
            module = importlib.import_module(module_name)
            importlib.reload(module)
            for _, obj in inspect.getmembers(module):
                if inspect.isclass(obj) and issubclass(obj, BaseCircuit) and obj is not BaseCircuit:
                    instance = obj(self)
                    instance.get_path = lambda dirpath=dirpath: dirpath
                    self.circuits[instance.get_name().lower()] = instance
                    self.logger.log(f" 커스텀 회선 연결: {instance.get_name()}", 1)
        except Exception as e:
            self.logger.log(f" 회선 로드 실패 ({module_name}): {str(e)}", 1)

    def _save_state_handler(self) -> None:
        """현재 매니저 상태를 파일에 저장합니다."""
        existing = read_json_safely(self.state_file) or {}
        state = {
            "active_circuit": self.active_circuit_override,
            "current_path": self.current_path,
            "lang": existing.get("lang", "ko")
        }
        os.makedirs(os.path.dirname(self.state_file), exist_ok=True)
        write_json_safely(self.state_file, state)

    def _load_state_handler(self) -> None:
        """저장된 상태를 로드합니다."""
        state = read_json_safely(self.state_file)
        if state:
            self.active_circuit_override = state.get("active_circuit") or state.get("active_circuit_override")
            self.current_path = state.get("current_path", "")
