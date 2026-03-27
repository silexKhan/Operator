#
#  axioms.py - GDR Project Rules & Path Constants
#

import os
from language.swift.axioms import SwiftAxioms
from tenants.projects.golfzon.gdr.overview import Overview

class Axioms(SwiftAxioms):
    # --- [Paths] ---
    PROJECT_ROOT = Overview.ROOT_PATH
    LEGACY_ROOT = Overview.LEGACY_PATH
    DEPLOY_SCRIPT = os.path.join(PROJECT_ROOT, "deploy.sh")
    
    # --- [Project Specs] ---
    # [대장님 🎯] 최소 지원 버전 iOS 15.0 확인 완료 🚀
    MIN_IOS_VERSION = "15.0" 
    
    # --- [Core Philosophy] ---
    NICKNAME = "대장님"
    LANGUAGE = "Korean"
    
    # [대장님 🎯] GDR 전용 커스텀 규칙 (하네스 엔지니어링 및 비즈니스 맥락 강화 🛡️)
    # 표준 규칙 외에 GDR 프로젝트에만 특화된 핵심 공리입니다. ✨
    CUSTOM_RULES = [
        "SWR Data Flow (Cache -> Server) 필수 준수",
        "Legacy Code 참조 시 전용 브릿지 사용",
        "Combine Subject 명명 시 'Subject' 접미사 사용 금지",
        "🛡️ GTM 서비스 선셋: GTM 시스템은 선셋되었으며 안정성을 위해 코드만 유지 중. (일부 API는 GDR과 혼용되니 분석 시 주의)",
        "📱 iOS 15+ 최신 API 적극 활용 (UISheetPresentationController 등 시스템 순정 기능 우선 권장)",
        "🖼️ Asset Prefix Mandatory: Xcode 15 심볼 충돌 방지를 위해 도메인 접두사 필수 (예: ico_nasmo_*)",
        "📡 Global Error Pattern: 전역 비즈니스 이벤트(401 인증 만료 등)는 Stepper/Navigator 중앙 처리 필수",
        "📝 CPS Framework: 모든 작업 전 [현상-원인-해결책] 순으로 대장님께 분석 보고 후 승인 득할 것"
    ]
    
    @classmethod
    def get_rules(cls):
        # Level 1 + Level 2 + Level 3(GDR Custom) 규칙 재귀적 결합
        return super().get_rules() + cls.CUSTOM_RULES

    @classmethod
    def get_summary(cls):
        briefing = Overview.get_briefing()
        return {
            "name": briefing["project"],
            "rules": cls.get_rules()
        }
