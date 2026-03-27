#
#  axioms.py - GolfzonCommon Rules
#

from language.swift.axioms import SwiftAxioms
from tenants.projects.golfzon.libraries.common.overview import Overview

class Axioms(SwiftAxioms):
    # --- [Paths] ---
    LIBRARY_ROOT = Overview.ROOT_PATH
    
    # --- [Core Philosophy] ---
    NICKNAME = "대장님"
    LANGUAGE = "Korean"
    
    # 라이브러리 전용 규칙
    CUSTOM_RULES = [
        "Singleton Access: 주요 유틸리티는 .shared 싱글톤으로 제공하여 상태 일관성 유지",
        "Framework Independent: 최대한 외부 의존성(CocoaPods 등)을 배제하고 순수 Swift/Foundation 위주로 구현",
        "Doc Comments Mandatory: 모든 public 인터페이스에는 '///' 형태의 문서화 주석 필수"
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
