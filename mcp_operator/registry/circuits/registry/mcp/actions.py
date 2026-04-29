#
#  actions.py - MCP Operator Core Controller (Unified Version)
#

from mcp_operator.registry.circuits.base import BaseCircuit

class McpCircuit(BaseCircuit):
    """[Unified Circuit] MCP 지휘부 컨트롤러입니다."""

    def __init__(self, manager=None):
        super().__init__(manager)
        self.units = ["python", "markdown", "sentinel", "planning"]

    def get_name(self) -> str:
        return "mcp"

    def get_tools(self) -> list:
        # 모든 도구는 CoreActions(Unified API)를 통해 제공됩니다.
        return []

    async def call_tool(self, name: str, arguments: dict) -> list:
        # 부모 클래스의 기본 호출 로직을 따릅니다.
        return await super().call_tool(name, arguments)
