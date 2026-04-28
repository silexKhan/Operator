#
#  models.py - Shared Data Models (Strict Clean Architecture)
#

import json
from enum import Enum, unique
from pydantic import BaseModel, Field
from typing import TypeVar, Generic, Optional, Any, Union, List, Dict

T = TypeVar('T')

@unique
class CommandTarget(str, Enum):
    """[Specification] 통합 지휘 API의 관리 대상 정의 (P-6)"""
    ALL = "all"
    PROTOCOL = "protocol"
    OVERVIEW = "overview"
    BLUEPRINT = "blueprint"
    SPEC = "spec"
    MISSION = "mission"
    CIRCUIT = "circuit"
    UNIT = "unit"
    STATUS = "status"
    STATE = "state"
    GLOBAL_PROTOCOL = "global_protocol"

class UnifiedRequest(BaseModel):
    """[Specification] 통합 요청 스키마 (P-2)"""
    target: CommandTarget = Field(CommandTarget.ALL, description="조작 대상 객체 (기본값: all)")
    name: Optional[str] = Field(None, description="대상 객체의 이름 (회선명, 유닛명 등)")
    data: Optional[Dict[str, Any]] = Field(None, description="업데이트 또는 생성 시 전달할 데이터")
    context: Optional[Dict[str, Any]] = Field(None, description="조회 시 필터링 또는 추가 컨텍스트")

class DataOrigin(str, Enum):
    """[Specification] 데이터의 출처 정의"""
    CACHE = "cache"
    SERVER = "server"

class FetchResult(BaseModel, Generic[T]):
    """[Specification] 데이터 엔티티 래퍼"""
    entity: T
    origin: DataOrigin

# -------------------------------------------------------------------------
# [Handlers] MCP 응답 처리 엔진 (Protocol P-4)
# -------------------------------------------------------------------------

def TextResponse(text: str) -> List[Any]:
    """[Handler] 평문을 MCP TextContent 리스트로 변환"""
    import mcp.types as types
    return [types.TextContent(type="text", text=text)]

def JsonResponse(data: Any, indent: int = 4) -> List[Any]:
    """[Handler] 객체를 JSON MCP 리스트로 변환"""
    import mcp.types as types
    json_str = json.dumps(data, indent=indent, ensure_ascii=False)
    return [types.TextContent(type="text", text=json_str)]

class ResponseHandler:
    """[Main Class] 응답 핸들러 클래스"""
    text = staticmethod(TextResponse)
    json = staticmethod(JsonResponse)
