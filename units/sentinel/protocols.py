#
#  protocols.py - Mission Objective & Evaluation Integrity Protocols
#  (Level 2: Unit Protocols - Sentinel / Harness Loop)
#

import os
import json

class SentinelProtocols:
    """센티널 유닛 전용 목적 달성 및 평가 무결성 수칙입니다.

    대장님(사용자)의 의도가 결과물에 100% 반영될 때까지
    작업 루프를 제어하고 품질을 보증하는 센티널 유닛 전용 행동 지침입니다.
    """
    
    def __init__(self) -> None:
        """SentinelProtocols 인스턴스를 초기화합니다."""
        self.protocol_path: str = os.path.join(os.path.dirname(__file__), "protocols.json")

    def get_overview(self) -> str:
        """센티널 유닛의 개요(OVERVIEW)를 JSON 파일에서 로드하여 반환합니다.

        Returns:
            str: 센티널 유닛의 개요 문자열.
        """
        with open(self.protocol_path, 'r', encoding='utf-8') as f:
            data: dict = json.load(f)
            return data.get("OVERVIEW", "")

    def get_rules(self) -> list[str]:
        """센티널 유닛의 구체적인 행동 규약 리스트를 JSON 파일에서 로드하여 반환합니다.

        Returns:
            list[str]: S-1부터 S-4까지 정의된 센티널 행동 규약 문자열 리스트.
        """
        with open(self.protocol_path, 'r', encoding='utf-8') as f:
            data: dict = json.load(f)
            return data.get("RULES", [])
