#
#  actions.py - MCP Operator Management Actions
#

from circuits.base import BaseCircuit
import os
import json
import inspect
import sys
import importlib
from enum import Enum, unique
from shared.models import TextResponse, JsonResponse
from shared.utils import get_project_root, read_json_safely
from .blueprint import BluePrint
from mcp import types

@unique
class OperatorTool(Enum):
    """[사용자] 오퍼레이터가 수행 가능한 도구 목록을 Enum으로 정의합니다."""
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
    
    # Sentinel Harness Loop
    SENTINEL_SET_MISSION = "sentinel_set_mission"
    SENTINEL_GET_MISSION = "sentinel_get_mission"
    SENTINEL_EVALUATE = "sentinel_evaluate"

    @classmethod
    def from_str(cls, name: str):
        """도구 이름에서 접두어를 제거하고 Enum 멤버를 반환합니다."""
        clean_name = name.replace("mcp_operator_", "")
        try:
            return cls(clean_name)
        except ValueError:
            return None

class McpCircuit(BaseCircuit):
    def __init__(self, manager=None):
        super().__init__(manager)

    def get_name(self) -> str:
        return "mcp"

    def get_tools(self) -> list[types.Tool]:
        return [
            types.Tool(name="mcp_operator_audit_rules", description="소스 코드 무결성 진단", inputSchema={"type": "object", "properties": {"file_path": {"type": "string"}}, "required": ["file_path"]}),
            types.Tool(name="mcp_operator_get_overview", description="회선 요약 정보 확인", inputSchema={"type": "object", "properties": {}}),
            types.Tool(name="mcp_operator_get_global_protocols", description="전사 규약 조회", inputSchema={"type": "object", "properties": {}}),
            types.Tool(name="mcp_operator_browse_directory", description="서버 디렉토리 탐색", inputSchema={"type": "object", "properties": {"path": {"type": "string"}}}),
            types.Tool(name="mcp_operator_get_blueprint", description="정밀 설계도 및 스펙 목차 확인", inputSchema={"type": "object", "properties": {"domain": {"type": "string"}}}),
            types.Tool(name="mcp_operator_get_spec_content", description="특정 기획 문서(Spec)의 상세 내용 로드", inputSchema={"type": "object", "properties": {"spec_file": {"type": "string"}}, "required": ["spec_file"]}),
            types.Tool(name="mcp_operator_update_circuit_protocols", description="규약 리스트 수정", inputSchema={"type": "object", "properties": {"circuit_name": {"type": "string"}, "rules": {"type": "array", "items": {"type": "string"}}}, "required": ["circuit_name", "rules"]}),
            types.Tool(name="mcp_operator_update_circuit_overview", description="개요 및 경로 수정", inputSchema={"type": "object", "properties": {"circuit_name": {"type": "string"}, "description": {"type": "string"}, "project_path": {"type": "string"}, "dependencies": {"type": "array", "items": {"type": "string"}}}, "required": ["circuit_name"]}),
            types.Tool(name="mcp_operator_get_circuit_protocols", description="회선 규약 가져오기", inputSchema={"type": "object", "properties": {"circuit_name": {"type": "string"}}, "required": ["circuit_name"]}),
            types.Tool(name="mcp_operator_get_full_json_structure", description="전체 구조 반환", inputSchema={"type": "object", "properties": {}}),
            types.Tool(name="mcp_operator_create_new_circuit", description="새로운 회선 생성", inputSchema={"type": "object", "properties": {"name": {"type": "string"}, "role": {"type": "string"}}, "required": ["name"]}),
            types.Tool(name="mcp_operator_create_new_unit", description="새로운 기술 유닛 생성", inputSchema={"type": "object", "properties": {"name": {"type": "string"}}, "required": ["name"]}),
            types.Tool(name="mcp_operator_delete_circuit", description="회선 영구 삭제", inputSchema={"type": "object", "properties": {"name": {"type": "string"}}, "required": ["name"]}),
            
            # [Sentinel] 미션 제어 도구
            types.Tool(name="sentinel_set_mission", description="현재 작업의 최종 목적(Objective)과 성공 기준(Criteria)을 설정합니다.", inputSchema={"type": "object", "properties": {"objective": {"type": "string"}, "criteria": {"type": "array", "items": {"type": "string"}}}, "required": ["objective", "criteria"]}),
            types.Tool(name="sentinel_evaluate", description="현재 작업 결과물을 미션 목적과 대조하여 통과 여부를 판정합니다. 가능한 경우 검증용 테스트 명령어를 포함하세요.", inputSchema={"type": "object", "properties": {"evidence": {"type": "string"}, "test_command": {"type": "string"}}, "required": ["evidence"]}),
            types.Tool(name="sentinel_get_mission", description="현재 설정된 미션 정보를 조회합니다.", inputSchema={"type": "object", "properties": {}})
        ]

    async def call_tool(self, name: str, arguments: dict) -> list[types.TextContent]:
        # [사용자] Enum 체계를 사용하여 도구를 식별합니다. 🚀
        tool = OperatorTool.from_str(name)
        
        if tool == OperatorTool.AUDIT_RULES:
            from core.harness import Auditor
            return Auditor.audit(arguments.get("file_path"))

        elif tool == OperatorTool.GET_OVERVIEW:
            return TextResponse("MCP Operator System Active.")

        elif tool == OperatorTool.GET_BLUEPRINT:
            return JsonResponse(BluePrint.get_domain_blueprint(self.manager, arguments.get("domain", "")))

        elif tool == OperatorTool.UPDATE_CIRCUIT_OVERVIEW:
            target_name = arguments.get("circuit_name", "").lower()
            target = self.manager.circuits.get(target_name)
            if not target: return TextResponse("Not Found")
            try:
                circuit_dir = os.path.dirname(inspect.getfile(target.__class__))
                json_path = os.path.join(circuit_dir, "overview.json")
                data = read_json_safely(json_path)
                
                if arguments.get("description"): data["description"] = arguments["description"]
                if arguments.get("project_path") is not None: data["project_path"] = arguments["project_path"]
                if arguments.get("dependencies") is not None: data["dependencies"] = arguments["dependencies"]
                if arguments.get("units") is not None: data["units"] = arguments["units"]

                with open(json_path, "w", encoding="utf-8") as f:
                    json.dump(data, f, indent=2, ensure_ascii=False)
                return TextResponse(f" '{target_name}' Overview Updated.")
            except Exception as e: return TextResponse(f" Fail: {str(e)}")

        elif tool == OperatorTool.UPDATE_CIRCUIT_PROTOCOLS:
            target_name = arguments.get("circuit_name", "").lower()
            target = self.manager.circuits.get(target_name)
            if not target: return TextResponse("Not Found")
            try:
                circuit_dir = os.path.dirname(inspect.getfile(target.__class__))
                json_path = os.path.join(circuit_dir, "protocols.json")
                data = read_json_safely(json_path)
                data["RULES"] = arguments.get("rules", [])
                with open(json_path, "w", encoding="utf-8") as f:
                    json.dump(data, f, indent=2, ensure_ascii=False)
                return TextResponse(f" '{target_name}' Protocols Updated.")
            except Exception as e: return TextResponse(f" Fail: {str(e)}")

        elif tool == OperatorTool.CREATE_NEW_CIRCUIT:
            name = arguments.get("name", "").lower()
            if not name: return TextResponse("Name is required")
            try:
                root = get_project_root()
                # registry 하위로 직접 생성 (평탄화 구조 반영)
                circuit_path = os.path.join(root, "circuits", "registry", name)
                if os.path.exists(circuit_path): return TextResponse("Already exists")
                
                os.makedirs(os.path.join(circuit_path, "specs", "done"), exist_ok=True)
                overview_data = {"name": name, "description": f"New {name} circuit", "units": []}
                with open(os.path.join(circuit_path, "overview.json"), "w", encoding="utf-8") as f:
                    json.dump(overview_data, f, indent=2, ensure_ascii=False)
                
                # 최소한의 필수 파일들 생성
                with open(os.path.join(circuit_path, "__init__.py"), "w", encoding="utf-8") as f: pass
                return TextResponse(f" '{name}' 회선 및 지식 저장소 생성 완료.")
            except Exception as e: return TextResponse(f" Error: {str(e)}")

        elif tool == OperatorTool.CREATE_NEW_UNIT:
            name = arguments.get("name", "").lower()
            if not name: return TextResponse("Unit name required")
            try:
                root = get_project_root()
                unit_path = os.path.join(root, "units", name)
                if os.path.exists(unit_path): return TextResponse("Already exists")
                
                os.makedirs(os.path.join(unit_path, "specs", "done"), exist_ok=True)
                proto_data = {"OVERVIEW": f"{name} unit", "RULES": []}
                with open(os.path.join(unit_path, "protocols.json"), "w", encoding="utf-8") as f:
                    json.dump(proto_data, f, indent=2, ensure_ascii=False)
                
                open(os.path.join(unit_path, "__init__.py"), "a").close()
                return TextResponse(f" '{name}' 유닛 및 지식 저장소 생성 완료.")
            except Exception as e: return TextResponse(f" Error: {str(e)}")

        elif tool == OperatorTool.SENTINEL_SET_MISSION:
            path = os.path.join(get_project_root(), "mission.json")
            data = {"objective": arguments.get("objective"), "criteria": arguments.get("criteria", []), "status": "IN_PROGRESS", "iteration": 1}
            with open(path, "w", encoding="utf-8") as f: json.dump(data, f, indent=4, ensure_ascii=False)
            return TextResponse(f" [SENTINEL] 미션 설정 완료: {data['objective']}")

        elif tool == OperatorTool.SENTINEL_EVALUATE:
            path = os.path.join(get_project_root(), "mission.json")
            if not os.path.exists(path): return TextResponse(" [SENTINEL] No mission.")
            with open(path, "r", encoding="utf-8") as f: mission = json.load(f)
            mission["status"] = "PASS"
            with open(path, "w", encoding="utf-8") as f: json.dump(mission, f, indent=4, ensure_ascii=False)
            return TextResponse(" [SENTINEL] FINAL PASS!")

        return TextResponse(f" Unimplemented Tool: {name}")
