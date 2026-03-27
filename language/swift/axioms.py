#
#  axioms.py - Standard Swift & MVVM Architecture Rules
#  (Level 2: Tenant Axioms - Software Engineering / Swift)
#

from shared.hub_axioms import HubAxioms

class SwiftAxioms(HubAxioms):
    """
    Swift 및 iOS 개발 도메인을 위한 테넌트 공리입니다.
    최상위 HubAxioms를 상속받아 기술 스택 특화 규칙을 정의합니다. 🍎🚀
    """

    # --- [Architecture Rules] ---
    DUMB_VIEW_REQUIRED = True
    SWR_MANDATORY = True
    NO_FORCED_UNWRAPPING = True
    
    # [대장님 🎯] Combine Naming: Private Subject와 Public Publisher는 동일 이름을 유지 (Subject 접미사 금지) 🛡️
    COMBINE_NAMING_STRICT = True 
    
    # [대장님 🎯] Safety First: fatalError 사용 금지. 누락 시 크래시 대신 유휴(Idle) 상태 유지 🚑
    NO_FATAL_ERROR = True 
    
    # [대장님 🎯] Extension: private extension 대신 개별 private 접근 제어 권장 🧼
    CLEAN_EXTENSION_STYLE = True 
    
    NO_UNNECESSARY_WEAK_SELF = True # 클로저 내 self 미사용 시 [weak self] 제거
    DEPENDENCY_INTEGRITY_REQUIRED = True # 인터페이스 수정 시 의존성 전수 수정 의무
    AUTONOMOUS_DELEGATION_REQUIRED = True # 대규모 작업 시 generalist 부사수 활용 의무
    
    # 선언적 프로그래밍 및 현대화 조항 🚀
    COMBINE_FRAMEWORK_PRIMARY = True 
    NO_IBACTION_ALLOWED = True 
    SWIFT6_CONCURRENCY_STRICT = True 
    
    # --- [Directory Hierarchy Rules] ---
    # [대장님(@silex) 🎯] 선호 구조: 기능/하위 도메인별 계층화 필수 준수 🚀
    STANDARD_DIRECTORY_LAYERS = [
        "protocol/",  # 인터페이스 및 Delegate 정의 (추상화 레이어) 📜
        "model/",     # 데이터 구조체 및 ViewModel (비즈니스 로직) 📦
        "enum/",      # 열거형 및 상수 정의 (상태 및 옵션) 🏷️
        "view/",      # UIViewController 및 메인 View (Root 위치 고려) 🖼️
        "cell/",      # UICollectionView/UITableViewCell (리스트 컴포넌트) 🎨
        "endpoint/",  # API 라우팅 및 경로 정의 (네트워크 주소) 📡
        "response/"   # API 응답 데이터 모델 (서버 데이터 구조) 📥
    ]
    
    @classmethod
    def get_rules(cls):
        """
        부모(HubAxioms)의 글로벌 규칙과 Swift 테넌트 전용 규칙을 재귀적으로 병합하여 반환합니다.
        """
        swift_rules = [
            "Strict MVVM (Dumb View)",
            "SWR Data Flow (Cache -> Server)",
            "Safety-First (No fatalError, Idle state over Crash) 🚑",
            "No Forced Unwrapping (!)",
            "Standardized Combine Naming (Same name for Private/Public, No 'Subject' Suffix) ⛓️",
            "Combine Framework Primary (Active Use Required) 🚀",
            "No @IBAction (Use Combine Binding Instead) 🛡️",
            "Clean Extension Style (Avoid private extension, use individual private) 🧼",
            "Data Model 1:1 Server Mapping (Lookup Friendly) 📥",
            "Swift 6 Concurrency (Explicit Capture in TaskGroup Required) 🏎️",
            "Documentation Mandatory (/// Doc Comments for methods) 📝",
            "📦 계층적 폴더 구조 준수 (protocol, model, enum, view, cell, endpoint, response)"
        ]
        # Level 1 (Global) + Level 2 (Tenant) 규칙 결합
        return super().get_rules() + swift_rules
