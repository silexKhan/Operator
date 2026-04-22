#
#  actions.py - Research Domain Actions (Unified Version)
#

from mcp_operator.registry.circuits.base import BaseCircuit
from .protocols import Protocols
from .overview import Overview

class ResearchCircuit(BaseCircuit):
    """[Unified Circuit] 리서치 도메인을 관리하는 회선입니다."""
    
    def __init__(self, manager=None):
        super().__init__(manager)
        # Overview에 정의된 전문 유닛들을 동적으로 배속합니다. 
        self.units = getattr(Overview, "UNITS", [])

    def get_name(self) -> str: 
        return "research"

    def get_protocols(self): 
        return Protocols

    def get_tools(self) -> list:
        # 모든 도구는 CoreActions(Unified API)를 통해 제공되므로 더 이상 개별 정의하지 않습니다.
        return []

    async def call_tool(self, name: str, arguments: dict) -> list:
        # 회선 전용 특수 로직이 필요한 경우에만 이곳에 구현합니다.
        # 현재는 모든 요청을 부모(BaseCircuit)에게 위임하거나 Core에서 처리하게 합니다.
        return await super().call_tool(name, arguments)
