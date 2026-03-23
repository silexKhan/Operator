#
#  base.py - Base Tenant Definition
#

from abc import ABC, abstractmethod
import mcp.types as types

class BaseTenant(ABC):
    @abstractmethod
    def get_name(self) -> str:
        pass

    @abstractmethod
    def get_tools(self) -> list[types.Tool]:
        pass

    @abstractmethod
    async def call_tool(self, name: str, arguments: dict) -> list[types.TextContent]:
        pass
