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
