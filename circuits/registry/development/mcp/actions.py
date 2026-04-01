#
#  actions.py - Standard MCP Domain Actions (Naming Fixed) 
#

from shared.models import TextResponse, JsonResponse
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
from shared.utils import get_project_root, read_json_safely, write_json_safely

class MCPCircuit(BaseCircuit):
    def __init__(self, manager=None):
        super().__init__(manager)
        self.logger = OperatorLogger("MCPCircuit")
        # [사용자] Overview에 정의된 전문 유닛들을 동적으로 배속합니다. 
        self.units = Overview.UNITS

    def get_name(self) -> str: return "MCP"
    def get_protocols(self): return Protocols
    def get_auditor(self):
        # [사용자] 배속된 'python' 유닛에서 감사기를 로드합니다. 
        from units.python.auditor import PythonAuditor
        return PythonAuditor(self.logger)

    def get_tools(self) -> list[types.Tool]:
        # [사용자] 도구 이름을 브릿지가 찾는 'mcp_operator_...' 규격과 완벽히 일치시킵니다. 
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
            types.Tool(name="mcp_operator_delete_circuit", description="회선 영구 삭제", inputSchema={"type": "object", "properties": {"name": {"type": "string"}}, "required": ["name"]}),
            # [Sentinel] 하네스 엔지니어링 미션 제어 도구
            types.Tool(name="sentinel_set_mission", description="현재 작업의 최종 목적(Objective)과 성공 기준(Criteria)을 설정합니다.", inputSchema={"type": "object", "properties": {"objective": {"type": "string"}, "criteria": {"type": "array", "items": {"type": "string"}}}, "required": ["objective", "criteria"]}),
            types.Tool(
                name="sentinel_evaluate",
                description="현재 작업 결과물을 미션 목적과 대조하여 통과 여부를 판정합니다. 가능한 경우 검증용 테스트 명령어를 포함하세요.",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "test_command": {
                            "type": "string",
                            "description": "선택사항. 변경 사항이 제대로 동작하는지 증명할 쉘 명령어 (예: 'pytest src/test.py'). 없으면 빈 문자열."
                        },
                        "evidence": {
                            "type": "string",
                            "description": "각 성공 기준(criteria)을 어떻게 충족했는지 설명하는 구체적인 증거 데이터 및 논리."
                        }
                    },
                    "required": ["evidence"]
                }
            ),
            types.Tool(name="sentinel_get_mission", description="현재 설정된 미션 정보를 조회합니다.", inputSchema={"type": "object", "properties": {}})
        ]

    async def call_tool(self, name: str, arguments: dict) -> list[types.TextContent]:
        # 호출명에서 접두사를 떼고 순수 기능명으로 분기 
        func_name = name.replace("mcp_operator_", "").replace("mcp_", "")
        
        if func_name == "get_blueprint":
            domain = arguments.get("domain")
            if domain:
                return JsonResponse(BluePrint.get_domain_spec(domain))
            # 도메인 지정이 없으면 Master Blueprint(스펙 목차 포함)를 반환합니다. 
            return JsonResponse(BluePrint.get_master())
        
        elif func_name == "get_spec_content":
            spec_file = arguments.get("spec_file")
            return JsonResponse(BluePrint.get_spec_detail(spec_file))

        elif func_name == "get_overview":
            try:
                base_dir = os.path.dirname(os.path.abspath(__file__))
                json_path = os.path.join(base_dir, "overview.json")
                if os.path.exists(json_path):
                    with open(json_path, "r", encoding="utf-8") as f:
                        data = json.load(f)
                        res = {
                            "name": data.get("name", ""),
                            "description": data.get("description", ""),
                            "units": data.get("units", []),
                            "dependencies": data.get("dependencies", []),
                            "path": Overview.PROJECT_PATH
                        }
                        return JsonResponse(res)
            except Exception as e:
                pass
            
            # 폴백
            try:
                base_dir = os.path.dirname(os.path.abspath(__file__))
                path = os.path.join(base_dir, "overview.py")
                with open(path, "r", encoding="utf-8") as f: content = f.read()
                
                name = re.search(r'NAME\s*=\s*["\'](.*?)["\']', content).group(1)
                desc_block = re.search(r'DESCRIPTION\s*=\s*(.*?)\s*UNITS\s*=', content, re.DOTALL).group(1)
                description = "".join(re.findall(r'["\'](.*?)["\']', desc_block, re.DOTALL)).strip()
                
                units_match = re.search(r'UNITS\s*=\s*\[(.*?)\]', content, re.DOTALL)
                units = re.findall(r'["\'](.*?)["\']', units_match.group(1), re.DOTALL) if units_match else []
                
                deps_match = re.search(r'DEPENDENCIES\s*=\s*\[(.*?)\]', content, re.DOTALL)
                deps = re.findall(r'["\'](.*?)["\']', deps_match.group(1), re.DOTALL) if deps_match else []

                res = {
                    "name": name,
                    "description": description,
                    "units": units,
                    "dependencies": deps,
                    "path": Overview.PROJECT_PATH
                }
                return JsonResponse(res)
            except Exception as e:
                self.logger.log(f"Fail to direct read overview: {str(e)}", 0)
                return JsonResponse(Overview.get_briefing())
        elif func_name == "get_global_protocols":
            # [사용자] JSON으로 분리된 전사 규약을 GlobalProtocols를 통해 로드합니다.
            try:
                rules = GlobalProtocols.get_rules()
                return JsonResponse(rules)
            except Exception as e:
                self.logger.log(f"Fail to read global protocols: {str(e)}", 0)
                return TextResponse("[]")
                
        elif func_name == "create_new_circuit":
            name = arguments.get("name", "").lower()
            role = arguments.get("role", "development")
            if not name: return TextResponse(" Error: Name is required")
            
            try:
                root = get_project_root()
                circuit_path = os.path.join(root, "circuits", "registry", role, name)
                
                if os.path.exists(circuit_path):
                    return TextResponse(f" Error: Circuit '{name}' already exists")
                    
                os.makedirs(circuit_path, exist_ok=True)
                
                # 1. overview.json 생성
                overview_data = {
                    "name": name,
                    "description": f"새로운 {name.upper()} 회선입니다.",
                    "project_path": "",
                    "dependencies": [],
                    "units": []
                }
                with open(os.path.join(circuit_path, "overview.json"), "w", encoding="utf-8") as f:
                    json.dump(overview_data, f, indent=2, ensure_ascii=False)
                    
                # 하위 호환성을 위한 최소한의 overview.py 생성 (추후 완전 제거 가능)
                overview_content = f'''#
#  overview.py - {name.upper()} Circuit Overview (Legacy Fallback)
#  Data is now primarily managed in overview.json
#

class Overview:
    NAME = "{name}"
    UNITS = []
    
    @classmethod
    def get_briefing(cls) -> dict:
        import json, os
        try:
            with open(os.path.join(os.path.dirname(__file__), "overview.json"), "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return {{"name": cls.NAME, "description": "", "path": "", "dependencies": [], "units": cls.UNITS}}
'''
                with open(os.path.join(circuit_path, "overview.py"), "w", encoding="utf-8") as f:
                    f.write(overview_content)
                    
                # 2. protocols.json 생성 (신규 JSON 설계 준수)
                protocols_data = {
                    "RULES": [
                        f"Protocol {name.upper()}-1 (Identity): {name.upper()} 회선의 고유한 목적을 유지한다."
                    ]
                }
                with open(os.path.join(circuit_path, "protocols.json"), "w", encoding="utf-8") as f:
                    json.dump(protocols_data, f, indent=2, ensure_ascii=False)
                    
                # 3. actions.py 생성
                actions_content = f'''#
#  actions.py - {name.upper()} Circuit Actions
#

from circuits.base import BaseCircuit
import os
import json
from mcp import types

class {name.capitalize()}Circuit(BaseCircuit):
    def __init__(self, manager=None):
        super().__init__(manager)
        self.units = []
        try:
            with open(os.path.join(os.path.dirname(__file__), "overview.json"), "r", encoding="utf-8") as f:
                data = json.load(f)
                self.units = data.get("units", [])
        except Exception:
            pass

    def get_name(self) -> str: return "{name}"
    
    def get_tools(self) -> list[types.Tool]:
        return [
            types.Tool(name="{name}_get_overview", description="{name.upper()} 프로젝트 요약 정보 확인", inputSchema={{"type": "object", "properties": {{}}}})
        ]
        
    async def call_tool(self, name: str, arguments: dict) -> list[types.TextContent]:
        return TextResponse("Success")
'''
                with open(os.path.join(circuit_path, "actions.py"), "w", encoding="utf-8") as f:
                    f.write(actions_content)
                
                # __init__.py 생성
                with open(os.path.join(circuit_path, "__init__.py"), "w", encoding="utf-8") as f:
                    pass
                
                return TextResponse(f" '{name}' Circuit Created successfully.")
            except Exception as e:
                return TextResponse(f" Error: {{str(e)}}")
        elif func_name == "get_full_json_structure":
            return JsonResponse(BluePrint.get_full_structure(self.manager))
        elif func_name == "browse_directory":
            path = arguments.get("path")
            if not path:
                path = os.path.expanduser("~")
            try:
                items = [d for d in os.listdir(path) if os.path.isdir(os.path.join(path, d)) and not d.startswith(".")]
                return JsonResponse({"current": path, "folders": sorted(items)})
            except Exception as e: return TextResponse(f'{{"error": "{str(e)}"}}')
        elif func_name == "get_circuit_protocols":
            target_name = arguments.get("circuit_name", "").lower()
            target = self.manager.circuits.get(target_name)
            if not target: return TextResponse("[]")
            
            try:
                circuit_dir = os.path.dirname(inspect.getfile(target.__class__))
                json_path = os.path.join(circuit_dir, "protocols.json")
                if os.path.exists(json_path):
                    with open(json_path, "r", encoding="utf-8") as f:
                        data = json.load(f)
                        return JsonResponse(data.get("RULES", []))
            except Exception: pass
            
            # JSON이 없으면 기존 방식(클래스 참조)으로 폴백
            rules = getattr(target.get_protocols(), "RULES", []) if target else []
            return JsonResponse(rules)
        elif func_name == "delete_circuit":
            target_name = arguments.get("name", "").lower()
            if target_name in ["mcp", "core"]: return TextResponse(" Protection Active")
            target = self.manager.circuits.get(target_name)
            if not target: return TextResponse(" Not Found")
            try:
                path = os.path.dirname(inspect.getfile(target.__class__))
                shutil.rmtree(path); return TextResponse(f" '{target_name}' Decommissioned.")
            except Exception as e: return TextResponse(f" Error: {str(e)}")
        elif func_name == "update_circuit_overview":
            target_name = arguments.get("circuit_name", "").lower()
            target = self.manager.circuits.get(target_name)
            if not target: return TextResponse(" Not Found")
            try:
                circuit_dir = os.path.dirname(inspect.getfile(target.__class__))
                json_path = os.path.join(circuit_dir, "overview.json")
                
                # 기존 데이터 로드 (없으면 기본값 사용)
                data = {}
                if os.path.exists(json_path):
                    with open(json_path, "r", encoding="utf-8") as f:
                        data = json.load(f)
                else:
                    # 마이그레이션을 위해 overview.py에서 읽어오기 시도
                    try:
                        from importlib import import_module
                        module_name = f"circuits.registry.development.{target_name}.overview"
                        mod = import_module(module_name)
                        OverviewClass = getattr(mod, "Overview")
                        data = {
                            "name": OverviewClass.NAME,
                            "description": OverviewClass.DESCRIPTION,
                            "units": OverviewClass.UNITS,
                            "dependencies": OverviewClass.DEPENDENCIES,
                            "project_path": OverviewClass.PROJECT_PATH
                        }
                    except Exception:
                        pass
                
                # 업데이트 수행
                if arguments.get("description"): data["description"] = arguments["description"]
                if arguments.get("project_path") is not None: data["project_path"] = arguments["project_path"]
                if arguments.get("dependencies") is not None: data["dependencies"] = arguments["dependencies"]
                if arguments.get("units") is not None: data["units"] = arguments["units"]

                with open(json_path, "w", encoding="utf-8") as f:
                    json.dump(data, f, indent=2, ensure_ascii=False)
                    
                return TextResponse(f" '{target_name}' Overview Updated in JSON.")
            except Exception as e: return TextResponse(f" Fail: {str(e)}")
        
        elif func_name == "update_circuit_protocols":
            target_name = arguments.get("circuit_name", "").lower()
            target = self.manager.circuits.get(target_name)
            if not target: return TextResponse(" Not Found")
            
            try:
                # 회선 물리 경로 하위의 protocols.json 타겟팅 
                circuit_dir = os.path.dirname(inspect.getfile(target.__class__))
                json_path = os.path.join(circuit_dir, "protocols.json")
                
                # 기존 데이터 로드 (PROJECT_NAME 등 보존)
                data = {}
                if os.path.exists(json_path):
                    with open(json_path, "r", encoding="utf-8") as f:
                        data = json.load(f)
                
                # RULES 업데이트
                data["RULES"] = arguments.get("rules", [])
                
                with open(json_path, "w", encoding="utf-8") as f:
                    json.dump(data, f, indent=2, ensure_ascii=False)
                
                return TextResponse(f" '{target_name}' Protocols JSON Updated.")
            except Exception as e:
                return TextResponse(f" Fail: {str(e)}")

        # --- Sentinel Logic ---
        elif func_name == "sentinel_set_mission":
            root = get_project_root()
            path = os.path.join(root, "mission.json")
            data = {
                "objective": arguments.get("objective"),
                "criteria": arguments.get("criteria", []),
                "status": "IN_PROGRESS",
                "iteration": 1,
                "max_iteration": 3
            }
            with open(path, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=4, ensure_ascii=False)
            return TextResponse(f" [SENTINEL] 미션 목표 설정 완료: {data['objective']}")

        elif func_name == "sentinel_get_mission":
            root = get_project_root()
            path = os.path.join(root, "mission.json")
            if not os.path.exists(path): return TextResponse(" [SENTINEL] 활성화된 미션이 없습니다.")
            with open(path, "r", encoding="utf-8") as f:
                return TextResponse(f.read())

        elif func_name == "sentinel_evaluate":
            root = get_project_root()
            path = os.path.join(root, "mission.json")
            if not os.path.exists(path): return TextResponse(" [SENTINEL] 평가할 미션이 없습니다.")
            
            with open(path, "r", encoding="utf-8") as f:
                mission = json.load(f)
            
            test_command = arguments.get("test_command", "")
            evidence = arguments.get("evidence", "")
            max_iteration = mission.get("max_iteration", 3)
            
            if mission["iteration"] >= max_iteration:
                mission["status"] = "HARD_FAIL"
                with open(path, "w", encoding="utf-8") as f: json.dump(mission, f, indent=4, ensure_ascii=False)
                return TextResponse(f" [SENTINEL] HARD FAIL: 최대 재시도 횟수({max_iteration}회)를 초과했습니다. 무한 루프 방지를 위해 작업을 강제 종료합니다. (현재 상태: {mission['status']})")

            if len(evidence.strip()) < 10:
                mission["iteration"] += 1
                with open(path, "w", encoding="utf-8") as f: json.dump(mission, f, indent=4, ensure_ascii=False)
                return TextResponse(f" [SENTINEL] FAIL (Iteration {mission['iteration']}): 성공 기준(criteria)에 대한 구체적인 증거(evidence)가 부족합니다. 다시 시도하십시오.")

            if test_command:
                import subprocess
                try:
                    result = subprocess.run(test_command, shell=True, capture_output=True, text=True, timeout=30)
                    if result.returncode != 0:
                        mission["iteration"] += 1
                        with open(path, "w", encoding="utf-8") as f: json.dump(mission, f, indent=4, ensure_ascii=False)
                        res = f" [SENTINEL] FAIL (Iteration {mission['iteration']}): 테스트 명령어 실패.\n명령어: {test_command}\n종료 코드: {result.returncode}\n출력: {result.stdout}\n에러: {result.stderr}"
                        return TextResponse(res)
                except Exception as e:
                    mission["iteration"] += 1
                    with open(path, "w", encoding="utf-8") as f: json.dump(mission, f, indent=4, ensure_ascii=False)
                    return TextResponse(f" [SENTINEL] FAIL (Iteration {mission['iteration']}): 테스트 명령어 실행 중 오류 발생: {str(e)}")

            mission["status"] = "PASS"
            with open(path, "w", encoding="utf-8") as f: json.dump(mission, f, indent=4, ensure_ascii=False)
            return TextResponse(" [SENTINEL] FINAL PASS: 모든 미션 기준과 테스트가 충족되었습니다! 작전을 성공적으로 종료해도 좋습니다.")

        # (기타 도구 생략... 필요시 복구)
        return TextResponse("Success")
