#
#  models.py - Shared Data Models (Strict Clean Architecture)
#

import json
from enum import Enum
from pydantic import BaseModel
from typing import TypeVar, Generic, Optional, Any, Union, List, Dict

T = TypeVar('T')

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
