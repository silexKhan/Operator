#
#  manager.py - Circuit Switching & Line Discovery (Org-based) 📞⚡️
#

import os
import sys
import importlib
import inspect
import json
from circuits.base import BaseCircuit
from typing import Optional, Dict
from core.logger import OperatorLogger

class CircuitManager:
    """
    [대장님 🎯] 모든 회선(Circuit)을 탐색하고 연결을 관리하는 중앙 교환기입니다. 📞
    """
    def __init__(self):
        self.logger = OperatorLogger("CircuitManager")
        self.circuits: Dict[str, BaseCircuit] = {}
        self.current_path: str = ""
        self.active_circuit_override: Optional[str] = None
        self.discovery_log: list[str] = []
        self.load_errors: Dict[str, str] = {}
        
        self.state_file = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "state.json")
        self._load_state()
        self._discover_circuits()

    def _discover_circuits(self):
        self.logger.log("🏢 전역 회선(Circuit) 등록소 탐색 시작", 0)
        self.circuits.clear()
        self.load_errors.clear()
        self.discovery_log.clear()
        
        base_dir = os.path.dirname(os.path.abspath(__file__))
        self.discovery_log.append(f"🔎 Root: {base_dir}")
        
        for dirpath, _, filenames in os.walk(base_dir):
            if dirpath == base_dir: continue
            
            if "actions.py" in filenames:
                rel_path = os.path.relpath(dirpath, base_dir)
                module_name = f"circuits.{rel_path.replace(os.sep, '.')}.actions"
                self.discovery_log.append(f"✅ Found line at: {rel_path} -> {module_name}")
                
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
                            self.logger.log(f"✅ 회선 연결 완료: {instance.get_name()} ({module_name})", 1)
                            found_class = True
                    
                    if not found_class:
                        self.discovery_log.append(f"⚠️ No BaseCircuit class found in {module_name}")
                        
                except Exception as e:
                    self.load_errors[module_name] = str(e)
                    self.logger.log(f"❌ 회선 로드 실패 ({module_name}): {str(e)}", 1)

    def get_active_circuit(self) -> Optional[BaseCircuit]:
        if self.active_circuit_override:
            return self.circuits.get(self.active_circuit_override)
        return None

    def set_active_circuit(self, name: str) -> bool:
        name_lower = name.lower()
        if name_lower in self.circuits:
            self.active_circuit_override = name_lower
            self._save_state()
            circuit = self.circuits[name_lower]
            self._print_circuit_context_card(circuit)
            return True
        return False

    def _print_circuit_context_card(self, circuit: BaseCircuit):
        card = self.get_circuit_context_card(circuit)
        self.logger.log(f"📞 [Circuit Connected: {circuit.get_name().upper()}] ⚡️", 0)
        print("\n" + card + "\n")

    def get_circuit_context_card(self, circuit: BaseCircuit) -> str:
        from core.protocols import GlobalProtocols
        name = circuit.get_name().upper()
        res = f"📞 [CIRCUIT CONTEXT CARD: {name}] ⚡️\n"
        res += "="*40 + "\n"
        
        # [대장님 🎯] 회선의 상속 설정(inherit_global)을 체크합니다! 🛡️⚡️
        if getattr(circuit, 'inherit_global', True):
            res += "\n🏛️ [Inherited Global Protocols]\n"
            for rule in GlobalProtocols.get_rules(): res += f"  - {rule}\n"
        else:
            res += "\n🚫 [Global Protocols Inheritance Disabled]\n"
        
        protocols_cls = circuit.get_protocols()
        if protocols_cls and hasattr(protocols_cls, "RULES"):
            res += f"\n📍 [Circuit Protocols ({name} Special)]\n"
            for rule in protocols_cls.RULES: res += f"  - {rule}\n"
        
        res += "\n🛠️ [Available Actions]\n"
        for tool in circuit.get_tools(): res += f"  - {tool.name}: {tool.description}\n"
        res += "="*40
        return res

    def _save_state(self):
        with open(self.state_file, 'w') as f:
            json.dump({"active_circuit": self.active_circuit_override, "current_path": self.current_path}, f)

    def _load_state(self):
        if os.path.exists(self.state_file):
            with open(self.state_file, 'r') as f:
                state = json.load(f)
                self.active_circuit_override = state.get("active_circuit")
                self.current_path = state.get("current_path", "")

    def sync_path(self, path: str):
        if os.path.exists(path):
            self.current_path = path
            self._save_state()
            self._discover_circuits()
