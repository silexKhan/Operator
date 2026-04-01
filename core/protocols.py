#
#  protocols.py - Global Universal Protocols (Level 0) 
#

import os
from core.interfaces import BaseProtocols
from typing import List
from shared.utils import get_project_root, read_json_safely

class GlobalProtocols(BaseProtocols):
    """
    [사용자] 전 조직이 공통으로 준수해야 할 최상위 규약입니다.
    PROJECT_ROOT를 실행 시점에 동적으로 계산하여 이식성을 확보합니다. 
    """
    # 현재 파일 위치를 기준으로 프로젝트 루트 자동 감지
    PROJECT_ROOT = get_project_root()

    @classmethod
    def get_rules(cls) -> List[str]:
        """최상위 규약 리스트를 실시간으로 JSON 파일에서 로드하여 반환합니다."""
        # PROJECT_ROOT를 기준으로 동적 경로 생성
        json_path = os.path.join(cls.PROJECT_ROOT, "core", "protocols.json")
            
        try:
            if not os.path.exists(json_path):
                return [f"Protocol 0-0: 파일을 찾을 수 없습니다 (Path: {json_path})"]
            
            data = read_json_safely(json_path)
            return data.get("GLOBAL_RULES", [])
        except Exception as e:
            # 파일이 없거나 오류 발생 시 최소한의 기본 규칙 반환
            return [f"Protocol 0-0: 로드 실패 ({type(e).__name__}: {str(e)} at {json_path})"]
