#
#  protocols.py - Global Universal Protocols (Level 0) 
#

import os
from mcp_operator.engine.interfaces import BaseProtocols
from typing import List
from mcp_operator.common.utils import get_project_root, read_json_safely

class GlobalProtocols(BaseProtocols):
    """
    [사용자] 전사 지배 규약(Global Protocols)입니다.
    데이터 무결성을 위해 operator/engine/protocols.json 파일에서 실시간으로 로드합니다.
    """
    PROJECT_ROOT = get_project_root()

    @classmethod
    def get_rules(cls) -> List[str]:
        """[사용자] 물리적 JSON 파일을 직접 읽어 전사 규약을 반환합니다 (Hot Sync)."""
        json_path = os.path.join(cls.PROJECT_ROOT, "operator", "engine", "protocols.json")
        try:
            data = read_json_safely(json_path)
            # [대장님 지침 🎯] 단일화된 RULES 필드에서 데이터를 추출합니다. 🚀
            return data.get("RULES", [])
        except Exception as e:
            # 파일이 없거나 오류 발생 시 최소한의 기본 규칙 반환
            return [f"Protocol 0-0: 로드 실패 ({type(e).__name__}: {str(e)} at {json_path})"]
