#
#  actions.py - GolfzonAuth Library Actions
#

import mcp.types as types
import os
from tenants.base import BaseTenant
from tenants.projects.golfzon.libraries.auth.axioms import Axioms
from tenants.projects.golfzon.libraries.auth.overview import Overview
from tenants.projects.golfzon.libraries.auth.blueprint import BluePrint
from core.logger import HubLogger
from language.swift.auditor import SwiftAuditor

class GolfzonAuthTenant(BaseTenant):
    def __init__(self):
        self.logger = HubLogger("GolfzonAuth")
        self.auditor = SwiftAuditor(logger=self.logger)

    def get_name(self) -> str:
        return "GolfzonAuth"

    def get_tools(self) -> list[types.Tool]:
        return [
            types.Tool(
                name="auth_audit_rules",
                description="GolfzonAuth 라이브러리 컨벤션 준수 여부를 진단합니다.",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "file_path": {"type": "string", "description": "진단할 소스 파일 경로"}
                    },
                    "required": ["file_path"]
                }
            ),
            types.Tool(
                name="auth_get_overview",
                description="GolfzonAuth 라이브러리의 요약 정보(경로, 도메인)를 확인합니다.",
                inputSchema={"type": "object", "properties": {}},
            ),
            types.Tool(
                name="auth_get_blueprint",
                description="GolfzonAuth 라이브러리의 상세 설계도를 확인합니다.",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "domain": {"type": "string", "description": "상세 설계도를 볼 도메인 이름 (예: auth/core, screenlogin)"}
                    }
                },
            )
        ]

    async def call_tool(self, name: str, arguments: dict) -> list[types.TextContent]:
        self.logger.log(f"GolfzonAuth 도구 호출: {name}", 0)
        
        func_name = name.replace("auth_", "")
        
        if func_name == "get_overview":
            briefing = Overview.get_briefing()
            res = (
                f"🔐 [GolfzonAuth Overview]\n"
                f"---\n"
                f"📍 Root: {briefing['path']}\n"
                f"📂 Domains: {', '.join(briefing['domains'])}\n"
                f"📜 Key Rules: {', '.join(Axioms.CUSTOM_RULES)}"
            )
            return [types.TextContent(type="text", text=res)]

        elif func_name == "get_blueprint":
            domain = arguments.get("domain")
            if domain:
                spec = BluePrint.get_domain_spec(domain)
                if not spec:
                    return [types.TextContent(type="text", text=f"❌ '{domain}' 도메인 설계도를 찾을 수 없습니다.")]
                
                res = f"📐 [BluePrint: {spec['name']}]\n---\n"
                res += f"📝 Desc: {spec['desc']}\n"
                res += f"📍 Path: {spec['path']}\n"
                if "flow" in spec:
                    res += "\n🔄 Flow:\n"
                    for k, v in spec["flow"].items(): res += f"  - {k}: {v}\n"
                if "components" in spec:
                    res += "\n🧩 Components:\n"
                    for k, v in spec["components"].items(): res += f"  - {k}: {v}\n"
                return [types.TextContent(type="text", text=res)]
            else:
                master = BluePrint.get_master()
                return [types.TextContent(type="text", text=f"📐 [GolfzonAuth Master]\n---\n🔄 Flow: {master['flow']}\n🎯 Purpose: {master['purpose']}")]

        elif func_name == "audit_rules":
            file_path = arguments.get("file_path", "")
            if not os.path.exists(file_path):
                return [types.TextContent(type="text", text=f"❌ ERROR: Axiom Verification Failed\n---\n파일을 찾을 수 없습니다: {file_path}")]

            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    content = f.read()
            except Exception as e:
                return [types.TextContent(type="text", text=f"❌ ERROR: Axiom Verification Failed\n---\n파일을 읽을 수 없습니다: {str(e)}")]

            results = self.auditor.audit(file_path, content)
            if not results:
                status_msg = "✅ PASS: 모든 공리를 준수하고 있습니다! 🚀"
                return [types.TextContent(type="text", text=f"🔍 [Auth Audit] {os.path.basename(file_path)}\n---\n{status_msg}")]
            else:
                violations = "\n".join(results)
                error_res = (
                    f"❌ ERROR: Axiom Violation Detected!\n"
                    f"---\n"
                    f"파일: {os.path.basename(file_path)}\n"
                    f"위반 내역:\n{violations}\n\n"
                    f"⚠️ 주의: 인증 관련 모듈은 보안과 직결되므로 공리를 반드시 준수해야 합니다. 🛡️"
                )
                return [types.TextContent(type="text", text=error_res)]
            
        raise ValueError(f"Unknown tool: {name}")
