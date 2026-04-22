#
#  base.py - Base Circuit Definition (Unified 2.0)
#

from mcp_operator.engine.interfaces import BaseComponent, BaseAuditor
import mcp.types as types
from typing import Optional, Any, List

class BaseCircuit(BaseComponent):
    """
    [Commander] 모든 회선(Circuit)의 최상위 추상화 클래스입니다.
    유닛들을 지휘하고 통합 API의 실제 집행을 담당합니다.
    """
    def __init__(self, manager: Optional[Any] = None) -> None:
        """BaseCircuit 인스턴스를 초기화합니다.
        
        Args:
            manager (Optional[Any]): 회선 매니저 객체.
        """
        super().__init__(manager)
        self.inherit_global: bool = True
        self.units: List[str] = []

    def get_name(self) -> str:
        """[Abstract] 회선의 이름을 반환합니다. 하위 클래스에서 오버라이드해야 합니다.
        
        Returns:
            str: 회선 명칭.
        """
        return "base_circuit"

    def get_units(self) -> List[str]:
        """해당 회선에 배속된 전문 기술 유닛(Unit) 리스트를 반환합니다.
        
        Returns:
            List[str]: 유닛 명칭 리스트.
        """
        return self.units

    def get_protocols(self) -> Optional[Any]:
        """[Legacy Support] 규약 객체를 반환합니다.
        
        Returns:
            Optional[Any]: 규약 객체 또는 None.
        """
        return None

    def get_auditor(self) -> Optional[BaseAuditor]:
        """해당 회선 전용 감사기를 반환합니다.
        
        Returns:
            Optional[BaseAuditor]: 감사기 객체 또는 None.
        """
        return None

    def get_tools(self) -> List[types.Tool]:
        """회선 고유의 도구가 있을 경우 정의합니다. (통합 API 사용 시 비워둠)
        
        Returns:
            List[types.Tool]: 도구 명세 리스트.
        """
        return []

    async def call_tool(self, name: str, arguments: dict) -> List[types.TextContent]:
        """특수 도구 호출 시 로직을 수행합니다.
        
        Args:
            name (str): 호출할 도구 이름.
            arguments (dict): 도구 인자값.
            
        Returns:
            List[types.TextContent]: MCP 응답 결과.
        """
        return [types.TextContent(type="text", text=f" [Circuit: {self.get_name()}] '{name}' 도구는 코어에서 처리됩니다. ")]
