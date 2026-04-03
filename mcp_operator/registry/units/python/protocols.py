#
#  protocols.py - Standard Python & MCP Architecture Rules (Hot Sync)
#  (Level 2: Unit Protocols - Software Engineering / Python)
#

import os
import json

class PythonProtocols:
    """
    [사용자] Python 유닛 전용 전문 기술 수칙입니다.
    데이터 무결성을 위해 실시간으로 protocols.json에서 정보를 로드합니다. 
    """
    
    @classmethod
    def _load_data(cls):
        """[사용자] 물리적 JSON 파일을 직접 읽어 실시간성을 확보합니다."""
        base_dir = os.path.dirname(os.path.abspath(__file__))
        json_path = os.path.join(base_dir, "protocols.json")
        try:
            with open(json_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return {"OVERVIEW": "", "RULES": []}

    @property
    def OVERVIEW(self):
        return self._load_data().get("OVERVIEW", "")

    @classmethod
    def get_rules(cls):
        """[사용자] 런타임에 JSON 데이터를 반환하여 웹 대시보드와 AI의 동기화를 보장합니다."""
        return cls._load_data().get("RULES", [])
