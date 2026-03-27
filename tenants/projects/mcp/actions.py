#
#  actions.py - High-Performance MCP Hub Domain Actions (Restored)
#

import mcp.types as types
import os
from tenants.base import BaseTenant
from tenants.projects.mcp.axioms import Axioms
from tenants.projects.mcp.overview import Overview
from tenants.projects.mcp.blueprint import BluePrint
from core.logger import HubLogger

class MCPTenant(BaseTenant):
    def __init__(self):
        self.logger = HubLogger("MCPTenant")

    def get_name(self) -> str:
        return "MCP"

    def get_dependencies(self) -> list[str]:
        # MCP는 최상위 전장이므로 의존성 없음
        return []

    def get_tools(self) -> list[types.Tool]:
        """
        [대장님 🎯] MCP 프로젝트 전용 도구 목록을 정의합니다.
        GDR과 동일한 깔끔한 명명 규칙을 준수합니다.
        """
        return [
            types.Tool(
                name="audit_rules",
                description="[MANDATORY] MCP Hub 소스 수정 시 반드시 호출하십시오. Python Type Hinting, Pydantic, Async 등 MCP 공리를 진단합니다.",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "file_path": {"type": "string", "description": "진단할 소스 파일 경로"}
                    },
                    "required": ["file_path"]
                }
            ),
            types.Tool(
                name="get_overview",
                description="MCP Hub의 요약 정보(이름, 경로, 도메인, 목표)를 확인합니다.",
                inputSchema={"type": "object", "properties": {}},
            ),
            types.Tool(
                name="get_blueprint",
                description="MCP Hub의 정밀 설계도(Interface, Data Flow, Core Architecture)를 확인합니다.",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "domain": {"type": "string", "description": "상세 설계도를 볼 도메인 이름 (예: core, tenants)"}
                    }
                },
            )
        ]

    async def call_tool(self, name: str, arguments: dict) -> list[types.TextContent]:
        self.logger.log(f"MCP 도구 호출: {name}", 0)
        
        # [대장님 🎯] 핵심 기능 매핑 (mcp_ 접두사 처리)
        func_name = name.replace("mcp_", "")
        
        if func_name == "get_overview":
            briefing = Overview.get_briefing()
            res = (
                f"📋 [MCP Overview]\n"
                f"---\n"
                f"🚀 Project: {briefing['project']}\n"
                f"📍 Root: {briefing['path']}\n"
                f"🐍 Languages: {', '.join(briefing['languages'])}\n"
                f"📂 Domains: {', '.join(briefing['domains'])}\n"
                f"🎯 Goal: {briefing['goal']}\n"
                f"💡 Tip: 'get_blueprint'를 통해 허브 엔진의 설계를 확인하세요."
            )
            return [types.TextContent(type="text", text=res)]

        elif func_name == "get_blueprint":
            domain = arguments.get("domain")
            
            if domain:
                spec = BluePrint.get_domain_spec(domain)
                if not spec:
                    return [types.TextContent(type="text", text=f"❌ '{domain}' 도메인 설계도를 찾을 수 없습니다.")]
                
                res = f"📐 [MCP BluePrint: {spec['name']}]\n---\n"
                res += f"📝 Desc: {spec['desc']}\n"
                res += f"📍 Path: {spec['path']}\n"
                
                if "flow" in spec:
                    res += "\n🔄 Core Flow:\n"
                    for k, v in spec["flow"].items(): res += f"  - {k}: {v}\n"
                
                if "logic" in spec: res += f"⚙️ Logic: {spec['logic']}\n"
                
                if "components" in spec:
                    res += "\n🧩 Components:\n"
                    for k, v in spec["components"].items(): res += f"  - {k}: {v}\n"
                
                return [types.TextContent(type="text", text=res)]
            else:
                master = BluePrint.get_master()
                bindings_str = "\n".join([f"- {k}: {v}" for k, v in master["bindings"].items()])
                res = (
                    f"📐 [MCP System BluePrint]\n"
                    f"---\n"
                    f"🔄 Data Flow: {master['flow']['Data']}\n"
                    f"🗺️ Navigation: {master['flow']['Navigation']}\n"
                    f"\n🔗 Global Bindings:\n{bindings_str}\n"
                )
                return [types.TextContent(type="text", text=res)]

        elif func_name == "audit_rules":
            file_path = arguments.get("file_path", "")
            result = self._audit(file_path)
            return [types.TextContent(type="text", text=result)]
            
        self.logger.log(f"알 수 없는 도구: {name}", 1)
        raise ValueError(f"테넌트에서 '{name}' 도구를 처리할 수 없습니다.")

    def _audit(self, file_path: str) -> str:
        # 전문 Python Auditor 엔진 호출 (Level 2: PythonAxioms 상속)
        from language.python.auditor import PythonAuditor
        
        if not os.path.exists(file_path):
            return f"❌ ERROR: 파일을 찾을 수 없습니다: {file_path}"

        if not (file_path.endswith(".py") or file_path.endswith(".md")):
            return "✅ PASS: Non-code file (Axiom not applicable)."

        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()

            auditor = PythonAuditor(self.logger)
            report = auditor.audit(file_path, content)

        except Exception as e:
            return f"❌ ERROR: 파일을 읽는 도중 에러가 발생했습니다: {str(e)}"

        if not report:
            return f"🔍 [Audit] {os.path.basename(file_path)}\n---\n✅ PASS: Silex Standard (Python MCP) 준수 완료! 역시 대장님 스타일입니다! 🚀"
        
        violations = "\n".join(report)
        return (
            f"❌ ERROR: Axiom Violation Detected!\n"
            f"---\n"
            f"파일: {os.path.basename(file_path)}\n"
            f"위반 내역:\n{violations}\n\n"
            f"🛡️✨ 공리를 교정한 후 다시 Audit 하십시오."
        )
