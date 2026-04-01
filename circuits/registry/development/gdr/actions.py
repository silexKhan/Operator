#  actions.py - GDR Circuit Domain Actions (Full Specs & JSON Edition)
import os
import mcp.types as types
from circuits.base import BaseCircuit
from core.logger import OperatorLogger
from shared.models import TextResponse

class GdrCircuit(BaseCircuit):
    def __init__(self, manager):
        self.manager = manager
        self.logger = OperatorLogger("GdrCircuit")
        self.units = ["markdown", "sentinel", "swift"]

    def get_name(self) -> str: return "GDR"

    def get_tools(self) -> list[types.Tool]:
        return [
            # GDR 전용 도구
            types.Tool(name="gdr_get_overview", description="GDR 프로젝트의 요약 정보와 현재 미션 상태를 확인합니다. ", inputSchema={"type": "object", "properties": {}}),
            types.Tool(name="gdr_audit_code", description="[필수] 수정한 GDR 소스 코드가 규약을 준수하는지 정밀 진단합니다. ", inputSchema={"type": "object", "properties": {"file_path": {"type": "string"}}, "required": ["file_path"]}),
        ]

    async def call_tool(self, name: str, arguments: dict | None) -> list[types.TextContent]:
        from core.scanner import CodeScanner
        from shared.utils import get_project_root
        
        args = arguments or {}
        # 도구 접두사 제거
        func_name = name.replace("gdr_", "")
        
        if func_name == "get_overview":
            from circuits.registry.development.gdr.overview import Overview
            res = f" [GDR MISSION CENTER]\n- NAME: {Overview.NAME}\n- ROLE: {Overview.ROLE}\n- STATUS: ACTIVE"
            return TextResponse(res)
            
        elif func_name == "audit_code":
            from units.swift.auditor import SwiftAuditor
            auditor = SwiftAuditor(self.logger, self.manager)
            file_path = args.get("file_path", "")
            if not os.path.exists(file_path): return TextResponse(f" 존재하지 않는 파일: {file_path}")
            
            with open(file_path, "r", encoding="utf-8") as f:
                report = auditor.audit(file_path, f.read())
            return TextResponse("\n".join(report) if report else " PASS: 모든 규약을 준수하고 있습니다. ")
            
        raise ValueError(f"Tool not found: {name}")

    def get_protocols(self):
        from circuits.registry.development.gdr.protocols import Protocols
        return Protocols

    def get_blueprint(self):
        from circuits.registry.development.gdr.blueprint import BluePrint
        return BluePrint()
