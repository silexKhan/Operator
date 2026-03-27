#
#  initializer.py - Initializer (Splash) Module Blueprint (GDR)
#

class InitializerSpec:
    NAME = "View/Initializer"
    DESC = "앱 진입 시의 스플래시 화면 및 초기화 시퀀스(보안, 업데이트, 인증) 제어"
    PATH = "GDR/view/initializer"
    
    # --- [Core Architectural Flow] ---
    # View.didAppear -> VM.handleDidAppear -> [1. Security] -> [2. Service] -> [3. Auth/Legacy] -> [4. Navigation]
    CORE_FLOW = {
        "1_Security_Check": "JailbreakDetector.isJailbrokenAsync() -> 탈옥 감지 시 즉시 앱 종료(exit 1)",
        "2_Service_Validate": "ServiceValidator.validateService() 호출 -> 점검(Maintenance), 강제업데이트(Forced), 권장업데이트(Recent), 정상(Normal) 상태 판별 및 UI 대응",
        "3_Splash_Resource": "NetworkService(SWR)를 통해 SplashEndpoint 호출 -> 최신 스플래시 URL 획득 및 UIImageView 업데이트 (UserDefaults 저장)",
        "4_Auth_Sequence": "migrateLegacyTokenIfNeeded(KeyChain: jwt_codable_key) -> authManager.validate() (토큰 갱신) -> authManager.info() (상세 정보 획득)",
        "5_Session_Sync": "PRIME.shared에 accessToken 및 GZ_SESSION_ID 주입하여 하이브리드(웹뷰) 환경 동기화",
        "6_Navigation": "최종 인증 상태에 따라 .main 또는 .login으로 이동 (Splash 노출을 위해 1.0s 의도적 지연 적용)"
    }
    
    # --- [Key Components] ---
    COMPONENTS = {
        "View": {
            "class": "Initializer",
            "desc": "Dumb View. viewDidLoad/viewDidAppear 이벤트를 VM에 전달하고, Output(이미지, 알럿, 라우팅)을 바인딩"
        },
        "ViewModel": {
            "class": "InitializerViewModel",
            "desc": "초기화 시퀀스의 핵심 두뇌. 보안, 네트워크, 인증, 세션 마이그레이션을 총괄 오케스트레이션"
        },
        "Service_Validators": {
            "JailbreakDetector": "비동기 탈옥 감지 엔진",
            "ServiceValidator": "서버 점검 및 앱 버전 유효성 검사기",
            "AuthManager": "인증/세션 관리 및 레거시 토큰 교환(Exchange) 담당"
        }
    }

    # --- [Detailed Initialization Logic] ---
    INITIALIZATION_TASKS = {
        "Legacy_Migration": {
            "Target": "Keychain: jwt_codable_key (기존 GDR 유저)",
            "Action": "exchangeAccessToken을 호출하여 신규 인증 라이브러리 세션으로 자동 전환",
            "Cleanup": "마이그레이션 성공 시 레거시 키체인 데이터 삭제 (Sweep)"
        },
        "Session_PRIME_Sync": {
            "Action": "인증 성공 후 PRIME.shared.accessToken 및 headerField 업데이트",
            "Purpose": "Native-Web 간 세션 공유 및 API 호출 시 공통 헤더 보장"
        },
        "SWR_Splash_Strategy": {
            "Action": "NetworkService.fetch(endpoint: SplashEndpoint) 사용",
            "Benefit": "캐시된 이미지를 즉시 보여주면서 서버의 최신 이미지를 백그라운드에서 갱신"
        }
    }

    @classmethod
    def get_spec(cls):
        return {
            "name": cls.NAME,
            "desc": cls.DESC,
            "path": cls.PATH,
            "flow": cls.CORE_FLOW,
            "components": cls.COMPONENTS,
            "logic": cls.LOGIC
        }
