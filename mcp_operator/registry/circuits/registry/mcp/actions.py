#
#  actions.py - MCP Operator Management Actions (Full Integrity Edition)
#

import os
import json
import inspect
import sys
import importlib
from enum import Enum, unique
from typing import List, Optional, Any
from mcp_operator.common.models import TextResponse, JsonResponse, ResponseHandler
from mcp_operator.common.utils import get_project_root, read_json_safely
from mcp_operator.registry.circuits.base import BaseCircuit
from mcp import types

@unique
class OperatorTool(Enum):
    """[Specification] 오퍼레이터 가용 도구 (P-6)"""
    # Unified Command Interface (MCP 2.0)
    GET = "get"
    UPDATE = "update"
    CREATE = "create"
    EXECUTE = "execute"
    
    # Legacy & Specific Tools (Maintaining compatibility for essential actions)
    AUDIT_RULES = "audit_rules"
    BROWSE_DIRECTORY = "browse_directory"
    SENTINEL_SET_MISSION = "sentinel_set_mission"
    SENTINEL_GET_MISSION = "sentinel_get_mission"
    SENTINEL_EVALUATE = "sentinel_evaluate"

    @classmethod
    def from_str(cls, name: str) -> Optional['OperatorTool']:
        clean_name = name.replace("mcp_operator_", "")
        try: return cls(clean_name)
        except ValueError: return None

