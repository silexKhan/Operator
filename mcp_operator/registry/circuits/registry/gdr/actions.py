#  actions.py - GDR Domain Actions (Unified Version)
from mcp_operator.registry.circuits.base import BaseCircuit

class GdrCircuit(BaseCircuit):
    """[Unified Circuit] GDR 프로젝트를 관리하는 회선입니다."""
    
    def __init__(self, manager=None):
        super().__init__(manager)
        self.units = ["markdown", "sentinel", "swift", "python"]

    def get_name(self) -> str: 
        return "gdr"

    def get_protocols(self):
        from .protocols import Protocols
        return Protocols

    def get_tools(self) -> list:
        # 모든 도구는 CoreActions를 통해 통합 제공됩니다.
        return []

    async def call_tool(self, name: str, arguments: dict) -> list:
        # 특수한 GDR 전용 로직이 필요한 경우만 오버라이드합니다.
        return await super().call_tool(name, arguments)

    def get_blueprint(self):
        from .blueprint import BluePrint
        return BluePrint()
