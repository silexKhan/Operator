#
#  manager.py - Circuit Switching & Line Discovery (Strict Clean Architecture)
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
    [Main Class] 모든 회선(Circuit)을 탐색하고 생명주기를 관리하는 중앙 교환기입니다. (Protocol P-1)
    """
    
    def __init__(self):
        """CircuitManager 초기화 및 자동 탐색 시작"""
        self.logger = OperatorLogger("CircuitManager")
        self.circuits: Dict[str, BaseCircuit] = {}
        self.current_path: str = ""
        self.active_circuit_override: Optional[str] = None
        self.discovery_log: List[str] = []
        self.load_errors: Dict[str, str] = {}
        
        self.state_file = os.path.join(get_project_root(), "data", "state.json")
        self._load_state_handler()
        self.discover_circuits_handler()

    # -------------------------------------------------------------------------
    # [Handlers] 공개 관리 인터페이스 (Protocol P-4)
    # -------------------------------------------------------------------------

    def create_new_circuit(self, name: str) -> bool:
        """[Handler] 새로운 회선을 물리적으로 생성하고 기본 템플릿을 배치합니다."""
        name_lower = name.lower().strip()
        if not name_lower or name_lower in self.circuits:
            return False
            
        target_dir = os.path.join(get_project_root(), "mcp_operator", "registry", "circuits", "registry", name_lower)
        if os.path.exists(target_dir):
            return False
            
        try:
            os.makedirs(target_dir, exist_ok=True)
            
            # 1. actions.py (기본 템플릿)
            with open(os.path.join(target_dir, "actions.py"), "w", encoding="utf-8") as f:
                f.write(f"from mcp_operator.registry.circuits.base import BaseCircuit\n\nclass {name.capitalize()}Circuit(BaseCircuit):\n    def get_name(self) -> str:\n        return \"{name_lower}\"\n")
            
            # 2. overview.json
            write_json_safely(os.path.join(target_dir, "overview.json"), {
                "name": name_lower, "description": f"{name_lower} 회선입니다.", "units": []
            })
            
            # 3. protocols.json
            write_json_safely(os.path.join(target_dir, "protocols.json"), {"RULES": []})
            
            self.logger.log(f" 새로운 회선 생성 완료: {name_lower}", 1)
            self.discover_circuits_handler() # 재탐색
            return True
        except Exception as e:
            self.logger.log(f" 회선 생성 실패: {str(e)}", 2)
            return False

    def delete_circuit(self, name: str) -> bool:
        """[Handler] 특정 회선의 물리적 디렉토리를 제거하고 메모리에서 해제합니다."""
        name_lower = name.lower().strip()
        if name_lower not in self.circuits:
            return False
            
        # 보안: registry 하위만 삭제 가능하도록 검증
        target_dir = os.path.join(get_project_root(), "mcp_operator", "registry", "circuits", "registry", name_lower)
        if not os.path.exists(target_dir):
            return False
            
        try:
            shutil.rmtree(target_dir)
            if self.active_circuit_override == name_lower:
                self.active_circuit_override = "mcp" # 기본값으로 복구
                self._save_state_handler()
                
            self.logger.log(f" 회선 물리적 삭제 완료: {name_lower}", 1)
            self.discover_circuits_handler() # 상태 갱신
            return True
        except Exception as e:
            self.logger.log(f" 회선 삭제 실패: {str(e)}", 2)
            return False

    def create_new_unit(self, name: str) -> bool:
        """[Handler] 새로운 기술 유닛을 물리적으로 생성하고 기본 템플릿을 배치합니다."""
        name_lower = name.lower().strip()
        target_dir = os.path.join(get_project_root(), "mcp_operator", "registry", "units", name_lower)
        if os.path.exists(target_dir):
            return False
            
        try:
            os.makedirs(target_dir, exist_ok=True)
            
            # 1. auditor.py (기본 템플릿)
            with open(os.path.join(target_dir, "auditor.py"), "w", encoding="utf-8") as f:
                f.write(f"class {name.capitalize()}Auditor:\n    def audit(self, file_path: str, content: str) -> list[str]:\n        return []\n")
            
            # 2. protocols.json
            write_json_safely(os.path.join(target_dir, "protocols.json"), {
                "OVERVIEW": f"{name_lower} 유닛의 미션입니다.", "RULES": []
            })
            
            self.logger.log(f" 새로운 유닛 생성 완료: {name_lower}", 1)
            return True
        except Exception as e:
            self.logger.log(f" 유닛 생성 실패: {str(e)}", 2)
            return False

    def delete_unit(self, name: str) -> bool:
        """[Handler] 특정 유닛의 물리적 디렉토리를 제거합니다."""
        name_lower = name.lower().strip()
        target_dir = os.path.join(get_project_root(), "mcp_operator", "registry", "units", name_lower)
        if not os.path.exists(target_dir):
            return False
            
        try:
            # 의존성 확인 로그 (경고)
            for c_name, circuit in self.circuits.items():
                if name_lower in getattr(circuit, "units", []):
                    self.logger.log(f" 경고: 유닛 '{name_lower}'은(는) 회선 '{c_name}'에서 사용 중입니다.", 2)

            shutil.rmtree(target_dir)
            self.logger.log(f" 유닛 물리적 삭제 완료: {name_lower}", 1)
            return True
        except Exception as e:
            self.logger.log(f" 유닛 삭제 실패: {str(e)}", 2)
            return False

    def discover_circuits_handler(self):
        """[Handler] 전역 회선 등록소를 초기화하고 물리적 파일 스캔을 통해 회선을 재탐색합니다."""
        self.logger.log(" 전역 회선(Circuit) 등록소 탐색 시작", 0)
        self.circuits.clear()
        self.load_errors.clear()
        self.discovery_log.clear()
        
        base_dir = os.path.dirname(os.path.abspath(__file__))
        self._scan_circuits_recursive(base_dir)

    def get_active_circuit(self) -> Optional[BaseCircuit]:
        """[Handler] 현재 활성화된 회선 객체를 반환합니다."""
        if self.active_circuit_override:
            return self.circuits.get(self.active_circuit_override)
        return None

    def set_active_circuit_handler(self, name: str) -> bool:
        """[Handler] 특정 회선으로 통신 스위치를 전환하고 상태를 저장합니다."""
        name_lower = name.lower()
        if name_lower in self.circuits:
            self.active_circuit_override = name_lower
            self._save_state_handler()
            return True
        return False

    def sync_path_handler(self, path: str):
        """[Handler] 작업 경로를 동기화하고 변경 시 회선을 재탐색합니다."""
        if os.path.exists(path) and self.current_path != path:
            self.current_path = path
            self._save_state_handler()
            self.discover_circuits_handler()

    def get_circuit_context_card_handler(self, circuit: BaseCircuit) -> str:
        """[Handler] 회선의 모든 규약 및 행동 정보를 시각화된 텍스트 카드로 조합합니다."""
        name = circuit.get_name().upper()
        res = f" [CIRCUIT CONTEXT CARD: {name}] \n" + "="*40 + "\n"
        
        res += self._build_global_protocols_section(circuit)
        res += self._build_circuit_special_protocols_section(circuit, name)
        res += self._build_technology_units_section(circuit)
        res += self._build_available_actions_section(circuit)
        
        return res + "="*40

    # -------------------------------------------------------------------------
    # [Internal Helpers] 상세 구현 로직 (Protocol P-4)
    # -------------------------------------------------------------------------

    def _scan_circuits_recursive(self, base_dir: str):
        """디렉토리를 순회하며 actions.py를 포함한 회선 패키지를 탐색합니다."""
        for dirpath, dirnames, filenames in os.walk(base_dir):
            # [사용자] 대규모 디렉토리는 탐색에서 즉시 제외하여 CPU 점유율을 방어합니다. (G-0)
            skip_dirs = ['node_modules', '.next', '.venv', '.git', '__pycache__']
            dirnames[:] = [d for d in dirnames if d not in skip_dirs]
            
            if dirpath == base_dir: continue
            if "actions.py" in filenames:
                self._load_circuit_module(base_dir, dirpath)

    def _load_circuit_module(self, base_dir: str, dirpath: str):
        """발견된 디렉토리로부터 회선 모듈을 임포트하고 인스턴스화합니다."""
        # [사용자] registry 하위 경로를 안전하게 추출합니다.
        rel_path = os.path.relpath(dirpath, base_dir)
        path_parts = rel_path.replace(os.sep, '.').strip('.')
        
        # [사용자] 정규화된 풀 패키지 경로를 사용하여 구식 'circuits' 임포트를 원천 차단합니다.
        module_name = f"mcp_operator.registry.circuits.{path_parts}.actions"
        
        try:
            module = importlib.reload(sys.modules[module_name]) if module_name in sys.modules else importlib.import_module(module_name)
            self._extract_circuit_classes(module, module_name)
        except Exception as e:
            self.load_errors[module_name] = str(e)
            self.logger.log(f" 회선 로드 실패 ({module_name}): {str(e)}", 1)

    def _extract_circuit_classes(self, module: Any, module_name: str):
        """모듈 내의 BaseCircuit 구현체를 찾아 circuits 맵에 등록합니다."""
        for _, obj in inspect.getmembers(module):
            if inspect.isclass(obj) and issubclass(obj, BaseCircuit) and obj is not BaseCircuit:
                instance = obj(self)
                key = instance.get_name().lower()
                self.circuits[key] = instance
                self.logger.log(f" 회선 연결 완료: {instance.get_name()} ({module_name})", 1)

    def _build_global_protocols_section(self, circuit: BaseCircuit) -> str:
        """전사 공통 규약 섹션을 빌드합니다."""
        if not getattr(circuit, 'inherit_global', True): return ""
        from mcp_operator.engine.protocols import GlobalProtocols
        res = "\n [Inherited Global Protocols]\n"
        for rule in GlobalProtocols.get_rules(): res += f"  - {rule}\n"
        return res

    def _build_circuit_special_protocols_section(self, circuit: BaseCircuit, name: str) -> str:
        """회선 전용 규약 섹션을 빌드합니다."""
        circuit_dir = os.path.dirname(inspect.getfile(circuit.__class__))
        # protocols.json 또는 protocols.py 등을 유연하게 탐색 (여기선 json 우선)
        json_path = os.path.join(circuit_dir, "protocols.json")
        rules = read_json_safely(json_path).get("RULES", [])
        
        if not rules: return ""
        res = f"\n [Circuit Protocols ({name} Special)]\n"
        for rule in rules: res += f"  - {rule}\n"
        return res

    def _build_technology_units_section(self, circuit: BaseCircuit) -> str:
        """회선에 배속된 기술 유닛 규약 섹션을 빌드합니다."""
        units = getattr(circuit, "units", [])
        if not units and hasattr(circuit, "get_units"): units = circuit.get_units()
        if not units: return ""
        
        res = "\n [Active Technology Units]\n"
        project_root = get_project_root()
        for unit in list(dict.fromkeys(units)):
            res += f"  - {unit.capitalize()} Unit\n"
            res += self._load_unit_spec_text(project_root, unit)
        return res

    def _load_unit_spec_text(self, root: str, unit: str) -> str:
        """개별 유닛의 물리적 JSON에서 미션과 규약을 텍스트로 추출합니다."""
        # 경로 수정: operator/registry/units -> mcp_operator/registry/units
        json_path = os.path.join(root, "mcp_operator", "registry", "units", unit, "protocols.json")
        data = read_json_safely(json_path)
        if not data: return ""
        
        text = f"    └ Mission: {data.get('OVERVIEW', 'N/A')}\n"
        for rule in data.get("RULES", []): text += f"    └ {rule}\n"
        return text

    def _build_available_actions_section(self, circuit: BaseCircuit) -> str:
        """가용 행동(Tools) 목록 섹션을 빌드합니다."""
        res = "\n [Available Actions]\n"
        for tool in circuit.get_tools():
            res += f"  - {tool.name}: {tool.description}\n"
        return res

    def _save_state_handler(self):
        """현재 상태를 파일에 영구 저장합니다."""
        write_json_safely(self.state_file, {
            "active_circuit": self.active_circuit_override, 
            "current_path": self.current_path
        })

    def _load_state_handler(self):
        """저장된 상태를 파일에서 불러옵니다."""
        state = read_json_safely(self.state_file)
        self.active_circuit_override = state.get("active_circuit")
        raw_path = state.get("current_path", "")
        
        # [상대 경로 대응] 경로가 비어있거나 '.'일 경우 프로젝트 루트를 할당합니다.
        if not raw_path or raw_path == ".":
            self.current_path = get_project_root()
        else:
            self.current_path = raw_path
