#
#  actions.py - Clean & Precision Domain Actions
#

import mcp.types as types
import os
from tenants.base import BaseTenant
from tenants.projects.golfzon.gdr.axioms import Axioms
from tenants.projects.golfzon.gdr.overview import Overview
from tenants.projects.golfzon.gdr.blueprint import BluePrint
from core.logger import HubLogger
from language.swift.auditor import SwiftAuditor

class GDRTenant(BaseTenant):
    def __init__(self):
        self.logger = HubLogger("GDRTenant")
        self.auditor = SwiftAuditor(logger=self.logger)

    def get_name(self) -> str:
        return "GDR"

    def get_dependencies(self) -> list[str]:
        return getattr(Overview, "DEPENDENCIES", [])

    def get_tools(self) -> list[types.Tool]:
        """
        [대장님 🎯] 도구 이름에서 중복된 'gdr_' 접두사를 제거하여 
        더 직관적이고 담백한 인터페이스를 제공합니다.
        """
        return [
            types.Tool(
                name="audit_rules",
                description="[MANDATORY] 모든 파일 수정 전/후 반드시 호출하십시오. 이 도구가 'PASS'를 반환하지 않으면 공리 위반으로 간주되어 작업 완료가 거부됩니다. MVVM, Naming, Safety 등 프로젝트 핵심 공리를 정밀 진단합니다.",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "file_path": {"type": "string", "description": "진단할 소스 파일 경로"}
                    },
                    "required": ["file_path"]
                }
            ),
            types.Tool(
                name="get_environment",
                description="프로젝트의 핵심 경로 및 설정 정보를 반환합니다.",
                inputSchema={"type": "object", "properties": {}},
            ),
            types.Tool(
                name="get_overview",
                description="프로젝트의 요약 정보(이름, 경로, 언어, 도메인)를 확인합니다.",
                inputSchema={"type": "object", "properties": {}},
            ),
            types.Tool(
                name="get_blueprint",
                description="프로젝트의 정밀 설계도(인터페이스, 데이터 흐름, 결합도)를 확인합니다.",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "domain": {"type": "string", "description": "상세 설계도를 볼 도메인 이름 (예: Nasmo, Auth)"}
                    }
                },
            )
        ]

    async def call_tool(self, name: str, arguments: dict) -> list[types.TextContent]:
        self.logger.log(f"GDR 도구 호출: {name}", 0)
        
        # [대장님 🎯] 접두사 유무와 관계없이 핵심 기능 매핑
        func_name = name.replace("gdr_", "")
        
        if func_name == "get_environment":
            summary = Axioms.get_summary()
            return [types.TextContent(
                type="text",
                text=f"🏢 Project: {summary['name']}\n📍 Root: {Axioms.PROJECT_ROOT}\n📜 Rules: {', '.join(summary['rules'])}"
            )]
            
        elif func_name == "get_overview":
            briefing = Overview.get_briefing()
            res = (
                f"📋 [Overview]\n"
                f"---\n"
                f"🚀 Project: {briefing['project']}\n"
                f"📍 Root: {briefing['path']}\n"
                f"🌐 Languages: {', '.join(briefing['languages'])}\n"
                f"📂 Domains: {', '.join(briefing['domains'])}\n"
                f"💡 Tip: 'get_blueprint'를 통해 더 자세한 구조를 확인하세요."
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
                    res += "\n🔄 Core Flow:\n"
                    for k, v in spec["flow"].items(): res += f"  - {k}: {v}\n"
                
                if "logic" in spec: res += f"⚙️ Logic: {spec['logic']}\n"
                
                if "interfaces" in spec:
                    res += f"📥 Input: {', '.join(spec['interfaces']['Input'])}\n"
                    res += f"📤 Output: {', '.join(spec['interfaces']['Output'])}\n"
                
                if "components" in spec:
                    res += "\n🧩 Components:\n"
                    for k, v in spec["components"].items(): 
                        desc = v['desc'] if isinstance(v, dict) else v
                        res += f"  - {k}: {desc}\n"
                
                if "structures" in spec:
                    res += "\n📦 Structures:\n"
                    for k, v in spec["structures"].items(): res += f"  - {k}: {v}\n"

                if "dependencies" in spec:
                    res += f"\n🔗 Dependencies: {', '.join(spec['dependencies'])}\n"
                
                return [types.TextContent(type="text", text=res)]
            else:
                # 전체 시스템 마스터 흐름 로드
                master = BluePrint.get_master()
                bindings_str = "\n".join([f"- {k}: {v}" for k, v in master["bindings"].items()])
                res = (
                    f"📐 [System BluePrint]\n"
                    f"---\n"
                    f"🔄 Data Flow: {master['flow']['Data']}\n"
                    f"🗺️ Navigation: {master['flow']['Navigation']}\n"
                    f"\n🔗 Global Bindings:\n{bindings_str}\n"
                    f"\n💡 특정 도메인 상세 정보는 'get_blueprint(domain=\"...\")'를 사용하세요."
                )
                return [types.TextContent(type="text", text=res)]

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
                status_msg = "✅ PASS: 모든 공리를 준수하고 있습니다! 역시 대장님 스타일입니다! 🚀"
                return [types.TextContent(type="text", text=f"🔍 [Audit] {os.path.basename(file_path)}\n---\n{status_msg}")]
            else:
                # [대장님 🎯] 위반 사항이 있을 경우 'ERROR' 헤더를 붙여 모델에게 강한 경고를 보냅니다! 🛡️⚡️
                violations = "\n".join(results)
                error_res = (
                    f"❌ ERROR: Axiom Violation Detected!\n"
                    f"---\n"
                    f"파일: {os.path.basename(file_path)}\n"
                    f"위반 내역:\n{violations}\n\n"
                    f"⚠️ 주의: 위 사항들을 즉시 교정하지 않으면 작업 완료로 인정되지 않습니다. 🛡️"
                )
                return [types.TextContent(type="text", text=error_res)]
            
        self.logger.log(f"알 수 없는 도구: {name}", 1)
        raise ValueError(f"테넌트에서 '{name}' 도구를 처리할 수 없습니다.")
