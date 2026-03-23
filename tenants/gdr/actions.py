#
#  actions.py - High-Precision GDR Domain Actions
#

import mcp.types as types
import os
import re
from tenants.base import BaseTenant
from tenants.gdr.axioms import GDRAxioms
from core.logger import HubLogger

class GDRTenant(BaseTenant):
    def __init__(self):
        self.logger = HubLogger("GDRTenant")

    def get_name(self) -> str:
        return "GDR"

    def get_tools(self) -> list[types.Tool]:
        return [
            types.Tool(
                name="gdr_audit_rules",
                description="현재 파일이 GDR의 아키텍처 공리(MVVM, Naming, etc)를 준수하는지 정밀 진단합니다.",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "file_path": {"type": "string", "description": "진단할 소스 파일 경로"}
                    },
                    "required": ["file_path"]
                }
            ),
            types.Tool(
                name="gdr_get_environment",
                description="GDR 프로젝트의 핵심 경로 및 설정 정보를 반환합니다.",
                inputSchema={"type": "object", "properties": {}},
            )
        ]

    async def call_tool(self, name: str, arguments: dict) -> list[types.TextContent]:
        self.logger.log(f"GDR 도구 호출: {name}", 0)
        
        if name == "gdr_get_environment":
            summary = GDRAxioms.get_summary()
            self.logger.log("환경 정보 반환 완료", 1)
            return [types.TextContent(
                type="text",
                text=f"🏢 Project: {summary['name']}\n📍 Root: {GDRAxioms.PROJECT_ROOT}\n📜 Rules: {', '.join(summary['rules'])}"
            )]
            
        elif name == "gdr_audit_rules":
            file_path = arguments.get("file_path", "")
            self.logger.log(f"규칙 진단 시작: {file_path}", 1)
            
            if not os.path.exists(file_path):
                self.logger.log(f"파일 없음 에러: {file_path}", 1)
                return [types.TextContent(type="text", text=f"❌ 에러: 파일을 찾을 수 없습니다. ({file_path})")]

            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    content = f.read()
            except Exception as e:
                self.logger.log(f"파일 읽기 에러: {str(e)}", 1)
                return [types.TextContent(type="text", text=f"❌ 에러: 파일을 읽을 수 없습니다. ({str(e)})")]

            results = []
            is_view_controller = "ViewController" in file_path
            is_view_model = "ViewModel" in file_path
            
            self.logger.log(f"파일 타입 감지 - VC: {is_view_controller}, VM: {is_view_model}", 1)

            # 1. Combine Naming Convention Check (전역 규칙)
            subject_pattern = r"(let|var)\s+\w+Subject\s*[:=]\s*(PassthroughSubject|CurrentValueSubject)"
            if re.search(subject_pattern, content):
                self.logger.log("Naming 위반 발견 (Subject suffix)", 2)
                results.append("⚠️ [Naming] 'Subject' 접미사가 포함된 변수가 발견되었습니다. (GDR 공리 위반)")

            # 1-5. [weak self] Optimization Check (전역 규칙)
            weak_self_blocks = re.findall(r"\{\s*\[weak\s+self\][^}]*\}", content)
            for block in weak_self_blocks:
                if "self?." not in block and "self." not in block and "self " not in block:
                    self.logger.log("불필요한 [weak self] 발견", 2)
                    results.append("⚠️ [Optimization] 클로저 내에서 self를 참조하지 않는데 [weak self]가 선언된 곳이 있습니다.")
                    break # 한 파일 내에서 한 번만 경고

            # 2. Dumb-View Integrity Check (ViewController 전용)
            if is_view_controller:
                logic_keywords = len(re.findall(r"\b(if|switch|guard)\b", content))
                if logic_keywords > 15:
                    self.logger.log(f"Dumb-View 위반 의심: 조건문 {logic_keywords}개", 2)
                    results.append(f"⚠️ [Dumb-View] {logic_keywords}개의 조건문이 발견되었습니다. 비즈니스 로직이 ViewModel로 완전히 이전되었는지 확인이 필요합니다.")
                
                if "!" in content and "IBOutlet" not in content:
                    self.logger.log("Safety 위반 의심: 강제 언래핑 발견", 2)
                    results.append("⚠️ [Safety] 강제 언래핑('!') 사용이 의심됩니다. (Safety-First 위반)")

            # 3. Business Specification Check (ViewModel 전용)
            if is_view_model:
                has_input = "struct Input" in content
                has_output = "struct Output" in content
                has_transform = "func transform" in content
                
                if not (has_input and has_output and has_transform):
                    self.logger.log("ViewModel 구조 미달 발견", 2)
                    results.append("⚠️ [Architect] Input/Output 구조체 또는 transform() 메서드가 누락되었습니다. (Business Spec 미준수)")
                else:
                    self.logger.log("ViewModel 연쇄 수정 리마인더 추가", 1)
                    results.append("💡 [Dependency] ViewModel의 인터페이스(Output)가 수정되었다면, 이를 사용하는 ViewController의 바인딩 코드도 반드시 전수 업데이트하십시오. (GDR 공리: 연쇄 수정 의무)")
                    results.append("👥 [Delegation] 작업 범위가 넓거나(3개 파일 이상) 반복적인 작업인 경우, 'generalist' 부사수를 투입하여 자율적으로 완수하도록 지휘하십시오. (GDR 공리: 자율 위임 의무)")

            # 4. Project Integrity Check (Project 파일 전용)
            if file_path.endswith(".pbxproj"):
                versions = re.findall(r"MARKETING_VERSION = (.*?);", content)
                unique_versions = set(versions)
                if len(unique_versions) > 1:
                    self.logger.log(f"버전 불일치 발견: {unique_versions}", 2)
                    results.append(f"⚠️ [Project] 타겟별 MARKETING_VERSION이 일치하지 않습니다. ({', '.join(unique_versions)})")

            status_msg = "✅ 진단 결과: 모든 규칙을 준수하고 있습니다! 역시 대장님 스타일입니다! 🚀" if not results else "\n".join(results)
            self.logger.log("진단 완료", 1)
            
            return [types.TextContent(
                type="text",
                text=f"🔍 [GDR Audit] {os.path.basename(file_path)}\n---\n{status_msg}"
            )]
            
        self.logger.log(f"알 수 없는 도구: {name}", 1)
        raise ValueError(f"GDR 테넌트에서 '{name}' 도구를 처리할 수 없습니다.")
