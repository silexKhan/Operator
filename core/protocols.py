#
#  protocols.py - Global Universal Protocols (Level 0) 📞⚡️
#

import os
from core.interfaces import BaseProtocols
from typing import List

class GlobalProtocols(BaseProtocols):
    """
    [대장님 🎯] 전 조직이 공통으로 준수해야 할 최상위 규약입니다.
    PROJECT_ROOT를 실행 시점에 동적으로 계산하여 이식성을 확보합니다. 🛡️⚡️
    """
    # 현재 파일 위치를 기준으로 프로젝트 루트 자동 감지 (core -> root)
    PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    GLOBAL_RULES = [
        "Protocol 0-1 (Mechanical Integrity): 코드/문서 내에 '...' 또는 '중략' 금지. 완전한 리터럴 텍스트 의무화.",
        "Protocol 0-2 (Preservation & Substitution): 기존의 유효한 정보는 보존 후 확장이 원칙이며, 삭제는 오직 더 정교한 내용으로의 대체가 확정되었을 때만 수행하여 기존 정보의 가치를 훼손하지 않는다.",
        "Protocol 0-3 (Standard Formatting): 모든 신규 규약 추가 시 최상위 규약의 명명 규격(번호, 이름, 서술)을 엄격히 준수하여 조직 전체의 일관성을 유지한다.",
        "Protocol 0-4 (Security First): 비밀번호, API Key, 개인정보 노출 금지. .env 또는 Secret 관리 권장.",
        "Protocol 0-5 (Explain Before Acting): 모든 작업 전 의도와 전략을 선제적으로 보고할 것.",
        "Protocol 0-6 (Safety First): 시스템 중단(Crash)이나 예외 유발 대신 유휴(Idle) 또는 안전한 예외 처리 지향.",
        "Protocol 0-7 (Proactive Specification): 모든 제안(Inquiry/Next Steps)은 반드시 구체적인 '예시(e.g.)'와 '기대 효과'를 포함하여 대장님의 의사결정을 지원할 것."
    ]

    @classmethod
    def get_rules(cls) -> List[str]:
        """최상위 규약 리스트를 반환합니다."""
        return cls.GLOBAL_RULES
