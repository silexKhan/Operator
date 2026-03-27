#
#  axioms.py - GolfzonVision Rules
#

from language.swift.axioms import SwiftAxioms
from tenants.projects.golfzon.libraries.vision.overview import Overview

class Axioms(SwiftAxioms):
    # --- [Paths] ---
    LIBRARY_ROOT = Overview.ROOT_PATH
    
    # --- [Core Philosophy] ---
    NICKNAME = "대장님"
    LANGUAGE = "Korean"
    
    # 라이브러리 전용 규칙
    CUSTOM_RULES = [
        "PRIME Integration: 모든 하이브리드 요청 시 PRIME.shared의 토큰과 UA를 필수적으로 주입",
        "Process Pool Sharing: 세션 공유를 위해 VisionWKWebViewController.processPool 정적 인스턴스를 반드시 사용",
        "Declarative JS Bridge: 자바스크립트 브릿지 로직은 Executer 클래스의 Behaviors Enum을 통해 선언적으로 확장",
        "Subclass Interception: 특정 도메인 로직은 requestedUrl() 오버라이딩을 통해 서브클래스에서 가로채기 지원"
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