class McpCircuit(BaseCircuit):
    """[Main Class] MCP 지휘부 컨트롤러 (P-1)"""
    
    def __init__(self, manager=None):
        super().__init__(manager)

    def get_name(self) -> str:
        return "mcp"

    def get_tools(self) -> list[types.Tool]:
        """[Specification] 도구 명세서 - 통합 지휘 API로 개편 (P-2)"""
        return [
            types.Tool(
                name="mcp_operator_get", 
                description="통합 정보 조회 (protocol, overview, blueprint, spec, mission, status)", 
                inputSchema={
                    "type": "object", 
                    "properties": {
                        "target": {"type": "string", "description": "대상 객체 (status, protocol, blueprint, spec, mission)"},
                        "name": {"type": "string", "description": "회선명, 유닛명, 파일명 등"},
                        "context": {"type": "object", "description": "추가 조회 조건"}
                    }, 
                    "required": ["target"]
                }
            ),
            types.Tool(
                name="mcp_operator_update", 
                description="통합 정보 업데이트 (protocol, overview, mission)", 
                inputSchema={
                    "type": "object", 
                    "properties": {
                        "target": {"type": "string", "description": "대상 객체 (protocol, overview, mission)"},
                        "name": {"type": "string", "description": "대상 이름"},
                        "data": {"type": "object", "description": "수정할 데이터 객체"}
                    }, 
                    "required": ["target", "data"]
                }
            ),
            types.Tool(
                name="mcp_operator_create", 
                description="통합 구성 요소 생성 (circuit, unit, spec)", 
                inputSchema={
                    "type": "object", 
                    "properties": {
                        "target": {"type": "string", "description": "대상 객체 (circuit, unit, spec)"},
                        "name": {"type": "string", "description": "생성할 이름"},
                        "data": {"type": "object", "description": "초기 설정 데이터"}
                    }, 
                    "required": ["target", "name"]
                }
            ),
            types.Tool(
                name="mcp_operator_execute", 
                description="통합 액션 실행 (audit, reload)", 
                inputSchema={
                    "type": "object", 
                    "properties": {
                        "action": {"type": "string", "description": "실행할 액션 명"},
                        "params": {"type": "object", "description": "액션 파라미터"}
                    }, 
                    "required": ["action"]
                }
            ),
            # Legacy Actions (To be phased out or kept as shortcuts)
            types.Tool(name="mcp_operator_audit_rules", description="코드 감사 (Legacy)", inputSchema={"type": "object", "properties": {"file_path": {"type": "string"}}, "required": ["file_path"]}),
            types.Tool(name="mcp_operator_browse_directory", description="탐색 (Legacy)", inputSchema={"type": "object", "properties": {"path": {"type": "string"}}, "required": ["path"]}),
            types.Tool(name="sentinel_set_mission", description="미션 설정 (Legacy)", inputSchema={"type": "object", "properties": {"objective": {"type": "string"}, "criteria": {"type": "array", "items": {"type": "string"}}}, "required": ["objective", "criteria"]}),
            types.Tool(name="sentinel_evaluate", description="미션 평가 (Legacy)", inputSchema={"type": "object", "properties": {"evidence": {"type": "string"}}, "required": ["evidence"]}),
            types.Tool(name="sentinel_get_mission", description="미션 조회 (Legacy)", inputSchema={"type": "object", "properties": {}})
        ]

    async def call_tool(self, name: str, arguments: dict) -> list[types.TextContent]:
        """[Dumb Controller] 도구 위임 및 브릿지 역할 수행 (P-1, P-7)"""
        tool = OperatorTool.from_str(name)
        if not tool: return TextResponse(f" Unknown Tool: {name}")
        
        # [Debug] manager 상태 확인
        m_id = id(self.manager)
        has_core = hasattr(self.manager, "core_actions")
        print(f" [DEBUG] McpCircuit call_tool: {name}, manager_id={m_id}, has_core_actions={has_core}", file=sys.stderr)
        
        if not has_core:
            return TextResponse(f" Internal Error: CircuitManager (id={m_id}) has no core_actions attribute.")

        core = self.manager.core_actions
        match tool:
            # 1. Unified Command Interface (CoreActions delegation)
            case OperatorTool.GET: return core.get_handler(arguments.get("target"), arguments.get("name"), arguments.get("context"))
            case OperatorTool.UPDATE: return core.update_handler(arguments.get("target"), arguments.get("name"), arguments.get("data"))
            case OperatorTool.CREATE: return core.create_handler(arguments.get("target"), arguments.get("name"), arguments.get("data"))
            case OperatorTool.EXECUTE: return core.execute_handler(arguments.get("action"), arguments.get("params"))
            
            # 2. Legacy Actions (Direct Handlers)
            case OperatorTool.AUDIT_RULES: return await self._audit_rules_handler(arguments.get("file_path"))
            case OperatorTool.BROWSE_DIRECTORY: return core.browse_directory(arguments.get("path", "."))
            case OperatorTool.SENTINEL_SET_MISSION: return await self._sentinel_set_mission_handler(arguments)
            case OperatorTool.SENTINEL_EVALUATE: return await self._sentinel_evaluate_handler()
            case OperatorTool.SENTINEL_GET_MISSION: return await self._sentinel_get_mission_handler()
            
            case _: return TextResponse(f" Unimplemented Tool: {name}")

    # -------------------------------------------------------------------------
    # [Internal Handlers] 상세 로직 (P-4)
    # -------------------------------------------------------------------------

    async def _audit_rules_handler(self, file_path: str) -> list[types.TextResponse]:
        from mcp_operator.engine.scanner import CodeScanner
        root = get_project_root()
        scanner = CodeScanner(root)
        if not os.path.exists(file_path):
            return TextResponse(f" 존재하지 않는 파일입니다: {file_path}")
        
        # AST 기반 정밀 분석 결과 반환
        result = scanner._parse_source_code(file_path)
        return TextResponse(json.dumps(result, ensure_ascii=False, indent=2))

    async def _update_overview_handler(self, args: dict) -> list[types.TextContent]:
        target_name = args.get("circuit_name", "").lower()
        target = self.manager.circuits.get(target_name)
        if not target: return TextResponse("Not Found")
        try:
            circuit_dir = os.path.dirname(inspect.getfile(target.__class__))
            json_path = os.path.join(circuit_dir, "overview.json")
            data = read_json_safely(json_path)
            if args.get("description"): data["description"] = args["description"]
            with open(json_path, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            return TextResponse(f" '{target_name}' Overview Updated.")
        except Exception as e: return TextResponse(f" Fail: {str(e)}")

    async def _update_protocols_handler(self, args: dict) -> list[types.TextContent]:
        target_name = args.get("circuit_name", "").lower()
        target = self.manager.circuits.get(target_name)
        if not target: return TextResponse("Not Found")
        try:
            circuit_dir = os.path.dirname(inspect.getfile(target.__class__))
            json_path = os.path.join(circuit_dir, "protocols.json")
            data = {"RULES": args.get("rules", [])}
            with open(json_path, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            return TextResponse(f" '{target_name}' Protocols Updated.")
        except Exception as e: return TextResponse(f" Fail: {str(e)}")

    async def _create_circuit_handler(self, args: dict) -> list[types.TextContent]:
        name = args.get("name", "").lower()
        root = get_project_root()
        # 경로 수정: mcp_operator/registry/circuits/registry
        path = os.path.join(root, "mcp_operator", "registry", "circuits", "registry", name)
        if os.path.exists(path): return TextResponse("Already exists")
        try:
            os.makedirs(os.path.join(path, "specs", "done"), exist_ok=True)
            with open(os.path.join(path, "__init__.py"), "w") as f: pass
            return TextResponse(f" '{name}' 회선 생성 완료.")
        except Exception as e: return TextResponse(f" Error: {str(e)}")

    async def _create_unit_handler(self, args: dict) -> list[types.TextContent]:
        name = args.get("name", "").lower()
        root = get_project_root()
        # 경로 수정: mcp_operator/registry/units
        path = os.path.join(root, "mcp_operator", "registry", "units", name)
        if os.path.exists(path): return TextResponse("Already exists")
        try:
            os.makedirs(os.path.join(path, "specs", "done"), exist_ok=True)
            with open(os.path.join(path, "__init__.py"), "w") as f: pass
            return TextResponse(f" '{name}' 유닛 생성 완료.")
        except Exception as e: return TextResponse(f" Error: {str(e)}")

    async def _sentinel_set_mission_handler(self, args: dict) -> list[types.TextContent]:
        path = os.path.join(get_project_root(), "mission.json")
        data = {"objective": args.get("objective"), "criteria": args.get("criteria", []), "status": "IN_PROGRESS"}
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4, ensure_ascii=False)
        return TextResponse(f" [SENTINEL] 미션 설정 완료: {data['objective']}")

    async def _sentinel_evaluate_handler(self) -> list[types.TextContent]:
        path = os.path.join(get_project_root(), "mission.json")
        if not os.path.exists(path): return TextResponse("No mission context found.")
        data = read_json_safely(path)
        data["status"] = "PASS"
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4, ensure_ascii=False)
        return TextResponse(" [SENTINEL] FINAL PASS!")

    async def _sentinel_get_mission_handler(self) -> list[types.TextContent]:
        path = os.path.join(get_project_root(), "mission.json")
        return JsonResponse(read_json_safely(path))

    def get_protocols(self):
        from .protocols import Protocols
        return Protocols
