#
#  axioms.py - GDR Project Rules & Path Constants
#

import os

class GDRAxioms:
    # --- [Paths] ---
    PROJECT_ROOT = "/Users/silex/workspace/project/GDR"
    LEGACY_ROOT = "/Users/silex/workspace/project/legacy/legacy_gdr"
    DEPLOY_SCRIPT = os.path.join(PROJECT_ROOT, "deploy.sh")
    
    # --- [Architecture Rules] ---
    DUMB_VIEW_REQUIRED = True
    SWR_MANDATORY = True
    NO_FORCED_UNWRAPPING = True
    COMBINE_NAMING_STRICT = True # No 'Subject' suffix
    NO_UNNECESSARY_WEAK_SELF = True # 클로저 내 self 미사용 시 [weak self] 제거
    DEPENDENCY_INTEGRITY_REQUIRED = True # 인터페이스 수정 시 의존성 전수 수정 의무
    AUTONOMOUS_DELEGATION_REQUIRED = True # 대규모 작업 시 generalist 부사수 활용 의무
    
    # --- [Core Philosophy] ---
    NICKNAME = "대장님"
    LANGUAGE = "Korean"
    
    @staticmethod
    def get_summary():
        return {
            "name": "GDR (Golfzon Driving Range)",
            "rules": [
                "Strict MVVM (Dumb View)",
                "SWR Data Flow (Cache -> Server)",
                "Safety-First (No Forced Unwrapping)",
                "Standardized Combine Naming",
                "[weak self] Optimization (No weak self if self is unused)",
                "Dependency Integrity (Recursive Update Required)",
                "Autonomous Delegation (Use 'generalist' for large tasks)"
            ]
        }
