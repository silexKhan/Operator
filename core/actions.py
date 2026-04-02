#
#  actions.py - Operator Core Action Implementations 
#

import os
import sys
import importlib
from shared.models import TextResponse, JsonResponse
import mcp.types as types
from circuits.manager import CircuitManager
from core.logger import OperatorLogger

class CoreActions:
    """
    [사용자] 오퍼레이터 시스템의 핵심 명령을 수행하며, 모든 응답은 MCP 규격(TextContent)을 준수합니다. 
    """
    def __init__(self, manager: CircuitManager, logger: OperatorLogger):
        self.manager = manager
        self.logger = logger

    def get_operator_status(self) -> list[types.TextContent]:
        """[사용자] 시스템의 상태를 빠르게 보고합니다."""
        active = self.manager.get_active_circuit()
        active_name = active.get_name() if active else "None"
        
        current_path = getattr(self.manager, "current_path", "Unknown")
        registered = list(self.manager.circuits.keys())
        
        res = (
            f" Operator Status: Online\n"
            f" Path: {current_path}\n"
            f" Active Circuit: {active_name}\n"
            f" Total Registered: {registered}\n\n"
            f" [SYSTEM MESSAGE 1]: 'set_active_circuit(name=\"회선명\")'으로 세션을 확정하십시오.\n"
            f" [SYSTEM MESSAGE 2]: 작업 시작 전 사용할 유닛과 규약을 복명복창하십시오. "
        )
        return TextResponse(res)

    def set_active_circuit(self, name: str) -> list[types.TextContent]:
        """[사용자] 특정 회선에 정식으로 연결을 시도합니다."""
        if not name:
            return TextResponse(" 연결할 회선 이름을 입력해 주세요.")
        
        name_lower = name.lower()
        if name_lower in self.manager.circuits:
            # [사용자] 매니저의 예전 set_active_circuit 로직(중복 출력)을 우회합니다! 
            self.manager.active_circuit_override = name_lower
            if hasattr(self.manager, "_save_state"):
                self.manager._save_state()
            
            circuit = self.manager.circuits[name_lower]
            from core.protocols import GlobalProtocols
            
            # [사용자] 카드를 여기서 단일하게 조립하여 중복 문제를 종결합니다. 
            c_name = circuit.get_name().upper()
            res_card = f" [CIRCUIT CONTEXT CARD: {c_name}] \n"
            res_card += "="*40 + "\n"
            
            # 1. Global Protocols
            if getattr(circuit, 'inherit_global', True):
                res_card += "\n [Inherited Global Protocols]\n"
                self.logger.log(f"DEBUG: PROJECT_ROOT={GlobalProtocols.PROJECT_ROOT}", 0)
                rules = GlobalProtocols.get_rules()
                self.logger.log(f"DEBUG: Rules count={len(rules)}", 0)
                for rule in rules: res_card += f"  - {rule}\n"
            
            # 2. Circuit Special Protocols
            p_cls = circuit.get_protocols()
            if p_cls and hasattr(p_cls, "RULES"):
                res_card += f"\n [Circuit Protocols ({c_name} Special)]\n"
                for rule in p_cls.RULES: res_card += f"  - {rule}\n"
            
            # 3. Active Technology Units 
            units = getattr(circuit, "units", [])
            if not units and hasattr(circuit, "get_units"): units = circuit.get_units()
                
            if units:
                # [사용자] 런타임 리로드 시 발생할 수 있는 유닛 목록 중복을 물리적으로 제거합니다! 
                unique_units = []
                for u in units:
                    if u not in unique_units: unique_units.append(u)
                
                res_card += "\n [Active Technology Units]\n"
                for unit in unique_units:
                    res_card += f"  - {unit.capitalize()} Unit\n"
                    try:
                        module_path = f"units.{unit}.protocols"
                        # [사용자] 파일 수정 사항을 런타임에 즉시 반영하기 위해 강제 리로드합니다! 
                        if module_path in sys.modules:
                            unit_module = importlib.reload(sys.modules[module_path])
                        else:
                            unit_module = importlib.import_module(module_path)
                            
                        class_name = f"{unit.capitalize()}Protocols"
                        if hasattr(unit_module, class_name):
                            unit_p_cls = getattr(unit_module, class_name)
                            # [사용자] 유닛의 정체성(OVERVIEW)이 있다면 'Mission'으로 출력하여 강제성을 높입니다! 
                            if hasattr(unit_p_cls, "OVERVIEW"):
                                res_card += f"    └ Mission: {unit_p_cls.OVERVIEW}\n"
                            
                            if hasattr(unit_p_cls, "get_rules"):
                                for rule in unit_p_cls.get_rules():
                                    res_card += f"    └ {rule}\n"
                    except Exception as e:
                        self.logger.log(f" 유닛 로드 실패 ({unit}): {str(e)}", 1)
                        pass
            
            # 4. Available Actions
            res_card += "\n [Available Actions]\n"
            for tool in circuit.get_tools(): res_card += f"  - {tool.name}: {tool.description}\n"
            res_card += "="*40
            
            final_res = f" {name} 회선이 성공적으로 연결되었습니다!\n\n" + res_card
            return TextResponse(final_res)
        else:
            return TextResponse(f" '{name}' 회선을 찾을 수 없습니다. 등록된 회선을 확인해 주세요.")

    def sync_operator_path(self, path: str) -> list[types.TextContent]:
        """[사용자] 작업 경로를 동기화하고 주변 회선을 자동 탐색합니다."""
        if not os.path.exists(path):
            return TextResponse(f" 존재하지 않는 경로입니다: {path}")
            
        self.manager.sync_path(path)
        res = (
            f" 경로 동기화 완료: {path}\n"
            f" 새로운 회선들을 감지했습니다: {list(self.manager.circuits.keys())}"
        )
        return TextResponse(res)

    def get_full_json_structure(self) -> list[types.TextContent]:
        """[사용자] 전체 프로젝트 구조를 분석하여 JSON 형태로 반환합니다 (웹 UI 브릿지 전용) """
        from core.scanner import CodeScanner
        from shared.utils import get_project_root
        import json
        
        try:
            root = get_project_root()
            registered = list(self.manager.circuits.keys())
            data = CodeScanner.get_project_structure(root, registered)
            
            # [사용자] MCP 규격에 맞게 JSON 문자열로 변환하여 텍스트로 보냅니다! 
            return TextResponse(json.dumps(data, ensure_ascii=False, indent=2))
        except Exception as e:
            return TextResponse(json.dumps({"error": f"JSON 구조 생성 실패: {str(e)}"}))

    def get_global_protocols(self) -> list[types.TextContent]:
        """[사용자] 전사 공통 규약 정보를 반환합니다."""
        import json
        from core.protocols import GlobalProtocols
        try:
            rules = GlobalProtocols.get_rules()
            return TextResponse(json.dumps(rules, ensure_ascii=False))
        except Exception as e:
            return TextResponse(json.dumps({"error": str(e)}))

    def browse_directory(self, path: str) -> list[types.TextContent]:
        """[사용자] 특정 경로의 파일 및 폴더 목록을 조회합니다."""
        import json
        try:
            if not os.path.exists(path):
                return TextResponse(json.dumps({"error": f"Path not found: {path}"}))
            
            folders = [d for d in os.listdir(path) if os.path.isdir(os.path.join(path, d)) and not d.startswith(".")]
            files = [f for f in os.listdir(path) if os.path.isfile(os.path.join(path, f)) and not f.startswith(".")]
            
            return TextResponse(json.dumps({
                "current": path,
                "folders": folders,
                "files": files
            }, ensure_ascii=False))
        except Exception as e:
            return TextResponse(json.dumps({"error": str(e)}))

    def get_blueprint(self, domain: str = "") -> list[types.TextContent]:
        """[사용자] 현재 활성화된 회선 혹은 특정 도메인의 설계도를 반환합니다."""
        from core.scanner import CodeScanner
        from shared.utils import get_project_root, read_json_safely
        import json
        
        try:
            root = get_project_root()
            scanner = CodeScanner(root)
            
            # 특정 도메인(회선) 정보가 있으면 해당 경로를 스캔
            if domain and domain.lower() != 'mcp':
                target_rel = f"circuits/registry/{domain}"
                target_abs = os.path.join(root, target_rel)
                if not os.path.exists(target_abs):
                    for cat in ["development", "design", "planning"]:
                        p = os.path.join(root, "circuits", "registry", cat, domain.lower())
                        if os.path.exists(p):
                            target_abs = p
                            target_rel = os.path.relpath(p, root)
                            break
                
                # [사용자] overview.json 또는 overview.py 중 존재하는 곳에서 정보를 추출합니다.
                json_path = os.path.join(target_abs, "overview.json")
                py_path = os.path.join(target_abs, "overview.py")
                
                name, description, path, deps, units = domain, "", target_abs, [], []
                
                if os.path.exists(json_path):
                    overview = read_json_safely(json_path)
                    name = overview.get("name", domain)
                    description = overview.get("description", "")
                    deps = overview.get("dependencies", [])
                    units = overview.get("units", [])
                elif os.path.exists(py_path):
                    # overview.py에서 정보 추출 (상수 매핑)
                    try:
                        with open(py_path, "r", encoding="utf-8") as f:
                            content = f.read()
                            import re
                            def find_val(key, text):
                                match = re.search(f"{key}\\s*=\\s*[\"'](.*?)[\"']", text)
                                if not match:
                                    match = re.search(f"{key}\\s*=\\s*\\[(.*?)\\]", text, re.DOTALL)
                                    if match:
                                        vals = [v.strip().strip("'\"") for v in match.group(1).split(",") if v.strip()]
                                        return vals
                                return match.group(1) if match else None

                            name = find_val("NAME", content) or domain
                            description = find_val("DESCRIPTION", content) or ""
                            units = find_val("UNITS", content) or []
                            deps = find_val("DEPENDENCIES", content) or []
                    except: pass

                data = {
                    "name": name,
                    "description": description,
                    "path": target_abs,
                    "dependencies": deps,
                    "units": units
                }
            else:
                # MCP 루트 또는 전체 구조
                data = scanner.get_project_structure(root, list(self.manager.circuits.keys()))
                if domain.lower() == 'mcp':
                    # MCP 전용 브리핑 형식
                    data = {
                        "name": "Operator (Master)",
                        "description": "MCP 시스템의 중앙 지휘소입니다.",
                        "path": root,
                        "dependencies": [],
                        "units": ["python", "markdown", "sentinel"]
                    }
                
            return TextResponse(json.dumps(data, ensure_ascii=False, indent=2))
        except Exception as e:
            return TextResponse(json.dumps({"error": str(e)}))

    def get_circuit_protocols(self, name: str) -> list[types.TextContent]:
        """[사용자] 특정 회선의 규약(Protocols) 정보를 반환합니다."""
        import json
        from shared.utils import read_json_safely, get_project_root
        
        try:
            root = get_project_root()
            target_path = ""
            for cat in ["development", "design", "planning"]:
                p = os.path.join(root, "circuits", "registry", cat, name.lower())
                if os.path.exists(p):
                    target_path = p
                    break
            
            if not target_path:
                return TextResponse(json.dumps({"error": f"Circuit '{name}' not found."}))
                
            overview = read_json_safely(os.path.join(target_path, "overview.json"))
            protocols = read_json_safely(os.path.join(target_path, "protocols.json"))
            
            return TextResponse(json.dumps({
                "name": name,
                "overview": overview,
                "protocols": protocols.get("RULES", [])
            }, ensure_ascii=False, indent=2))
        except Exception as e:
            return TextResponse(json.dumps({"error": str(e)}))

    def get_spec_content(self, spec_file: str) -> list[types.TextContent]:
        """[사용자] 특정 스펙 파일의 내용을 읽어옵니다."""
        import json
        from shared.utils import get_project_root
        
        try:
            root = get_project_root()
            # 스펙 파일은 보통 회선 폴더 내 specs/ 에 위치함
            # 우선 루트의 specs/ 검색 후 실패 시 전체 스캔
            search_paths = [os.path.join(root, "specs", spec_file)]
            
            content = ""
            for p in search_paths:
                if os.path.exists(p):
                    with open(p, "r", encoding="utf-8") as f:
                        content = f.read()
                        break
            
            if not content:
                # 모든 회선 폴더를 뒤져서 해당 스펙 찾기
                for root_dir, dirs, files in os.walk(os.path.join(root, "circuits")):
                    if "specs" in dirs and spec_file in os.listdir(os.path.join(root_dir, "specs")):
                        with open(os.path.join(root_dir, "specs", spec_file), "r", encoding="utf-8") as f:
                            content = f.read()
                            break
                    if content: break

            return TextResponse(json.dumps({"file": spec_file, "content": content}, ensure_ascii=False))
        except Exception as e:
            return TextResponse(json.dumps({"error": str(e)}))
