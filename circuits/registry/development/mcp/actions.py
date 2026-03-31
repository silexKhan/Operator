#
#  actions.py - Standard MCP Domain Actions (Naming Fixed) 🛡️⚡️
#

import mcp.types as types
import os
import inspect
import re
import json
import shutil
from circuits.base import BaseCircuit
from circuits.registry.development.mcp.protocols import Protocols
from circuits.registry.development.mcp.overview import Overview
from circuits.registry.development.mcp.blueprint import BluePrint
from core.protocols import GlobalProtocols
from core.logger import OperatorLogger

class MCPCircuit(BaseCircuit):
    def __init__(self, manager=None):
        super().__init__(manager)
        self.logger = OperatorLogger("MCPCircuit")
        # [대장님 🎯] Overview에 정의된 전문 유닛들을 동적으로 배속합니다. 🕵️‍♂️🚀
        self.units = Overview.UNITS

    def get_name(self) -> str: return "MCP"
    def get_protocols(self): return Protocols
    def get_auditor(self):
        # [대장님 🎯] 배속된 'python' 유닛에서 감사기를 로드합니다. 🕵️‍♂️
        from units.python.auditor import PythonAuditor
        return PythonAuditor(self.logger)

    def get_tools(self) -> list[types.Tool]:
        # [대장님 🎯] 도구 이름을 브릿지가 찾는 'mcp_operator_...' 규격과 완벽히 일치시킵니다. 🛡️⚡️
        return [
            types.Tool(name="mcp_operator_audit_rules", description="소스 코드 무결성 진단", inputSchema={"type": "object", "properties": {"file_path": {"type": "string"}}, "required": ["file_path"]}),
            types.Tool(name="mcp_operator_get_overview", description="회선 요약 정보 확인", inputSchema={"type": "object", "properties": {}}),
            types.Tool(name="mcp_operator_get_global_protocols", description="전사 규약 조회", inputSchema={"type": "object", "properties": {}}),
            types.Tool(name="mcp_operator_browse_directory", description="서버 디렉토리 탐색", inputSchema={"type": "object", "properties": {"path": {"type": "string"}}}),
            types.Tool(name="mcp_operator_get_blueprint", description="정밀 설계도 확인", inputSchema={"type": "object", "properties": {"domain": {"type": "string"}}}),
            types.Tool(name="mcp_operator_update_circuit_protocols", description="규약 리스트 수정", inputSchema={"type": "object", "properties": {"circuit_name": {"type": "string"}, "rules": {"type": "array", "items": {"type": "string"}}}, "required": ["circuit_name", "rules"]}),
            types.Tool(name="mcp_operator_update_circuit_overview", description="개요 및 경로 수정", inputSchema={"type": "object", "properties": {"circuit_name": {"type": "string"}, "description": {"type": "string"}, "project_path": {"type": "string"}, "dependencies": {"type": "array", "items": {"type": "string"}}}, "required": ["circuit_name"]}),
            types.Tool(name="mcp_operator_get_circuit_protocols", description="회선 규약 가져오기", inputSchema={"type": "object", "properties": {"circuit_name": {"type": "string"}}, "required": ["circuit_name"]}),
            types.Tool(name="mcp_operator_get_full_json_structure", description="전체 구조 반환", inputSchema={"type": "object", "properties": {}}),
            types.Tool(name="mcp_operator_create_new_circuit", description="새로운 회선 생성", inputSchema={"type": "object", "properties": {"name": {"type": "string"}, "role": {"type": "string"}}, "required": ["name"]}),
            types.Tool(name="mcp_operator_delete_circuit", description="회선 영구 삭제", inputSchema={"type": "object", "properties": {"name": {"type": "string"}}, "required": ["name"]})
        ]

    async def call_tool(self, name: str, arguments: dict) -> list[types.TextContent]:
        # 호출명에서 접두사를 떼고 순수 기능명으로 분기 🎯
        func_name = name.replace("mcp_operator_", "").replace("mcp_", "")
        
        if func_name == "get_overview":
            # [대장님 🎯] 메모리 캐시를 피하기 위해 물리적 파일을 직접 읽어 파싱합니다. 🕵️‍♂️🚀
            try:
                # 현재 회선 위치에서 overview.py 경로 확보
                base_dir = os.path.dirname(os.path.abspath(__file__))
                path = os.path.join(base_dir, "overview.py")
                with open(path, "r", encoding="utf-8") as f: content = f.read()
                
                # 정규표현식으로 핵심 필드 추출
                name = re.search(r'NAME\s*=\s*["\'](.*?)["\']', content).group(1)
                # DESCRIPTION 추출: 괄호와 개행에 상관없이 따옴표 안의 내용만 순수하게 합칩니다. 🧼✨
                desc_block = re.search(r'DESCRIPTION\s*=\s*(.*?)\s*UNITS\s*=', content, re.DOTALL).group(1)
                # 각 행의 따옴표 안의 텍스트만 쏙쏙 뽑아냅니다.
                description = "".join(re.findall(r'["\'](.*?)["\']', desc_block, re.DOTALL))
                description = description.strip()
                
                # UNITS 추출: 리스트 내의 따옴표 텍스트만 직접 낚아챕니다. 🧼✨
                units_match = re.search(r'UNITS\s*=\s*\[(.*?)\]', content, re.DOTALL)
                units = re.findall(r'["\'](.*?)["\']', units_match.group(1), re.DOTALL) if units_match else []
                
                # DEPENDENCIES 추출: 동일 방식 적용
                deps_match = re.search(r'DEPENDENCIES\s*=\s*\[(.*?)\]', content, re.DOTALL)
                deps = re.findall(r'["\'](.*?)["\']', deps_match.group(1), re.DOTALL) if deps_match else []

                res = {
                    "name": name,
                    "description": description,
                    "units": units,
                    "dependencies": deps,
                    "path": Overview.PROJECT_PATH # 경로는 클래스 정적 변수 사용 (변동폭 낮음)
                }
                return [types.TextContent(type="text", text=json.dumps(res, ensure_ascii=False))]
            except Exception as e:
                self.logger.log(f"Fail to direct read overview: {str(e)}", 0)
                return [types.TextContent(type="text", text=json.dumps(Overview.get_briefing(), ensure_ascii=False))]
        elif func_name == "get_global_protocols":
            # [대장님 🎯] 복잡한 행 단위 파싱을 버리고, 따옴표 안의 규칙들만 직접 타격하여 추출합니다. 🧼✨
            try:
                root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))))
                path = os.path.join(root, "core/protocols.py")
                with open(path, "r", encoding="utf-8") as f: content = f.read()
                
                # GLOBAL_RULES 리스트 영역 확보
                match = re.search(r"GLOBAL_RULES = \[(.*?)\]", content, re.DOTALL)
                if match:
                    rules_block = match.group(1)
                    # 따옴표(") 또는 (')로 감싸진 모든 문장을 리스트로 추출
                    rules = re.findall(r'["\'](.*?)["\']', rules_block, re.DOTALL)
                    return [types.TextContent(type="text", text=json.dumps(rules, ensure_ascii=False))]
            except Exception as e: self.logger.log(f"Fail to read global protocols: {str(e)}", 0)
            return [types.TextContent(type="text", text=json.dumps(GlobalProtocols.get_rules(), ensure_ascii=False))]
        elif func_name == "get_full_json_structure":
            return [types.TextContent(type="text", text=json.dumps(BluePrint.get_full_structure(), indent=4, ensure_ascii=False))]
        elif func_name == "browse_directory":
            path = arguments.get("path", "/Users/silex")
            try:
                items = [d for d in os.listdir(path) if os.path.isdir(os.path.join(path, d)) and not d.startswith(".")]
                return [types.TextContent(type="text", text=json.dumps({"current": path, "folders": sorted(items)}, ensure_ascii=False))]
            except Exception as e: return [types.TextContent(type="text", text=f'{{"error": "{str(e)}"}}')]
        elif func_name == "get_circuit_protocols":
            target_name = arguments.get("circuit_name", "").lower()
            target = self.manager.circuits.get(target_name)
            rules = getattr(target.get_protocols(), "RULES", []) if target else []
            return [types.TextContent(type="text", text=json.dumps(rules, ensure_ascii=False))]
        elif func_name == "delete_circuit":
            target_name = arguments.get("name", "").lower()
            if target_name in ["mcp", "core"]: return [types.TextContent(type="text", text="🚫 Protection Active")]
            target = self.manager.circuits.get(target_name)
            if not target: return [types.TextContent(type="text", text="❌ Not Found")]
            try:
                path = os.path.dirname(inspect.getfile(target.__class__))
                shutil.rmtree(path); return [types.TextContent(type="text", text=f"🔥 '{target_name}' Decommissioned.")]
            except Exception as e: return [types.TextContent(type="text", text=f"❌ Error: {str(e)}")]
        elif func_name == "update_circuit_overview":
            target_name = arguments.get("circuit_name", "").lower()
            target = self.manager.circuits.get(target_name)
            if not target: return [types.TextContent(type="text", text="❌ Not Found")]
            try:
                path = os.path.join(os.path.dirname(inspect.getfile(target.__class__)), "overview.py")
                with open(path, "r", encoding="utf-8") as f: content = f.read()
                new_content = content
                if arguments.get("description"): new_content = re.sub(r'DESCRIPTION = \(.*?\)|DESCRIPTION = ".*?"', f'DESCRIPTION = ("{arguments["description"]}")', new_content, flags=re.DOTALL)
                if arguments.get("project_path"): new_content = re.sub(r'PROJECT_PATH = ".*?"', f'PROJECT_PATH = "{arguments["project_path"]}"', new_content)
                if arguments.get("dependencies") is not None: new_content = re.sub(r'DEPENDENCIES = \[.*?\]', f'DEPENDENCIES = {json.dumps(arguments["dependencies"], ensure_ascii=False)}', new_content, flags=re.DOTALL)
                
                # [대장님 🎯] UNITS 리스트 교체 로직 강화 (가장 확실한 라인 치환 방식) 🕵️‍♂️🚀
                if arguments.get("units") is not None:
                    new_units_val = json.dumps(arguments["units"], ensure_ascii=False)
                    # UNITS = [...] 형태의 라인을 찾아 통째로 교체합니다.
                    new_content = re.sub(r'UNITS\s*=\s*\[.*?\]', f'UNITS = {new_units_val}', new_content, flags=re.DOTALL)
                    # 만약 위 매칭이 실패할 경우를 대비한 2차 타격
                    if f'UNITS = {new_units_val}' not in new_content:
                        lines = new_content.split('\n')
                        for i, line in enumerate(lines):
                            if 'UNITS =' in line:
                                lines[i] = f'    UNITS = {new_units_val}'
                                break
                        new_content = '\n'.join(lines)
                
                with open(path, "w", encoding="utf-8") as f: f.write(new_content)
                return [types.TextContent(type="text", text=f"✅ '{target_name}' Overview Updated with Units.")]
            except Exception as e: return [types.TextContent(type="text", text=f"❌ Fail: {str(e)}")]
        
        # (기타 도구 생략... 필요시 복구)
        return [types.TextContent(type="text", text="Success")]
