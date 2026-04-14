#
#  actions.py - Operator Core Action Implementations (Strict Clean Architecture)
#

import os
import sys
import re
import json
import importlib
from typing import List, Optional, Any, Dict, Tuple
from mcp_operator.common.models import TextResponse, JsonResponse, CommandTarget, UnifiedRequest
from mcp_operator.common.utils import get_project_root, read_json_safely, get_i18n_text
import mcp.types as types
from mcp_operator.registry.circuits.manager import CircuitManager
from mcp_operator.engine.logger import OperatorLogger

class CoreActions:
    """
    [Main Controller] 오퍼레이터 시스템의 핵심 명령을 관리하는 지휘부입니다. (Protocol P-1)
    모든 응답은 MCP 규격(TextContent)을 준수하며, 상세 비즈니스 로직은 전용 핸들러로 위임합니다.
    """
    def __init__(self, manager: CircuitManager, logger: OperatorLogger):
        self.manager = manager
        self.logger = logger

    # -------------------------------------------------------------------------
    # [Unified Command API] MCP 2.0 통합 지휘 인터페이스 (Protocol P-7)
    # -------------------------------------------------------------------------

    def get_handler(self, target: str, name: Optional[str] = None, context: Optional[dict] = None) -> list[types.TextContent]:
        """[Handler] 모든 메타데이터 및 상태 정보를 통합 조회합니다."""
        try:
            t_enum = CommandTarget(target)
            match t_enum:
                case CommandTarget.STATUS:
                    return self.get_operator_status()
                case CommandTarget.PROTOCOL:
                    if name: return self.get_protocols_handler(name)
                    return self.get_global_protocols()
                case CommandTarget.BLUEPRINT:
                    return self.get_blueprint(name or "")
                case CommandTarget.SPEC:
                    return self.get_spec_content(name or "")
                case CommandTarget.MISSION:
                    from mcp_operator.engine.protocols import GlobalProtocols
                    gp = GlobalProtocols()
                    lang = gp.get_current_language()
                    path = os.path.join(get_project_root(), "mission.json")
                    mission = read_json_safely(path)
                    if mission:
                        mission["objective"] = get_i18n_text(mission.get("objective"), lang)
                        mission["criteria"] = get_i18n_text(mission.get("criteria"), lang)
                    return JsonResponse(mission)
                case CommandTarget.STATE:
                    path = os.path.join(get_project_root(), "data", "state.json")
                    state = read_json_safely(path) or {}
                    return JsonResponse(state)
                case _:
                    return TextResponse(f" Unsupported GET Target: {target}")
        except Exception as e:
            return TextResponse(f" GET Error: {str(e)}")

    def update_handler(self, target: str, name: Optional[str] = None, data: Optional[dict] = None) -> list[types.TextContent]:
        """[Handler] 모든 시스템 설정 및 상태를 통합 업데이트합니다."""
        if not data: return TextResponse(" Error: 'data' is required for update.")
        try:
            t_enum = CommandTarget(target)
            match t_enum:
                case CommandTarget.PROTOCOL:
                    return self._update_protocols_logic(name, data.get("rules", []))
                case CommandTarget.OVERVIEW:
                    return self._update_overview_logic(name, data)
                case CommandTarget.STATE:
                    path = os.path.join(get_project_root(), "data", "state.json")
                    state = read_json_safely(path) or {}
                    state.update(data)
                    with open(path, "w", encoding="utf-8") as f:
                        json.dump(state, f, indent=4, ensure_ascii=False)
                    return TextResponse(f" System State Updated: {json.dumps(state, ensure_ascii=False)}")
                case CommandTarget.MISSION:
                    # 미션 업데이트 로직 (Sentinel 역할)
                    path = os.path.join(get_project_root(), "mission.json")
                    mission = read_json_safely(path) or {}
                    mission.update(data)
                    with open(path, "w", encoding="utf-8") as f:
                        json.dump(mission, f, indent=4, ensure_ascii=False)
                    return TextResponse(f" Mission Updated: {mission.get('objective')}")
                case _:
                    return TextResponse(f" Unsupported UPDATE Target: {target}")
        except Exception as e:
            return TextResponse(f" UPDATE Error: {str(e)}")

    def create_handler(self, target: str, name: str, data: Optional[dict] = None) -> list[types.TextContent]:
        """[Handler] 회선, 유닛, 명세 등 신규 구성 요소를 통합 생성합니다."""
        try:
            t_enum = CommandTarget(target)
            match t_enum:
                case CommandTarget.CIRCUIT:
                    return self.create_new_circuit(name)
                case CommandTarget.UNIT:
                    return self.create_new_unit(name)
                case CommandTarget.SPEC:
                    # 명세 생성 로직 추가 가능
                    return TextResponse(f" Spec creation for '{name}' is not yet implemented.")
                case _:
                    return TextResponse(f" Unsupported CREATE Target: {target}")
        except Exception as e:
            return TextResponse(f" CREATE Error: {str(e)}")

    def execute_handler(self, action: str, params: Optional[dict] = None) -> list[types.TextContent]:
        """[Handler] 감사, 분석, 리로드 등 고부하/외부 연동 액션을 통합 실행합니다."""
        params = params or {}
        match action.lower():
            case "audit":
                # 기존 audit 로직 브릿지 (McpCircuit에서 CoreActions로 로직 이동 권장)
                return TextResponse(" Please use 'mcp_operator_audit_rules' for now.")
            case "reload":
                # 리로드 시그널 반환 (상위 서버에서 처리)
                return TextResponse(" ENGINE_RELOAD_SIGNAL_PENDING")
            case _:
                return TextResponse(f" Unknown Action: {action}")

    # -------------------------------------------------------------------------
    # [Legacy Support] 기존 호환성 유지 핸들러
    # -------------------------------------------------------------------------

    def get_operator_status(self) -> list[types.TextContent]:
        """[Handler] 시스템 전체 상태와 등록된 회선 목록을 빠르게 보고합니다."""
        active = self.manager.get_active_circuit()
        active_name = active.get_name() if active else "None"
        
        # [추가] 현재 활성 회선에 배속된 유닛 목록 추출
        active_units = active.get_units() if active else []
        
        registered = list(self.manager.circuits.keys())
        
        res = (
            f" Operator Status: Online\n"
            f" Active Circuit: {active_name}\n"
            f" Active Units: {active_units}\n"
            f" Total Registered Circuits: {registered}\n\n"
            f" [SYSTEM MESSAGE 1]: 'get_operator_status()'를 호출하여 시스템 목록을 확인하십시오.\n"
            f" [SYSTEM MESSAGE 2]: 'set_active_circuit(name=\"회선명\")'으로 통신 스위치를 전환하십시오. "
        )
        return TextResponse(res)

    def get_active_circuit_details(self) -> Optional[Dict[str, Any]]:
        """[Handler] 현재 활성화된 회선의 상세 정보를 구조화된 데이터로 반환합니다."""
        active = self.manager.get_active_circuit()
        if not active:
            return None
            
        from mcp_operator.engine.protocols import GlobalProtocols
        name = active.get_name()
        
        # 0. Mission (Current project-wide mission)
        from mcp_operator.engine.protocols import GlobalProtocols
        gp = GlobalProtocols()
        lang = gp.get_current_language()
        root = get_project_root()
        mission_path = os.path.join(root, "mission.json")
        mission_data = read_json_safely(mission_path) or {}
        
        # Apply I18N filtering
        if mission_data:
            mission_data["objective"] = get_i18n_text(mission_data.get("objective"), lang)
            mission_data["criteria"] = get_i18n_text(mission_data.get("criteria"), lang)
        
        # 1. Protocols
        protocols = []
        if getattr(active, 'inherit_global', True):
            protocols.extend(GlobalProtocols.get_rules())
        
        runtime_rules = self._get_runtime_protocols(active)
        if runtime_rules:
            protocols.extend(runtime_rules)
            
        # 2. Units
        units_data = []
        units = list(getattr(active, "units", []))
        if not units and hasattr(active, "get_units"):
            units = list(active.get_units())
            
        # [Sync] 물리적 overview.json 파일에서 유닛 목록 보강
        try:
            circuit_dir = os.path.dirname(inspect.getfile(active.__class__))
            overview_path = os.path.join(circuit_dir, "overview.json")
            if os.path.exists(overview_path):
                ov_data = read_json_safely(overview_path)
                if ov_data and "units" in ov_data:
                    units.extend(ov_data["units"])
        except: pass
            
        for unit_name in list(dict.fromkeys(units or [])):
            unit_info = {"name": unit_name, "mission": "N/A", "rules": []}
            try:
                # 1. JSON 데이터 우선 로드 (가장 안정적)
                json_path = os.path.join(root, "mcp_operator", "registry", "units", unit_name, "protocols.json")
                data = read_json_safely(json_path)
                if data:
                    unit_info["mission"] = data.get("OVERVIEW", "N/A")
                    unit_info["rules"] = data.get("RULES", [])
                
                # 2. Python 모듈이 있다면 데이터 보강 (오버라이드)
                try:
                    module_path = f"mcp_operator.registry.units.{unit_name}.protocols"
                    if module_path in sys.modules:
                        importlib.reload(sys.modules[module_path])
                    unit_module = importlib.import_module(module_path)
                    p_cls = getattr(unit_module, f"{unit_name.capitalize()}Protocols", None)
                    if p_cls:
                        # 모듈에 데이터가 있다면 JSON보다 우선함 (Hot Sync 용도)
                        p_mission = getattr(p_cls, "OVERVIEW", None)
                        if p_mission: unit_info["mission"] = p_mission
                        p_rules = p_cls.get_rules() if hasattr(p_cls, "get_rules") else getattr(p_cls, "RULES", None)
                        if p_rules: unit_info["rules"] = p_rules
                except Exception as e:
                    # 임포트 에러는 조용히 넘김 (JSON 데이터가 있으므로)
                    pass
            except Exception as e:
                print(f" [DEBUG] Error loading unit '{unit_name}': {str(e)}", file=sys.stderr)
            units_data.append(unit_info)
            
        # 3. Actions
        actions = []
        for tool in active.get_tools():
            actions.append({"name": tool.name, "description": tool.description})
            
        # 4. Audit History (Recent Security/Compliance Logs)
        from mcp_operator.common.history import history_logger
        audit_logs = []
        try:
            audit_logs = history_logger.get_recent_audits(10)
        except: pass

        return {
            "name": name,
            "mission": mission_data,
            "protocols": protocols,
            "units": units_data,
            "actions": actions,
            "audit_logs": audit_logs
        }

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
        from mcp_operator.engine.scanner import CodeScanner
        try:
            root = get_project_root()
            registered = list(self.manager.circuits.keys())
            data = CodeScanner.get_project_structure(root, registered)
            return TextResponse(json.dumps(data, ensure_ascii=False, indent=2))
        except Exception as e:
            return TextResponse(json.dumps({"error": f"JSON 구조 생성 실패: {str(e)}"}))

    def get_global_protocols(self) -> list[types.TextContent]:
        """[Handler] 전사 공통 지배 규약 정보를 반환합니다."""
        import importlib
        from mcp_operator.engine import protocols
        importlib.reload(protocols)
        GlobalProtocols = protocols.GlobalProtocols

        try:
            # 인스턴스를 생성하여 현재 언어 설정(state.json)을 반영
            gp = GlobalProtocols()
            rules = gp.get_rules()
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
        from mcp_operator.engine.scanner import CodeScanner
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

    def get_protocols_handler(self, name: str) -> list[types.TextContent]:
        """[Dumb Controller] 특정 회선 또는 유닛의 규약(Protocols) 정보를 통합 조회합니다."""
        try:
            name_lower = name.strip().lower()
            
            # 1. 회선(Circuit) 조회
            if name_lower in self.manager.circuits:
                rules = self._get_runtime_protocols(self.manager.circuits[name_lower])
                if rules:
                    return TextResponse(json.dumps({
                        "type": "circuit",
                        "name": name,
                        "source": "runtime",
                        "protocols": rules
                    }, ensure_ascii=False, indent=2))

            # 2. 유닛(Unit) 조회
            root = get_project_root()
            unit_path = os.path.join(root, "mcp_operator", "registry", "units", name_lower)
            if os.path.exists(unit_path):
                # _load_unit_mission_and_rules 헬퍼 활용 (텍스트 형태)
                unit_info_text = self._load_unit_mission_and_rules(name_lower)
                if unit_info_text:
                    return TextResponse(f" [Unit Protocols: {name.capitalize()}]\n{unit_info_text}")
                
                # JSON 직접 파싱 (구조화 데이터 형태)
                json_path = os.path.join(unit_path, "protocols.json")
                if os.path.exists(json_path):
                    data = read_json_safely(json_path)
                    return TextResponse(json.dumps({
                        "type": "unit",
                        "name": name,
                        "overview": data.get("OVERVIEW", ""),
                        "protocols": data.get("RULES", [])
                    }, ensure_ascii=False, indent=2))

            # 3. 파일 시스템 회선 조회 (Fallback)
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

    def get_audit_history(self, limit: int = 10) -> list[types.TextContent]:
        """[Handler] 시스템에 기록된 최근 감사 이력(위반 내역)을 조회합니다."""
        from mcp_operator.common.history import history_logger
        try:
            logs = history_logger.get_recent_audits(limit)
            if not logs:
                return TextResponse(" 기록된 감사 이력이 없습니다. 시스템이 안전하게 유지되고 있습니다.")
            return TextResponse(json.dumps({"audit_logs": logs}, ensure_ascii=False, indent=2))
        except Exception as e:
            return TextResponse(json.dumps({"error": f"감사 이력 조회 실패: {str(e)}"}))



    def get_spec_content(self, spec_file: str) -> list[types.TextContent]:
        """[Handler] 특정 명세 파일의 내용을 조회합니다."""
        root = get_project_root()
        content = self._find_spec_content(root, spec_file)
        if content:
            return TextResponse(content)
        return TextResponse(f" Spec not found: {spec_file}")

    # -------------------------------------------------------------------------
    # [Internal Helpers] 상세 구현 (Swift의 Extension 역할 - Protocol P-4)
    # -------------------------------------------------------------------------

    def _update_protocols_logic(self, name: str, rules: List[str]) -> list[types.TextContent]:
        """[Internal] 회선 규약을 물리적으로 업데이트합니다."""
        root = get_project_root()
        target_path = self._resolve_circuit_path(root, name)
        if not target_path: return TextResponse(f" Circuit '{name}' Not Found.")
        
        try:
            json_path = os.path.join(target_path, "protocols.json")
            data = {"RULES": rules}
            with open(json_path, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            return TextResponse(f" '{name}' Protocols Updated.")
        except Exception as e: return TextResponse(f" Update Fail: {str(e)}")

    def _update_overview_logic(self, name: str, data: dict) -> list[types.TextContent]:
        """[Internal] 회선 개요를 물리적으로 업데이트합니다."""
        root = get_project_root()
        target_path = self._resolve_circuit_path(root, name)
        if not target_path: return TextResponse(f" Circuit '{name}' Not Found.")
        
        try:
            json_path = os.path.join(target_path, "overview.json")
            existing = read_json_safely(json_path) or {}
            existing.update(data)
            with open(json_path, "w", encoding="utf-8") as f:
                json.dump(existing, f, indent=2, ensure_ascii=False)
            return TextResponse(f" '{name}' Overview Updated.")
        except Exception as e: return TextResponse(f" Update Fail: {str(e)}")

    def _build_circuit_context_card(self, circuit: Any) -> str:
        """[Internal] 활성화된 회선의 규약, 유닛, 가용 행동을 조합하여 컨텍스트 카드를 생성합니다."""
        from mcp_operator.engine.protocols import GlobalProtocols
        c_name = circuit.get_name().upper()
        card = f" [CIRCUIT CONTEXT CARD: {c_name}] \n" + "="*40 + "\n"
        
        # 1. Global Protocols
        if getattr(circuit, 'inherit_global', True):
            card += "\n [Inherited Global Protocols]\n"
            for rule in GlobalProtocols.get_rules(): card += f"  - {rule}\n"
        
        # 2. Circuit Special Protocols
        # 런타임 객체(protocols.py) 또는 JSON 데이터를 로드합니다.
        rules = self._get_runtime_protocols(circuit)
        if rules:
            card += f"\n [Circuit Protocols ({c_name} Special)]\n"
            for rule in rules: card += f"  - {rule}\n"
        
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
        """[Internal] 개별 유닛의 물리적 설정에서 미션과 규약을 추출합니다."""
        try:
            # 우선순위: 1. Python 모듈(protocols.py) -> 2. JSON(protocols.json)
            module_path = f"mcp_operator.registry.units.{unit}.protocols"
            unit_module = importlib.reload(sys.modules[module_path]) if module_path in sys.modules else importlib.import_module(module_path)
            p_cls = getattr(unit_module, f"{unit.capitalize()}Protocols", None)
            
            line = ""
            if p_cls:
                # 인스턴스 생성 시도 (프로퍼티 접근을 위해)
                instance = p_cls()
                if hasattr(instance, "OVERVIEW"):
                    overview = getattr(instance, "OVERVIEW")
                    line += f"    └ Mission: {overview}\n"
                
                if hasattr(p_cls, "get_rules"):
                    for rule in p_cls.get_rules(): line += f"    └ {rule}\n"
                return line
            
            # JSON Fallback
            root = get_project_root()
            json_path = os.path.join(root, "mcp_operator", "registry", "units", unit, "protocols.json")
            data = read_json_safely(json_path)
            if data:
                line += f"    └ Mission: {data.get('OVERVIEW', 'N/A')}\n"
                for rule in data.get("RULES", []): line += f"    └ {rule}\n"
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
        """[Internal] 평탄화된 경로에서 회선 디렉토리를 탐색합니다."""
        # 경로 수정: mcp_operator/registry/circuits/registry 하위 탐색
        base = os.path.join(root, "mcp_operator", "registry", "circuits", "registry")
        candidates = [
            os.path.join(base, name.lower()),
            *[os.path.join(base, cat, name.lower()) for cat in ["development", "design", "planning"]]
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
        # 1. 루트 mcp_operator/registry/ 내의 모든 specs/ 탐색
        base_search = os.path.join(root, "mcp_operator", "registry")
        for root_dir, dirs, _ in os.walk(base_search):
            if "specs" in dirs:
                p = os.path.join(root_dir, "specs", spec_file)
                if os.path.exists(p):
                    with open(p, "r", encoding="utf-8") as f: return f.read()
        return ""

    def _get_master_blueprint(self, scanner: Any, root: str) -> Dict:
        """[Internal] MCP 시스템 전체의 구조 지도를 생성합니다."""
        return scanner.get_project_structure(root, list(self.manager.circuits.keys()))
