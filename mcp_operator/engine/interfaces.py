#
#  interfaces.py - MCP Operator Unified Interfaces (Protocol-Oriented)
#

import os
import json
from abc import ABC, abstractmethod
from typing import List, Optional, Any, Dict
from mcp_operator.common.utils import get_project_root, read_json_safely

class BaseComponent(ABC):
    """
    [Foundation] 모든 회선(Circuit)과 유닛(Unit)의 최상위 추상화 클래스입니다.
    JSON 기반의 규약 로딩 및 정체성 관리를 담당합니다.
    """
    def __init__(self, manager: Optional[Any] = None, logger: Optional[Any] = None) -> None:
        """BaseComponent 인스턴스를 초기화합니다.
        
        Args:
            manager (Optional[Any]): 회선/유닛을 관리하는 매니저 객체.
            logger (Optional[Any]): 시스템 로그를 기록할 로거 객체.
        """
        self.manager = manager
        self.logger = logger
        self.project_root: str = get_project_root()

    @abstractmethod
    def get_name(self) -> str:
        """구성 요소의 식별 명칭을 반환합니다."""
        pass

    def get_path(self) -> str:
        """구성 요소의 물리적 디렉토리 경로를 반환합니다.
        
        Returns:
            str: 구성 요소의 절대 경로.
        """
        return ""

    def load_overview(self) -> Dict[str, Any]:
        """overview.json 파일을 읽어 정보를 반환합니다.
        
        Returns:
            Dict[str, Any]: 오버뷰 메타데이터 정보.
        """
        path = os.path.join(self.get_path(), "overview.json")
        return read_json_safely(path) or {"name": self.get_name(), "description": "N/A"}

    def load_protocols(self) -> List[str]:
        """protocols.json 파일을 읽어 규약 리스트를 반환합니다.
        
        Returns:
            List[str]: 규약(RULES) 리스트.
        """
        path = os.path.join(self.get_path(), "protocols.json")
        data = read_json_safely(path)
        if isinstance(data, dict):
            return data.get("RULES", [])
        return []

class BaseProtocols(ABC):
    """[I18N] 다국어 행동 규약 인터페이스"""
    def __init__(self, circuit_manager: Optional[Any] = None, logger: Optional[Any] = None) -> None:
        """BaseProtocols 인스턴스를 초기화합니다.
        
        Args:
            circuit_manager (Optional[Any]): 회선 매니저 객체.
            logger (Optional[Any]): 로거 객체.
        """
        self.circuit_manager = circuit_manager
        self.logger = logger

    @classmethod
    @abstractmethod
    def get_rules(cls: Any) -> List[str]:
        """최상위 규약 리스트를 반환합니다."""
        pass

class BaseAuditor(ABC):
    """[QA] 물리적 코드 무결성 검증 인터페이스"""
    def __init__(self, logger: Optional[Any] = None) -> None:
        """BaseAuditor 인스턴스를 초기화합니다.
        
        Args:
            logger (Optional[Any]): 로거 객체.
        """
        self.logger = logger

    @abstractmethod
    def audit(self, file_path: str, content: str) -> List[str]:
        """규약 위반 사항 리스트를 반환합니다."""
        pass

class BaseUnit(BaseComponent, BaseAuditor):
    """
    [Specialist] 기술 전문가 유닛의 기본 구현체입니다.
    BaseComponent의 정체성과 BaseAuditor의 검증 능력을 동시에 가집니다.
    """
    def __init__(self, logger: Optional[Any] = None, manager: Optional[Any] = None) -> None:
        """BaseUnit 인스턴스를 초기화합니다.
        
        Args:
            logger (Optional[Any]): 로거 객체.
            manager (Optional[Any]): 매니저 객체.
        """
        BaseComponent.__init__(self, manager, logger)
        BaseAuditor.__init__(self, logger)

    def audit(self, file_path: str, content: str) -> List[str]:
        """기본 유닛의 감사 로직을 수행합니다. (기본적으로 무결성 통과)
        
        Args:
            file_path (str): 감사 대상 파일 경로.
            content (str): 파일의 실제 텍스트 내용.
            
        Returns:
            List[str]: 발견된 결함 리스트.
        """
        return []
