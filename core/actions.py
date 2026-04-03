#
#  actions.py - Operator Core Action Implementations (Strict Clean Architecture)
#

import os
import sys
import re
import json
import importlib
from typing import List, Optional, Any, Dict, Tuple
from shared.models import TextResponse, JsonResponse
from shared.utils import get_project_root, read_json_safely
import mcp.types as types
from circuits.manager import CircuitManager
from core.logger import OperatorLogger

class CoreActions:
    """
    [Main Controller] 오퍼레이터 시스템의 핵심 명령을 관리하는 지휘부입니다. (Protocol P-1)
    모든 응답은 MCP 규격(TextContent)을 준수하며, 상세 비즈니스 로직은 전용 핸들러로 위임합니다.
    """
    def __init__(self, manager: CircuitManager, logger: OperatorLogger):
        self.manager = manager
        self.logger = logger

    def get_operator_status(self) -> list[types.TextContent]:
        """[Handler] 시스템 전체 상태와 등록된 회선 목록을 빠르게 보고합니다."""
        active = self.manager.get_active_circuit()
        active_name = active.get_name() if active else "None"
        
        current_path = getattr(self.manager, "current_path", "Unknown")
        registered = list(self.manager.circuits.keys())
        
        res = (
            f" Operator Status: Online\n"
            f" Path: {current_path}\n"
            f" Active Circuit: {active_name}\n"
            f" Total Registered: {registered}\n\n"
            f" [SYSTEM MESSAGE 1]: 'get_operator_status()'를 호출하여 시스템 목록을 확인하십시오.\n"
            f" [SYSTEM MESSAGE 2]: 'set_active_circuit(name=\"회선명\")'으로 통신 스위치를 전환하십시오. "
        )
        return TextResponse(res)

    def set_active_circuit(self, name: str) -> list[types.TextContent]:
        """
        [Dumb Controller] 특정 회선에 정식으로 연결을 시도하고 지휘소 카드를 생성합니다.
        """
        if not name:
            return TextResponse(" 연결할 회선 이름을 입력해 주세요.")
        
        name_lower = name.lower()
        if name_lower not in self.manager.circuits:
            return TextResponse(f" '{name}' 회선을 찾을 수 없습니다. 등록된 회선을 확인해 주세요.")

        # 상태 갱신 및 저장
        self.manager.active_circuit_override = name_lower
        if hasattr(self.manager, "_save_state"):
            self.manager._save_state()
        
        # 지휘소 카드 조립 (상세 로직 위임)
        circuit = self.manager.circuits[name_lower]
        context_card = self._build_circuit_context_card(circuit)
        
        final_res = f" {name} 회선이 성공적으로 연결되었습니다!\n\n" + context_card
        return TextResponse(final_res)

    def sync_operator_path(self, path: str) -> list[types.TextContent]:
        """[Handler] 작업 경로를 동기화하고 주변 회선을 자동 감지합니다."""
        if not os.path.exists(path):
            return TextResponse(f" 존재하지 않는 경로입니다: {path}")
            
        self.manager.sync_path(path)
        res = (
            f" 경로 동기화 완료: {path}\n"
            f" 새로운 회선들을 감지했습니다: {list(self.manager.circuits.keys())}"
        )
        return TextResponse(res)

    def get_full_json_structure(self) -> list[types.TextContent]:
        """[Handler] 전체 프로젝트 구조를 분석하여 웹 UI용 JSON 지도를 생성합니다."""
        from core.scanner import CodeScanner
        try:
            root = get_project_root()
            registered = list(self.manager.circuits.keys())
            data = CodeScanner.get_project_structure(root, registered)
            return TextResponse(json.dumps(data, ensure_ascii=False, indent=2))
        except Exception as e:
            return TextResponse(json.dumps({"error": f"JSON 구조 생성 실패: {str(e)}"}))

    def get_global_protocols(self) -> list[types.TextContent]:
        """[Handler] 전사 공통 지배 규약 정보를 반환합니다."""
        from core.protocols import GlobalProtocols
        try:
            rules = GlobalProtocols.get_rules()
            return TextResponse(json.dumps(rules, ensure_ascii=False))
        except Exception as e:
            return TextResponse(json.dumps({"error": str(e)}))

    def browse_directory(self, path: str) -> list[types.TextContent]:
        """[Handler] 특정 경로의 파일 및 폴더 목록을 필터링하여 조회합니다."""
        try:
            if not os.path.exists(path):
                return TextResponse(json.dumps({"error": f"Path not found: {path}"}))
            
            folders = [d for d in os.listdir(path) if os.path.isdir(os.path.join(path, d)) and not d.startswith(".")]
            files = [f for f in os.listdir(path) if os.path.isfile(os.path.join(path, f)) and not f.startswith(".")]
            
            return TextResponse(json.dumps({
                "current": path, "folders": folders, "files": files
            }, ensure_ascii=False))
        except Exception as e:
            return TextResponse(json.dumps({"error": str(e)}))

    def get_blueprint(self, domain: str = "") -> list[types.TextContent]:
        """[Dumb Controller] 현재 활성화된 회선 혹은 특정 도메인의 설계도를 반환합니다."""
        from core.scanner import CodeScanner
        try:
            root = get_project_root()
            scanner = CodeScanner(root)
            
            if domain and domain.lower() != 'mcp':
                data = self._get_domain_specific_blueprint(root, domain)
            else:
                data = self._get_master_blueprint(scanner, root)
                
            return TextResponse(json.dumps(data, ensure_ascii=False, indent=2))
        except Exception as e:
            return TextResponse(json.dumps({"error": str(e)}))

    def get_circuit_protocols(self, name: str) -> list[types.TextContent]:
        """[Dumb Controller] 특정 회선의 규약(Protocols) 정보를 런타임 또는 파일에서 로드합니다."""
        try:
            name_lower = name.strip().lower()
            
            # 1. 런타임 매니저에서 우선 조회
            if name_lower in self.manager.circuits:
                rules = self._get_runtime_protocols(self.manager.circuits[name_lower])
                if rules:
                    return TextResponse(json.dumps({"name": name, "source": "runtime", "protocols": rules}, ensure_ascii=False, indent=2))

            # 2. 파일 시스템 기반 조회 (Fallback)
            return self._get_filesystem_protocols(name_lower)
        except Exception as e:
            return TextResponse(json.dumps({"error": str(e)}))

    def create_new_circuit(self, name: str) -> list[types.TextContent]:
        """[Handler] 새로운 회선을 물리적으로 생성하고 기본 템플릿을 배치합니다."""
        success = self.manager.create_new_circuit(name)
        if success:
            return TextResponse(f" 새로운 회선 '{name}'이(가) 성공적으로 생성 및 등록되었습니다.")
        return TextResponse(f" 회선 '{name}' 생성에 실패했습니다. 이미 존재하거나 권한 오류일 수 있습니다.")

    def delete_circuit(self, name: str) -> list[types.TextContent]:
        """[Handler] 특정 회선의 물리적 디렉토리를 제거하고 메모리에서 해제합니다."""
        success = self.manager.delete_circuit(name)
        if success:
            return TextResponse(f" 회선 '{name}' 및 관련 데이터가 물리적으로 삭제되었습니다.")
        return TextResponse(f" 회선 '{name}' 삭제에 실패했습니다. 이름이 정확한지 확인하십시오.")

    def create_new_unit(self, name: str) -> list[types.TextContent]:
        """[Handler] 새로운 기술 유닛을 물리적으로 생성하고 기본 템플릿을 배치합니다."""
        success = self.manager.create_new_unit(name)
        if success:
            return TextResponse(f" 새로운 유닛 '{name}'이(가) 성공적으로 생성되었습니다.")
        return TextResponse(f" 유닛 '{name}' 생성에 실패했습니다.")

    def delete_unit(self, name: str) -> list[types.TextContent]:
        """[Handler] 특정 유닛의 물리적 디렉토리를 제거합니다."""
        success = self.manager.delete_unit(name)
        if success:
            return TextResponse(f" 유닛 '{name}'이(가) 물리적으로 삭제되었습니다.")
        return TextResponse(f" 유닛 '{name}' 삭제에 실패했습니다.")


    # -------------------------------------------------------------------------
    # [Internal Helpers] 상세 구현 (Swift의 Extension 역할 - Protocol P-4)
    # -------------------------------------------------------------------------

    def _build_circuit_context_card(self, circuit: Any) -> str:
        """[Internal] 활성화된 회선의 규약, 유닛, 가용 행동을 조합하여 컨텍스트 카드를 생성합니다."""
        from core.protocols import GlobalProtocols
        c_name = circuit.get_name().upper()
        card = f" [CIRCUIT CONTEXT CARD: {c_name}] \n" + "="*40 + "\n"
        
        # 1. Global Protocols
        if getattr(circuit, 'inherit_global', True):
            card += "\n [Inherited Global Protocols]\n"
            for rule in GlobalProtocols.get_rules(): card += f"  - {rule}\n"
        
        # 2. Circuit Special Protocols
        p_cls = circuit.get_protocols()
        if p_cls and hasattr(p_cls, "get_rules"):
            card += f"\n [Circuit Protocols ({c_name} Special)]\n"
            for rule in p_cls.get_rules(): card += f"  - {rule}\n"
        
        # 3. Active Technology Units
        card += self._build_units_section(circuit)
        
        # 4. Available Actions
        card += "\n [Available Actions]\n"
        for tool in circuit.get_tools(): card += f"  - {tool.name}: {tool.description}\n"
        return card + "="*40

    def _build_units_section(self, circuit: Any) -> str:
        """[Internal] 회선에 배속된 전문 기술 유닛 목록과 개별 규약을 로드합니다."""
        units = getattr(circuit, "units", [])
        if not units and hasattr(circuit, "get_units"): units = circuit.get_units()
        if not units: return ""
        
        res = "\n [Active Technology Units]\n"
        for unit in list(dict.fromkeys(units)): # 중복 제거
            res += f"  - {unit.capitalize()} Unit\n"
            res += self._load_unit_mission_and_rules(unit)
        return res

    def _load_unit_mission_and_rules(self, unit: str) -> str:
        """[Internal] 개별 유닛의 protocols.py를 동적 리로드하여 최신 규약을 추출합니다."""
        try:
            module_path = f"units.{unit}.protocols"
            unit_module = importlib.reload(sys.modules[module_path]) if module_path in sys.modules else importlib.import_module(module_path)
            p_cls = getattr(unit_module, f"{unit.capitalize()}Protocols", None)
            
            line = ""
            if p_cls:
                if hasattr(p_cls, "OVERVIEW"): line += f"    └ Mission: {p_cls.OVERVIEW}\n"
                if hasattr(p_cls, "get_rules"):
                    for rule in p_cls.get_rules(): line += f"    └ {rule}\n"
            return line
        except: return ""

    def _get_domain_specific_blueprint(self, root: str, domain: str) -> Dict:
        """[Internal] 특정 도메인(회선)의 메타데이터 및 구조를 분석합니다."""
        target_path = self._resolve_circuit_path(root, domain)
        if not target_path: return {"error": "Domain not found"}
        
        # JSON 또는 PY 우선순위에 따른 메타데이터 추출
        json_path = os.path.join(target_path, "overview.json")
        py_path = os.path.join(target_path, "overview.py")
        
        if os.path.exists(json_path):
            return read_json_safely(json_path)
        elif os.path.exists(py_path):
            return self._parse_overview_py(py_path, domain, target_path)
        return {"name": domain, "path": target_path}

    def _resolve_circuit_path(self, root: str, name: str) -> Optional[str]:
        """[Internal] 평탄화된 경로 및 카테고리화된 경로에서 회선 디렉토리를 탐색합니다."""
        candidates = [
            os.path.join(root, "circuits", "registry", name.lower()),
            *[os.path.join(root, "circuits", "registry", cat, name.lower()) for cat in ["development", "design", "planning"]]
        ]
        for p in candidates:
            if os.path.exists(p): return p
        return None

    def _parse_overview_py(self, path: str, domain: str, abs_path: str) -> Dict:
        """[Internal] overview.py 파일에서 상수를 파싱하여 정보를 추출합니다."""
        try:
            with open(path, "r", encoding="utf-8") as f:
                content = f.read()
                def find(key):
                    m = re.search(f"{key}\\s*=\\s*[\"'](.*?)[\"']", content)
                    if not m:
                        m = re.search(f"{key}\\s*=\\s*\\[(.*?)\\]", content, re.DOTALL)
                        return [v.strip().strip("'\"") for v in m.group(1).split(",") if v.strip()] if m else []
                    return m.group(1)
                return {
                    "name": find("NAME") or domain, "description": find("DESCRIPTION") or "",
                    "path": abs_path, "dependencies": find("DEPENDENCIES"), "units": find("UNITS")
                }
        except: return {"name": domain, "path": abs_path}

    def _get_runtime_protocols(self, circuit: Any) -> List[str]:
        """[Internal] 런타임 객체로부터 규약 리스트를 추출합니다."""
        p_cls = circuit.get_protocols()
        if not p_cls: return []
        return p_cls.get_rules() if hasattr(p_cls, "get_rules") else getattr(p_cls, "RULES", [])

    def _get_filesystem_protocols(self, name: str) -> list[types.TextContent]:
        """[Internal] 물리적 파일 시스템에서 규약 정보를 로드합니다."""
        root = get_project_root()
        target_path = self._resolve_circuit_path(root, name)
        
        if not target_path:
            return TextResponse(json.dumps({"error": f"Circuit '{name}' not found."}))
            
        overview = read_json_safely(os.path.join(target_path, "overview.json"))
        protocols = read_json_safely(os.path.join(target_path, "protocols.json"))
        return TextResponse(json.dumps({
            "name": name, "source": "file", "overview": overview, "protocols": protocols.get("RULES", [])
        }, ensure_ascii=False, indent=2))

    def _find_spec_content(self, root: str, spec_file: str) -> str:
        """[Internal] 전체 프로젝트 트리에서 특정 스펙 파일을 Surgical하게 탐색합니다."""
        # 1. 루트 specs/ 우선 탐색
        root_spec = os.path.join(root, "specs", spec_file)
        if os.path.exists(root_spec):
            with open(root_spec, "r", encoding="utf-8") as f: return f.read()
            
        # 2. 모든 회선 폴더 specs/ 탐색
        for root_dir, dirs, _ in os.walk(os.path.join(root, "circuits")):
            if "specs" in dirs:
                p = os.path.join(root_dir, "specs", spec_file)
                if os.path.exists(p):
                    with open(p, "r", encoding="utf-8") as f: return f.read()
        return ""

    def _get_master_blueprint(self, scanner: Any, root: str) -> Dict:
        """[Internal] MCP 시스템 전체의 구조 지도를 생성합니다."""
        return scanner.get_project_structure(root, list(self.manager.circuits.keys()))
