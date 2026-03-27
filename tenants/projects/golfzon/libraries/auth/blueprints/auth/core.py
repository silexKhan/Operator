#
#  core.py - Auth Core Module Blueprint (GolfzonAuth)
#

class CoreSpec:
    NAME = "Auth/Core"
    DESC = "인증 매니저, 서비스, 스토리지 및 세션 관리의 핵심 엔진"
    PATH = "Sources/GolfzonAuth/auth"
    
    # --- [Core Architectural Flow] ---
    CORE_FLOW = {
        "1_Entry": "AuthManager.shared (싱글톤) 또는 인스턴스 주입을 통해 인증 요청 수행",
        "2_Request": "AuthService를 통해 골프존 인증 API 호출 (login, exchange, validate 등)",
        "3_Response": "서버 응답을 CertificationToken 모델로 변환하여 처리",
        "4_Storage": "인증 성공 시 AuthStorage(Keychain)에 토큰 영구 저장 및 AuthSession 상태 동기화",
        "5_Notification": "세션 변경 시 관련 알림을 전파하여 앱 전역의 로그인 상태 업데이트"
    }
    
    # --- [Key Components] ---
    COMPONENTS = {
        "Manager": {
            "class": "AuthManager",
            "desc": "인증 프로세스의 고수준 API 제공 (인터페이스: AuthManaging). ⚠️ 주의: getTokenForSessionID 메서드 누락 상태"
        },
        "Service": {
            "class": "AuthService",
            "desc": "Alamofire 기반의 순수 네트워크 요청 레이어. 모든 레거시 대응 통신 메서드(Exchange 등) 구현 완료"
        },
        "Session": {
            "class": "AuthSession",
            "desc": "현재 로그인된 유저의 상태(Status) 및 정보를 메모리상에 유지"
        },
        "Storage": {
            "class": "AuthStorage",
            "desc": "KeychainManager를 활용하여 민감 정보를 안전하게 영속화"
        }
    }

    # --- [Migration & Gaps] ---
    MIGRATION_KNOWLEDGE = {
        "Legacy_Mapping": "Authorizable 프로토콜의 모든 기능이 새 아키텍처로 이관됨 (MigrationMap.md 참조)",
        "Critical_Gap": "AuthManager 구현체에 getTokenForSessionID(sessionId:) 호출 로직이 누락되어 조치 필요",
        "Intentional_Removal": "ServiceValidator에서 UI(Alert) 로직이 제거되었으므로 클라이언트(View) 계층에서 결과에 따른 Alert 직접 구현 필수"
    }

    @classmethod
    def get_spec(cls):
        return {
            "name": cls.NAME,
            "desc": cls.DESC,
            "path": cls.PATH,
            "flow": cls.CORE_FLOW,
            "components": cls.COMPONENTS
        }
