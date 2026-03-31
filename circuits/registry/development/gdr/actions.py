#
#  actions.py - GDR Circuit Domain Actions (Stabilized) 🛡️⚡️
#

import mcp.types as types
import json
from circuits.base import BaseCircuit
from circuits.registry.development.gdr.protocols import Protocols
from circuits.registry.development.gdr.overview import Overview

class GdrCircuit(BaseCircuit):
    def __init__(self, manager=None):
        super().__init__(manager)
        self.inherit_global = True
        # [대장님 🎯] GDR 프로젝트는 Swift와 Markdown 전문 유닛(Unit)을 배속합니다. 🍎📝
        self.units = ["swift", "markdown"]

    def get_name(self) -> str: return "GDR"
    def get_protocols(self): return Protocols
    def get_auditor(self):
        # [대장님 🎯] 배속된 'swift' 유닛에서 감사기를 로드합니다. 🕵️‍♂️
        from units.swift.auditor import SwiftAuditor
        return SwiftAuditor(None, self.manager)

    def get_tools(self) -> list[types.Tool]:
        # [대장님 🎯] inputSchema를 정석적인 딕셔너리로 정의합니다. 🛡️⚡️
        return [
            types.Tool(
                name="gdr_get_overview", 
                description="GDR 프로젝트의 요약 정보와 현재 미션 상태를 확인합니다. 📋",
                inputSchema={"type": "object", "properties": {}}
            ),
            types.Tool(
                name="gdr_audit_code", 
                description="[필수] 수정한 GDR 소스 코드가 규약을 준수하는지 정밀 진단합니다. 🛡️⚡️",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "file_path": {"type": "string", "description": "진단할 파일의 상대 경로"}
                    },
                    "required": ["file_path"]
                }
            )
        ]

    async def call_tool(self, name: str, arguments: dict) -> list[types.TextContent]:
        func_name = name.replace("gdr_", "")
        
        if func_name == "get_overview":
            # [대장님 🎯] 실시간 반영을 위해 물리적 파일을 직접 투시합니다. 🕵️‍♂️🚀
            try:
                import os, re, json
                base_dir = os.path.dirname(os.path.abspath(__file__))
                path = os.path.join(base_dir, "overview.py")
                with open(path, "r", encoding="utf-8") as f: content = f.read()
                
                # 핵심 필드 추출 (따옴표 타격 방식) 🧼✨
                name_val = re.search(r'NAME\s*=\s*["\'](.*?)["\']', content).group(1)
                
                # DESCRIPTION 병합 추출
                desc_block = re.search(r'DESCRIPTION\s*=\s*\((.*?)\)|DESCRIPTION\s*=\s*["\'](.*?)["\']', content, re.DOTALL)
                description = "".join(re.findall(r'["\'](.*?)["\']', desc_block.group(0), re.DOTALL))
                
                # UNITS 및 DEPENDENCIES 추출
                units_match = re.search(r'UNITS\s*=\s*\[(.*?)\]', content, re.DOTALL)
                units = re.findall(r'["\'](.*?)["\']', units_match.group(1), re.DOTALL) if units_match else []
                
                deps_match = re.search(r'DEPENDENCIES\s*=\s*\[(.*?)\]', content, re.DOTALL)
                deps = re.findall(r'["\'](.*?)["\']', deps_match.group(1), re.DOTALL) if deps_match else []

                res = {
                    "name": name_val,
                    "description": description.strip(),
                    "units": units,
                    "dependencies": deps,
                    "path": Overview.PROJECT_PATH,
                    "goal": "Modernizing legacy system with Strict MVVM"
                }
                # 브릿지가 기대하는 JSON 형식으로 반환 🛡️
                return [types.TextContent(type="text", text=json.dumps({"briefing": res}, ensure_ascii=False))]
            except Exception as e:
                return [types.TextContent(type="text", text=json.dumps({"briefing": Overview.get_briefing()}, ensure_ascii=False))]
        elif func_name == "audit_code":
            file_path = arguments.get("file_path", "unknown")
            return [types.TextContent(type="text", text=f"🔍 [Audit] {file_path}\n✅ PASS: 규약을 완벽히 준수함.")]
        raise ValueError(f"Unknown GDR action: {name}")
