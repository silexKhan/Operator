#
#  models.py - Shared Data Models
#

from enum import Enum
from pydantic import BaseModel
from typing import TypeVar, Generic, Optional

T = TypeVar('T')

class DataOrigin(str, Enum):
    CACHE = "cache"
    SERVER = "server"

class FetchResult(BaseModel, Generic[T]):
    entity: T
    origin: DataOrigin

def TextResponse(text: str) -> list:
    """
    mcp.types.TextContent 객체를 단일 리스트에 담아 반환하는 Helper입니다.
    가장 빈번하게 사용되는 형태인 `[types.TextContent(type="text", text="...")]`를 간소화합니다.
    """
    import mcp.types as types
    return [types.TextContent(type="text", text=text)]

def JsonResponse(data: Any, indent: int = 4) -> list:
    """
    파이썬 객체(dict, list 등)를 JSON 문자열로 변환하여 mcp.types.TextContent 객체 리스트로 반환합니다.
    모든 JSON 응답의 인코딩(ensure_ascii=False)과 들여쓰기를 통일합니다.
    """
    import mcp.types as types
    import json
    return [types.TextContent(type="text", text=json.dumps(data, indent=indent, ensure_ascii=False))]
