#
#  auditor.py - Mission Objective Compliance Auditor
#

import os
import json
from core.interfaces import BaseAuditor

class SentinelAuditor(BaseAuditor):
    """설정된 미션 목적과 소스 코드의 일치성을 검사하는 감시관 유닛입니다.

    대장님(사용자)의 의도가 최종 산출물에 정확히 반영되었는지
    미션 데이터를 기반으로 기술적, 논리적 무결성을 검증합니다.
    """

    def __init__(self, logger: object = None, circuit_manager: object = None) -> None:
        """SentinelAuditor 인스턴스를 초기화합니다.

        Args:
            logger (object, optional): 시스템 로그를 기록할 로거 인스턴스. Defaults to None.
            circuit_manager (object, optional): 회선 관리 객체. Defaults to None.
        """
        super().__init__(logger)
        self.circuit_manager = circuit_manager
        # 프로젝트 루트 경로 확보
        self.project_root: str = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

    def audit(self, file_path: str, content: str = "") -> list[str]:
        """주어진 파일 경로와 내용을 미션 목적과 대조하여 감사를 수행합니다.

        Args:
            file_path (str): 감사를 수행할 대상 파일의 경로.
            content (str, optional): 파일의 리터럴 텍스트 내용. Defaults to "".

        Returns:
            list[str]: 감사 결과 리스트. 실패 시 사유를 포함하며 성공 시 빈 리스트를 반환합니다.

        Raises:
            FileNotFoundError: mission.json 파일이 존재하지 않을 경우.
        """
        results: list[str] = []
        mission_path: str = os.path.join(self.project_root, "mission.json")

        # 1. 미션 설정 여부 확인 (Protocol S-1)
        if not os.path.exists(mission_path):
            results.append(" FAIL: Protocol S-1 (Sentinel) - 'sentinel_set_mission'이 선행되지 않았습니다. ")
            return results

        try:
            with open(mission_path, "r", encoding="utf-8") as f:
                mission_data: dict = json.load(f)
                objective: str = mission_data.get("objective", "")
                criteria: list[str] = mission_data.get("criteria", [])
                status: str = mission_data.get("status", "IN_PROGRESS")

            # 2. 미션 성공 기준 대조 (Protocol S-2)
            for criterion in criteria:
                if criterion.lower() not in content.lower() and status != "PASS":
                     results.append(f" [Sentinel Check] 미션 기준 [{criterion}] 누락 위험이 감지되었습니다. ")

            # 3. 금지 표현 검사 (Global Protocol 0-1 연동)
            # Sentinel의 자기 참조 감시를 피하기 위해 금지 단어를 분할하여 체크합니다.
            forbidden_words: list[str] = ["." + ".." , "중" + "략", "생" + "략"]
            for word in forbidden_words:
                if word in content:
                    results.append(f" FAIL: Protocol S-2 (Sentinel) - 완전하지 않은 구현({word})은 센티널을 통과할 수 없습니다. ")

        except Exception as e:
            results.append(f" FAIL: 미션 데이터 로드 중 오류 발생: {str(e)}")

        return results
