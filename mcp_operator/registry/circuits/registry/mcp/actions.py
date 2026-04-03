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
    AUDIT_RULES = "audit_rules"
    GET_OVERVIEW = "get_overview"
    GET_GLOBAL_PROTOCOLS = "get_global_protocols"
    BROWSE_DIRECTORY = "browse_directory"
    GET_BLUEPRINT = "get_blueprint"
    GET_SPEC_CONTENT = "get_spec_content"
    UPDATE_CIRCUIT_PROTOCOLS = "update_circuit_protocols"
    UPDATE_CIRCUIT_OVERVIEW = "update_circuit_overview"
    GET_CIRCUIT_PROTOCOLS = "get_circuit_protocols"
    GET_FULL_JSON_STRUCTURE = "get_full_json_structure"
    CREATE_NEW_CIRCUIT = "create_new_circuit"
    CREATE_NEW_UNIT = "create_new_unit"
    DELETE_CIRCUIT = "delete_circuit"
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
        """[Specification] 도구 명세서 - 모든 객체에 properties 필수 명시 (P-2)"""
        return [
            types.Tool(name="mcp_operator_audit_rules", description="코드 감사", inputSchema={"type": "object", "properties": {"file_path": {"type": "string"}}, "required": ["file_path"]}),
            types.Tool(name="mcp_operator_get_overview", description="회선 개요", inputSchema={"type": "object", "properties": {}}),
            types.Tool(name="mcp_operator_get_global_protocols", description="전사 규약", inputSchema={"type": "object", "properties": {}}),
            types.Tool(name="mcp_operator_browse_directory", description="탐색", inputSchema={"type": "object", "properties": {"path": {"type": "string"}}, "required": ["path"]}),
            types.Tool(name="mcp_operator_get_blueprint", description="설계도", inputSchema={"type": "object", "properties": {"domain": {"type": "string"}}}),
            types.Tool(name="mcp_operator_get_spec_content", description="스펙 로드", inputSchema={"type": "object", "properties": {"spec_file": {"type": "string"}}, "required": ["spec_file"]}),
            types.Tool(name="mcp_operator_update_circuit_protocols", description="규약 수정", inputSchema={"type": "object", "properties": {"circuit_name": {"type": "string"}, "rules": {"type": "array", "items": {"type": "string"}}}, "required": ["circuit_name", "rules"]}),
            types.Tool(name="mcp_operator_get_circuit_protocols", description="회선 규약 로드", inputSchema={"type": "object", "properties": {"circuit_name": {"type": "string"}}, "required": ["circuit_name"]}),
            types.Tool(name="mcp_operator_get_full_json_structure", description="전체 구조", inputSchema={"type": "object", "properties": {}}),
            types.Tool(name="mcp_operator_create_new_circuit", description="회선 생성", inputSchema={"type": "object", "properties": {"name": {"type": "string"}}, "required": ["name"]}),
            types.Tool(name="mcp_operator_create_new_unit", description="유닛 생성", inputSchema={"type": "object", "properties": {"name": {"type": "string"}}, "required": ["name"]}),
            types.Tool(name="sentinel_set_mission", description="미션 설정", inputSchema={"type": "object", "properties": {"objective": {"type": "string"}, "criteria": {"type": "array", "items": {"type": "string"}}}, "required": ["objective", "criteria"]}),
            types.Tool(name="sentinel_evaluate", description="미션 평가", inputSchema={"type": "object", "properties": {"evidence": {"type": "string"}}, "required": ["evidence"]}),
            types.Tool(name="sentinel_get_mission", description="미션 조회", inputSchema={"type": "object", "properties": {}})
        ]

    async def call_tool(self, name: str, arguments: dict) -> list[types.TextContent]:
        """[Dumb Controller] 도구 위임 및 브릿지 역할 수행 (P-1, P-7)"""
        tool = OperatorTool.from_str(name)
        if not tool: return TextResponse(f" Unknown Tool: {name}")
        
        # 1. McpCircuit 직접 처리 도구
        match tool:
            case OperatorTool.AUDIT_RULES: return await self._audit_rules_handler(arguments.get("file_path"))
            case OperatorTool.GET_OVERVIEW: return TextResponse("MCP Operator System Active.")
            case OperatorTool.UPDATE_CIRCUIT_OVERVIEW: return await self._update_overview_handler(arguments)
            case OperatorTool.UPDATE_CIRCUIT_PROTOCOLS: return await self._update_protocols_handler(arguments)
            case OperatorTool.CREATE_NEW_CIRCUIT: return await self._create_circuit_handler(arguments)
            case OperatorTool.CREATE_NEW_UNIT: return await self._create_unit_handler(arguments)
            case OperatorTool.SENTINEL_SET_MISSION: return await self._sentinel_set_mission_handler(arguments)
            case OperatorTool.SENTINEL_EVALUATE: return await self._sentinel_evaluate_handler()
            case OperatorTool.SENTINEL_GET_MISSION: return await self._sentinel_get_mission_handler()
            
            # 2. CoreActions 브릿지 처리 도구 (무결성 복구)
            case OperatorTool.GET_GLOBAL_PROTOCOLS: return self.manager.core_actions.get_global_protocols()
            case OperatorTool.BROWSE_DIRECTORY: return self.manager.core_actions.browse_directory(arguments.get("path", "."))
            case OperatorTool.GET_BLUEPRINT: return self.manager.core_actions.get_blueprint(arguments.get("domain", ""))
            case OperatorTool.GET_SPEC_CONTENT: return self.manager.core_actions.get_spec_content(arguments.get("spec_file", ""))
            case OperatorTool.GET_CIRCUIT_PROTOCOLS: return self.manager.core_actions.get_circuit_protocols(arguments.get("circuit_name", ""))
            case OperatorTool.GET_FULL_JSON_STRUCTURE: return self.manager.core_actions.get_full_json_structure()
            
            case _: return TextResponse(f" Unimplemented Tool: {name}")

    # -------------------------------------------------------------------------
    # [Internal Handlers] 상세 로직 (P-4)
    # -------------------------------------------------------------------------

    async def _audit_rules_handler(self, file_path: str) -> list[types.TextContent]:
        from core.harness import Auditor
        return Auditor.audit(file_path)

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
        path = os.path.join(root, "circuits", "registry", name)
        if os.path.exists(path): return TextResponse("Already exists")
        try:
            os.makedirs(os.path.join(path, "specs", "done"), exist_ok=True)
            with open(os.path.join(path, "__init__.py"), "w") as f: pass
            return TextResponse(f" '{name}' 회선 생성 완료.")
        except Exception as e: return TextResponse(f" Error: {str(e)}")

    async def _create_unit_handler(self, args: dict) -> list[types.TextContent]:
        name = args.get("name", "").lower()
        root = get_project_root()
        path = os.path.join(root, "units", name)
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
