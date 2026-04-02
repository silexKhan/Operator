#
#  actions.py - Research Domain Actions
#

from shared.models import TextResponse, JsonResponse
import mcp.types as types
import os
from circuits.base import BaseCircuit
from .protocols import Protocols
from .overview import Overview
from core.logger import OperatorLogger

class ResearchCircuit(BaseCircuit):
    def __init__(self, manager=None):
        super().__init__(manager)
        self.logger = OperatorLogger("ResearchCircuit")
        # Overview에 정의된 전문 유닛들을 동적으로 배속합니다. 
        self.units = Overview.UNITS

    def get_name(self) -> str: return "Research"
    def get_protocols(self): return Protocols
    def get_auditor(self):
        # [사용자] 리서치 회선에 적합한 오디터를 설정합니다. (기본은 MarkdownAuditor 추천)
        from units.markdown.auditor import MarkdownAuditor
        return MarkdownAuditor(self.logger)

    def get_tools(self) -> list[types.Tool]:
        # 리서치 회선 고유의 도구들을 정의합니다.
        return [
            types.Tool(name="research_get_overview", description="리서치 회선 요약 및 현재 탐구 목표 확인", inputSchema={"type": "object", "properties": {}}),
            types.Tool(name="research_get_protocols", description="리서치 심화 규약 조회", inputSchema={"type": "object", "properties": {}}),
            types.Tool(name="research_analyze_topic", description="특정 주제에 대한 다각도 심층 분석 수행", inputSchema={"type": "object", "properties": {"topic": {"type": "string"}, "depth": {"type": "integer", "default": 3}}, "required": ["topic"]})
        ]

    async def call_tool(self, name: str, arguments: dict) -> list[types.TextContent]:
        # 도구 분기 처리
        if name == "research_get_overview":
            res = f" [RESEARCH OVERVIEW]\n- Role: {Overview.ROLE}\n- Goal: {Overview.DESCRIPTION}\n- Units: {', '.join(self.units)}"
            return TextResponse(res)
        
        elif name == "research_get_protocols":
            res = " [RESEARCH PROTOCOLS]\n" + "\n".join(Protocols.RULES)
            return TextResponse(res)

        elif name == "research_analyze_topic":
            topic = arguments.get("topic", "")
            depth = arguments.get("depth", 3)
            # 실제 분석 로직은 여기서 수행되거나 다른 유닛에 위임됩니다.
            res = f" '{topic}' 주제에 대해 {depth}단계 깊이로 리서치를 시작합니다. (Markdown Unit 가동)"
            return TextResponse(res)

        return TextResponse(f" 알 수 없는 도구: {name}")
