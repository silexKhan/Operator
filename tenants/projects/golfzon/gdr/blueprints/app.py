#
#  app.py - App Core Lifecycle & Navigation Blueprint (GDR)
#

class AppSpec:
    NAME = "App/Core"
    DESC = "앱의 생명주기 제어(Shell vs Brain) 및 네비게이션 명세"
    PATH = "GDR/app"
    
    # --- [Core Architectural Flow] ---
    # [시스템 이벤트] -> [Delegate (Shell)] -> [Stepper (Brain)] -> [각종 서비스/네비게이터 호출]
    CORE_FLOW = {
        "Process_Control": "AppDelegate (Event) -> AppStepper (Logic: Config, Firebase, UA, Vision Dispatcher)",
        "UI_Control": "SceneDelegate (Event) -> SceneStepper (Logic: Theme, Session, Push, DeepLink)",
        "Navigation_Flow": "Stepper/VM -> AppNavigator (Execute) -> AppRoute -> UIWindow/NavController",
    }
    
    # --- [Key Components] ---
    COMPONENTS = {
        "Delegates_Shell": {
            "AppDelegate": "시스템 프로세스 이벤트 수신처. AppStepper에 모든 로직 위임",
            "SceneDelegate": "UI 윈도우/씬 이벤트 수신처. SceneStepper와 AppNavigator를 조합하여 UI 흐름 제어"
        },
        "Steppers_Brain": {
            "AppStepper": "앱 전체의 '시스템 엔진'. 서비스 초기화, 전역 설정, APNS 등록 등 비독립적 로직 총괄",
            "SceneStepper": "개별 화면의 '비즈니스 엔진'. 세션 유효성, 테마 동기화, 푸시 데이터 해석 등 UI 연관 로직 총괄"
        },
        "Navigation_Engine": {
            "AppNavigator": "화면 전환 실행자. Window와 NavController를 직접 핸들링하는 Thread-Safe 네비게이터",
            "AppRoute": "앱의 모든 이동 경로(Destination)를 정의한 마스터 Enum"
        }
    }

    # --- [Specific Logic] ---
    LOGIC = {
        "UserAgent_Assembly": "AppStepper가 WKWebView를 통해 시스템 UA 획득 후 GDR 커스텀 UA 조립 (PRIME 주입)",
        "Session_Integrity": "SceneStepper가 didBecomeActive 시점에 AuthManager를 통해 토큰 유효성 강제 체크",
        "Hybrid_Routing": "AppStepper 초기화 시 HybridRouteDispatcher를 설정하여 웹-네이티브 간 브릿지 통로 개설"
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
