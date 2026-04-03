#
#  protocols.py - MCP 프로젝트 전용 규약 (Auto-Detect Path) 
#

import os
import json
from mcp_operator.common.utils import read_json_safely

class Protocols:
    PROJECT_NAME = "Operator (교환)"
    
    @classmethod
    def get_rules(cls) -> list:
        """[사용자] 물리적 protocols.json 파일을 직접 읽어 실시간 규약을 반환합니다."""
        current_dir = os.path.dirname(os.path.abspath(__file__))
        json_path = os.path.join(current_dir, "protocols.json")
        data = read_json_safely(json_path)
        return data.get("RULES", [])

    @classmethod
    def get_summary(cls) -> dict:
        return {
            "name": cls.PROJECT_NAME,
            "rules": cls.get_rules()
        }
