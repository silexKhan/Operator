#
#  axioms.py - GolfzonAuth Rules
#

from language.swift.axioms import SwiftAxioms
from tenants.projects.golfzon.libraries.auth.overview import Overview

class Axioms(SwiftAxioms):
    # --- [Paths] ---
    LIBRARY_ROOT = Overview.ROOT_PATH
    
    # --- [Core Philosophy] ---
    NICKNAME = "대장님"
    LANGUAGE = "Korean"
    
    # 라이브러리 전용 규칙
    CUSTOM_RULES = [
        "Protocol-Oriented: 주요 로직(Manager, Service)은 프로토콜을 통해 정의하여 테스트 용이성 확보",
        "Stateless Service: AuthService는 상태를 가지지 않으며 순수하게 API 요청만 수행",
        "Secure Storage: 토큰 등 민감 정보는 반드시 KeychainManager를 통해 암호화 저장",
        "Async/Await Mandatory: 신규 비동기 로직은 반드시 Swift Concurrency(Async/Await) 사용"
    ]
    
    @classmethod
    def get_rules(cls):
        return super().get_rules() + cls.CUSTOM_RULES
    
    @classmethod
    def get_summary(cls):
        briefing = Overview.get_briefing()
        return {
            "name": briefing["library"],
            "rules": cls.get_rules()
        }
