#
#  manager.py - Circuit Switching & Line Discovery (Org-based) 
#

import os
import sys
import importlib
import inspect
from circuits.base import BaseCircuit
from typing import Optional, Dict
from core.logger import OperatorLogger
from shared.utils import get_project_root, read_json_safely, write_json_safely

class CircuitManager:
    """
    [사용자] 모든 회선(Circuit)을 탐색하고 연결을 관리하는 중앙 교환기입니다. 
    """
    def __init__(self):
        self.logger = OperatorLogger("CircuitManager")
        self.circuits: Dict[str, BaseCircuit] = {}
        self.current_path: str = ""
        self.active_circuit_override: Optional[str] = None
        self.discovery_log: list[str] = []
        self.load_errors: Dict[str, str] = {}
        
        self.state_file = os.path.join(get_project_root(), "state.json")
        self._load_state()
        self._discover_circuits()

    def _discover_circuits(self):
        self.logger.log(" 전역 회선(Circuit) 등록소 탐색 시작", 0)
        self.circuits.clear()
        self.load_errors.clear()
        self.discovery_log.clear()
        
        base_dir = os.path.dirname(os.path.abspath(__file__))
        self.discovery_log.append(f" Root: {base_dir}")
        
        for dirpath, _, filenames in os.walk(base_dir):
            if dirpath == base_dir: continue
            
            if "actions.py" in filenames:
                rel_path = os.path.relpath(dirpath, base_dir)
                module_name = f"circuits.{rel_path.replace(os.sep, '.')}.actions"
                self.discovery_log.append(f" Found line at: {rel_path} -> {module_name}")
                
                try:
                    if module_name in sys.modules:
                        module = importlib.reload(sys.modules[module_name])
                    else:
                        module = importlib.import_module(module_name)
                    
                    found_class = False
                    for name, obj in inspect.getmembers(module):
                        if inspect.isclass(obj) and issubclass(obj, BaseCircuit) and obj is not BaseCircuit:
                            instance = obj(self)
                            key = instance.get_name().lower()
                            self.circuits[key] = instance
                            self.logger.log(f" 회선 연결 완료: {instance.get_name()} ({module_name})", 1)
                            found_class = True
                    
                    if not found_class:
                        self.discovery_log.append(f" No BaseCircuit class found in {module_name}")
                        
                except Exception as e:
                    self.load_errors[module_name] = str(e)
                    self.logger.log(f" 회선 로드 실패 ({module_name}): {str(e)}", 1)

    def get_active_circuit(self) -> Optional[BaseCircuit]:
        if self.active_circuit_override:
            return self.circuits.get(self.active_circuit_override)
        return None

    def set_active_circuit(self, name: str) -> bool:
        name_lower = name.lower()
        if name_lower in self.circuits:
            self.active_circuit_override = name_lower
            self._save_state()
            return True
        return False

    def _print_circuit_context_card(self, circuit: BaseCircuit):
        card = self.get_circuit_context_card(circuit)
        self.logger.log(f" [Circuit Connected: {circuit.get_name().upper()}] ", 0)
        print("\n" + card + "\n")

    def get_circuit_context_card(self, circuit: BaseCircuit) -> str:
        from core.protocols import GlobalProtocols
        name = circuit.get_name().upper()
        res = f" [CIRCUIT CONTEXT CARD: {name}] \n"
        res += "="*40 + "\n"
        
        # 1. Global Protocols (실시간 JSON 로드)
        if getattr(circuit, 'inherit_global', True):
            res += "\n [Inherited Global Protocols]\n"
            for rule in GlobalProtocols.get_rules(): res += f"  - {rule}\n"
        
        # 2. Circuit Special Protocols (실시간 JSON 로드) 📂✨
        circuit_dir = os.path.dirname(inspect.getfile(circuit.__class__))
        json_path = os.path.join(circuit_dir, "protocols.json")
        rules = read_json_safely(json_path).get("RULES", [])
        
        if rules:
            res += f"\n [Circuit Protocols ({name} Special)]\n"
            for rule in rules: res += f"  - {rule}\n"
        
        # 3. Active Technology Units (실시간 JSON 로드) 📂✨
        units = getattr(circuit, "units", [])
        if not units and hasattr(circuit, "get_units"): units = circuit.get_units()
            
        if units:
            unique_units = []
            for u in units:
                if u not in unique_units: unique_units.append(u)
            
            res += "\n [Active Technology Units]\n"
            base_dir = get_project_root()
            for unit in unique_units:
                res += f"  - {unit.capitalize()} Unit\n"
                json_path = os.path.join(base_dir, "units", unit, "protocols.json")
                data = read_json_safely(json_path)
                if data:
                    if "OVERVIEW" in data:
                        res += f"    └ Mission: {data['OVERVIEW']}\n"
                    for rule in data.get("RULES", []):
                        res += f"    └ {rule}\n"

        # 4. Available Actions
        res += "\n [Available Actions]\n"
        for tool in circuit.get_tools(): res += f"  - {tool.name}: {tool.description}\n"
        res += "="*40
        return res

    def _save_state(self):
        write_json_safely(self.state_file, {"active_circuit": self.active_circuit_override, "current_path": self.current_path})

    def _load_state(self):
        state = read_json_safely(self.state_file)
        self.active_circuit_override = state.get("active_circuit")
        self.current_path = state.get("current_path", "")

    def sync_path(self, path: str):
        if os.path.exists(path):
            self.current_path = path
            self._save_state()
            self._discover_circuits()
