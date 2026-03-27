#
#  axioms.py - GolfzonNasmo Rules
#

from language.swift.axioms import SwiftAxioms
from tenants.projects.golfzon.libraries.nasmo.overview import Overview

class Axioms(SwiftAxioms):
    # --- [Paths] ---
    LIBRARY_ROOT = Overview.ROOT_PATH
    
    # --- [Core Philosophy] ---
    NICKNAME = "대장님"
    LANGUAGE = "Korean"
    
    # 라이브러리 전용 규칙
    CUSTOM_RULES = [
        "AVPlayer Optimization: 비디오 로딩 및 재생 시 AVPlayer의 리소스를 효율적으로 관리하고 캐싱 활용",
        "Sync Integrity: Dual 모드에서 두 영상 간의 프레임 단위 동기화(Sync) 정확성 보장",
        "Declarative Drawing: 드로잉 레이어는 Shape 객체를 통해 선언적으로 관리하며 실행 취소(Undo) 지원",
        "Modular Player: PlayerView와 ControllView를 분리하여 다양한 레이아웃에 대응 가능하도록 설계"
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
