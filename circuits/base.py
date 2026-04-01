#
#  base.py - Base Circuit Definition 
#

from abc import ABC, abstractmethod
from shared.models import TextResponse
import mcp.types as types
from typing import Optional, Any
from core.interfaces import BaseProtocols, BaseAuditor

class BaseCircuit(ABC):
    """
    [사용자] 모든 회선(Circuit)의 최상위 추상화 클래스입니다. 
    inherit_global 속성을 통해 상위 규약 상속 여부를 결정합니다. 
    """
    def __init__(self, manager=None):
        self.manager = manager
        # [사용자] 기본값은 상속 허용(True)입니다.
        self.inherit_global = True
        # [사용자] 기본 배속된 유닛(Unit)은 비어있습니다.
        self.units = []

    def get_units(self) -> list[str]:
        """해당 회선에 배속된 전문 기술 유닛(Unit) 리스트를 반환합니다."""
        return self.units

    @abstractmethod
    def get_name(self) -> str:
        """회선의 식별 명칭을 반환합니다."""
        pass

    def get_protocols(self) -> Optional[Any]:
        """해당 회선에서 준수해야 할 규약(Protocols) 리스트를 반환합니다."""
        return None

    def get_dependencies(self) -> list[str]:
        """해당 회선이 의존하는 다른 회선(Circuit)들의 이름 리스트를 반환합니다."""
        return []

    def get_auditor(self) -> Optional[BaseAuditor]:
        """해당 회선의 규약 준수 여부를 검증하는 감사기를 반환합니다."""
        return None

    @abstractmethod
    def get_tools(self) -> list[types.Tool]:
        """회선이 외부(AI)에 제공하는 가용 행동(Tools) 리스트를 반환합니다."""
        pass

    @abstractmethod
    async def call_tool(self, name: str, arguments: dict) -> list[types.TextContent]:
        """회선의 특정 도구를 호출합니다."""
        pass
