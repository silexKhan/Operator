#
#  base.py - Base Tenant Definition
#

from abc import ABC, abstractmethod
import mcp.types as types

class BaseTenant(ABC):
    @abstractmethod
    def get_name(self) -> str:
        pass

    def get_dependencies(self) -> list[str]:
        """이 테넌트가 의존하는 타 테넌트 이름 리스트를 반환합니다."""
        return []

    @abstractmethod
    def get_tools(self) -> list[types.Tool]:
        pass

    @abstractmethod
    async def call_tool(self, name: str, arguments: dict) -> list[types.TextContent]:
        pass
