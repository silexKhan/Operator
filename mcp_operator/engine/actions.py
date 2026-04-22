#
#  actions.py - MCP Operator Core Action Implementations (Unified 2.0)
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
from mcp_operator.engine.interfaces import BaseComponent, BaseAuditor

class CoreActions:
    """
    [Main Controller] MCP 2.0 통합 지휘부입니다.
    모든 명령은 다형성(Polymorphism) 기반으로 처리되며, 특정 회선/유닛에 종속되지 않습니다.
    """
    def __init__(self, manager: CircuitManager, logger: OperatorLogger) -> None:
        """CoreActions 인스턴스를 초기화합니다.
        
        Args:
            manager (CircuitManager): 회선 매니저 객체.
            logger (OperatorLogger): 로거 객체.
        """
        self.manager = manager
        self.logger = logger

    # -------------------------------------------------------------------------
    # [Unified Command API] MCP 2.0 통합 지휘 인터페이스 (Protocol P-7)
    # -------------------------------------------------------------------------

    def get_handler(self, target: str, name: Optional[str] = None, context: Optional[dict] = None) -> List[types.TextContent]:
        """[Unified API] 메타데이터 통합 조회.
        
        Args:
            target (str): 조회 대상 (overview, protocol, etc.).
            name (Optional[str]): 대상 이름.
            context (Optional[dict]): 추가 컨텍스트.
            
        Returns:
            List[types.TextContent]: MCP 응답 데이터.
        """
        try:
            t_enum = CommandTarget(target)
            match t_enum:
                case CommandTarget.STATUS:
                    return self.get_operator_status()
                case CommandTarget.OVERVIEW:
                    target_obj = self._resolve_component(name)
                    if not target_obj: return TextResponse(f" Error: '{name or 'Active'}' 대상을 찾을 수 없습니다.")
                    return JsonResponse(target_obj.load_overview())
                case CommandTarget.PROTOCOL:
                    target_obj = self._resolve_component(name)
                    if not target_obj: return self.get_global_protocols()
                    return JsonResponse({"name": target_obj.get_name(), "protocols": target_obj.load_protocols()})
                case CommandTarget.BLUEPRINT:
                    return self.get_blueprint(name or "")
                case CommandTarget.SPEC:
                    return self.get_spec_content(name or "")
                case CommandTarget.MISSION:
                    return self.get_mission_logic()
                case CommandTarget.STATE:
                    path = os.path.join(get_project_root(), "data", "state.json")
                    return JsonResponse(read_json_safely(path) or {})
                case _:
                    return TextResponse(f" Unsupported GET Target: {target}")
        except Exception as e:
            return TextResponse(f" GET Error: {str(e)}")

    def update_handler(self, target: str, name: Optional[str] = None, data: Optional[dict] = None) -> List[types.TextContent]:
        """[Unified API] 메타데이터 통합 업데이트.
        
        Args:
            target (str): 업데이트 대상.
            name (Optional[str]): 대상 이름.
            data (Optional[dict]): 수정할 데이터.
            
        Returns:
            List[types.TextContent]: 업데이트 결과.
        """
        if not data: return TextResponse(" Error: 'data' is required for update.")
        try:
            t_enum = CommandTarget(target)
            match t_enum:
                case CommandTarget.PROTOCOL:
                    return self._update_json_logic(name, "protocols.json", {"RULES": data.get("rules", [])})
                case CommandTarget.OVERVIEW:
                    return self._update_json_logic(name, "overview.json", data)
                case CommandTarget.MISSION:
                    path = os.path.join(get_project_root(), "mission.json")
                    mission = read_json_safely(path) or {}
                    mission.update(data)
                    with open(path, "w", encoding="utf-8") as f:
                        json.dump(mission, f, indent=4, ensure_ascii=False)
                    return TextResponse(f" Mission Updated: {mission.get('objective')}")
                case CommandTarget.STATE:
                    path = os.path.join(get_project_root(), "data", "state.json")
                    state = read_json_safely(path) or {}
                    state.update(data)
                    with open(path, "w", encoding="utf-8") as f:
                        json.dump(state, f, indent=4, ensure_ascii=False)
                    return TextResponse(" System State Updated.")
                case _:
                    return TextResponse(f" Unsupported UPDATE Target: {target}")
        except Exception as e:
            return TextResponse(f" UPDATE Error: {str(e)}")

    def create_handler(self, target: str, name: str, data: Optional[dict] = None) -> List[types.TextContent]:
        """[Unified API] 구성 요소 통합 생성."""
        try:
            t_enum = CommandTarget(target)
            match t_enum:
                case CommandTarget.CIRCUIT:
                    if self.manager.create_new_circuit(name): return TextResponse(f" Circuit '{name}' created.")
                case CommandTarget.UNIT:
                    if self.manager.create_new_unit(name): return TextResponse(f" Unit '{name}' created.")
            return TextResponse(f" Failed to create {target} '{name}'.")
        except Exception as e:
            return TextResponse(f" CREATE Error: {str(e)}")

    def execute_handler(self, action: str, params: Optional[dict] = None) -> List[types.TextContent]:
        """[Unified API] 고부하 액션 통합 실행."""
        params = params or {}
        match action.lower():
            case "audit":
                return self.audit_rules(params.get("file_path", "MISSION_PIPELINE"))
            case "mission":
                return self.audit_rules("MISSION_PIPELINE")
            case "reload":
                return TextResponse(" ENGINE_RELOAD_SIGNAL_PENDING")
            case _:
                return TextResponse(f" Unknown Action: {action}")

    # -------------------------------------------------------------------------
    # [Internal Helpers] 다형성 지원 로직 (Swift POP Style)
    # -------------------------------------------------------------------------

    def _resolve_component(self, name: Optional[str]) -> Optional[BaseComponent]:
        """이름 또는 현재 문맥을 바탕으로 회선/유닛 객체를 찾아 반환합니다.
        
        Args:
            name (Optional[str]): 대상 이름.
            
        Returns:
            Optional[BaseComponent]: 찾은 구성 요소 객체.
        """
        if not name:
            return self.manager.get_active_circuit()
        
        name_lower = name.lower()
        if name_lower in self.manager.circuits:
            return self.manager.circuits[name_lower]
        
        root = get_project_root()
        unit_path = os.path.join(root, "mcp_operator", "registry", "units", name_lower)
        if os.path.exists(unit_path):
            from mcp_operator.engine.interfaces import BaseUnit
            unit = BaseUnit(manager=self.manager, logger=self.logger)
            unit.get_name = lambda: name_lower
            unit.get_path = lambda: unit_path
            return unit
        return None

    def _update_json_logic(self, name: Optional[str], filename: str, data: dict) -> List[types.TextContent]:
        """JSON 파일을 물리적으로 업데이트합니다.
        
        Args:
            name (Optional[str]): 대상 이름.
            filename (str): 수정할 파일명.
            data (dict): 수정 데이터.
            
        Returns:
            List[types.TextContent]: 업데이트 결과.
        """
        target_obj = self._resolve_component(name)
        if not target_obj: return TextResponse(f" Error: '{name}' 대상을 찾을 수 없습니다.")
        
        try:
            path = os.path.join(target_obj.get_path(), filename)
            existing = read_json_safely(path) or {}
            existing.update(data)
            with open(path, "w", encoding="utf-8") as f:
                json.dump(existing, f, indent=2, ensure_ascii=False)
            return TextResponse(f" '{target_obj.get_name()}' {filename} Updated.")
        except Exception as e: return TextResponse(f" Update Fail: {str(e)}")

    def audit_rules(self, file_path: str) -> List[types.TextContent]:
        """모든 유닛의 Auditor를 동원하여 통합 감사를 수행합니다.
        
        Args:
            file_path (str): 감사 대상 파일 경로.
            
        Returns:
            List[types.TextContent]: 통합 감사 보고서.
        """
        active = self.manager.get_active_circuit()
        if not active: return TextResponse(" Error: 활성화된 회선이 없습니다.")
        
        units = active.get_units()
        combined_results = []
        
        content = ""
        if file_path != "MISSION_PIPELINE" and os.path.exists(file_path):
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()

        for unit_name in units:
            try:
                auditor = self._get_unit_auditor(unit_name)
                if auditor:
                    results = auditor.audit(file_path, content)
                    if results:
                        combined_results.append(f" [{unit_name.upper()} UNIT AUDIT]")
                        combined_results.extend([f"  - {r}" for r in results])
            except Exception as e:
                combined_results.append(f" 🚨 [{unit_name.upper()} ERROR] 감사 실패: {str(e)}")

        if not combined_results:
            return TextResponse(" ✅ [AUDIT PASS] 모든 규약을 준수하고 있습니다.")
            
        res_text = "\n".join(combined_results)
        return TextResponse(f" [INTEGRATED AUDIT REPORT]\n" + "="*40 + "\n" + res_text + "\n" + "="*40)

    def _get_unit_auditor(self, unit_name: str) -> Optional[BaseAuditor]:
        """유닛의 전용 Auditor 또는 기본 Auditor를 로드합니다.
        
        Args:
            unit_name (str): 유닛 이름.
            
        Returns:
            Optional[BaseAuditor]: 감사기 객체.
        """
        root = get_project_root()
        module_path = f"mcp_operator.registry.units.{unit_name}.auditor"
        try:
            module = importlib.import_module(module_path)
            importlib.reload(module)
            cls_name = f"{unit_name.capitalize()}Auditor"
            auditor_cls = getattr(module, cls_name, None)
            if auditor_cls:
                return auditor_cls(logger=self.logger, circuit_manager=self.manager)
        except: pass

        from mcp_operator.engine.interfaces import BaseUnit
        unit_path = os.path.join(root, "mcp_operator", "registry", "units", unit_name.lower())
        if os.path.exists(unit_path):
            unit = BaseUnit(logger=self.logger, manager=self.manager)
            unit.get_path = lambda: unit_path
            return unit
        return None

    # -------------------------------------------------------------------------
    # [Legacy & Utility]
    # -------------------------------------------------------------------------

    def get_operator_status(self) -> List[types.TextContent]:
        """시스템 상태를 보고합니다."""
        active = self.manager.get_active_circuit()
        res = (
            f" Operator Status: Online\n"
            f" Active Circuit: {active.get_name() if active else 'None'}\n"
            f" Registered: {list(self.manager.circuits.keys())}\n"
            f" [SYSTEM]: 통합 API(get, update, execute)를 사용하십시오. "
        )
        return TextResponse(res)

    def get_mission_logic(self) -> List[types.TextContent]:
        """현재 미션 정보를 조회합니다."""
        path = os.path.join(get_project_root(), "mission.json")
        return JsonResponse(read_json_safely(path) or {})

    def get_blueprint(self, domain: str = "") -> List[types.TextContent]:
        """시스템 설계도를 조회합니다."""
        from mcp_operator.engine.scanner import CodeScanner
        data = CodeScanner.get_project_structure(get_project_root(), list(self.manager.circuits.keys()))
        return JsonResponse(data)

    def get_spec_content(self, spec_file: str) -> List[types.TextContent]:
        """특정 명세 파일 내용을 조회합니다."""
        if not spec_file: return TextResponse(" Error: 'name' (spec file name) is required.")
        
        root = get_project_root()
        for root_dir, dirs, _ in os.walk(os.path.join(root, "mcp_operator", "registry")):
            if "specs" in dirs:
                p = os.path.join(root_dir, "specs", spec_file)
                if os.path.exists(p) and os.path.isfile(p):
                    with open(p, "r", encoding="utf-8") as f: return TextResponse(f.read())
        return TextResponse(f" Spec '{spec_file}' not found.")

    def get_global_protocols(self) -> List[types.TextContent]:
        """전사 글로벌 규약을 조회합니다."""
        from mcp_operator.engine.protocols import GlobalProtocols
        return JsonResponse(GlobalProtocols().get_rules())

    def browse_directory(self, path: str) -> List[types.TextContent]:
        """디렉토리를 탐색합니다."""
        if not os.path.exists(path): return TextResponse("Path not found.")
        folders = [d for d in os.listdir(path) if os.path.isdir(os.path.join(path, d)) and not d.startswith(".")]
        files = [f for f in os.listdir(path) if os.path.isfile(os.path.join(path, f)) and not f.startswith(".")]
        return JsonResponse({"current": path, "folders": folders, "files": files})

    def set_active_circuit(self, name: str) -> List[types.TextContent]:
        """활성 회선을 전환합니다."""
        if self.manager.set_active_circuit_handler(name):
            return TextResponse(f" Circuit switched to: {name}")
        return TextResponse("Circuit not found.")
