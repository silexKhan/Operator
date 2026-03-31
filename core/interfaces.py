#
#  interfaces.py - Operator (교환) Standard Interfaces 📞⚡️
#

from abc import ABC, abstractmethod
from typing import List, Optional

class BaseProtocols(ABC):
    """
    [대장님 🎯] 모든 직군(기획/디자인/개발)의 표준 가이드라인(Protocols) 클래스의 부모입니다. 🛡️⚡️
    기존의 Axiom 개념을 계승하며, AI 모델의 행동 규약을 정의합니다.
    """
    def __init__(self, circuit_manager=None, logger=None):
        self.circuit_manager = circuit_manager
        self.logger = logger

    @classmethod
    @abstractmethod
    def get_rules(cls) -> List[str]:
        """최상위 규약 리스트를 반환합니다."""
        pass

class BaseAuditor(ABC):
    """
    [대장님 🎯] 소스 코드가 규약(Protocols)을 준수하는지 검사하는 엔진의 인터페이스입니다.
    """
    def __init__(self, logger=None):
        self.logger = logger

    @abstractmethod
    def audit(self, file_path: str, content: str) -> List[str]:
        """규약 위반 사항 리스트를 반환합니다."""
        pass
