#
#  main.py - Main TabBar & Dashboard Module Blueprint (GDR)
#

class MainSpec:
    NAME = "View/Main"
    DESC = "앱의 메인 허브인 탭바 컨트롤러 및 진입 시 팝업 시퀀스 제어"
    PATH = "GDR/view/main"
    
    # --- [Core Architectural Flow] ---
    # Scene.switchRoot(Main) -> MainTabBarVC.viewDidAppear -> VM.checkPopupSequence -> [1. Permission] -> [2. PushAgree] -> [3. Banner]
    CORE_FLOW = {
        "1_Root_Entry": "Main.storyboard 로드 -> MainTabBarViewController가 윈도우의 rootViewController로 설정됨",
        "2_Popup_Orchestration": "viewDidAppear 시점에 뷰모델의 팝업 체인(Sequence) 시작. 한 번에 하나씩 순차적으로 노출",
        "3_Permission_Gate": "UserDefaults에 'App_Permission'이 없으면 최우선으로 권한 가이드 팝업 노출",
        "4_Push_Symmetry": "서버의 알람 설정 데이터를 확인하여 'eventNoticeAgreeDate'가 없으면 푸시 동의 팝업 유도",
        "5_Banner_Policy": "하루에 한 번(Date().getCurrentDay()) SWR 방식으로 배너 팝업을 가져와 노출",
        "6_Tab_Navigation": "AnalyticsManager와 연동하여 탭 선택 시 카테고리별 트래킹 수행 및 배지 관리"
    }
    
    # --- [Key Components] ---
    COMPONENTS = {
        "View": {
            "class": "MainTabBarViewController",
            "desc": "Dumb View. 5개의 메인 탭(홈, AI, 샵, 나스모, 더보기) 관리 및 팝업 뷰컨트롤러의 물리적 present 담당"
        },
        "ViewModel": {
            "class": "MainTabBarViewModel",
            "desc": "팝업 노출 순서 및 비즈니스 조건(UserDefaults, API 상태)을 판단하는 순수 로직 엔진"
        },
        "Worker": {
            "class": "MainTabBarAPIWorker",
            "desc": "메인 탭바에 필요한 데이터(알람 설정, 팝업 배너)를 NetworkService(SWR)를 통해 조달"
        }
    }

    # --- [Special Logic & UI] ---
    LOGIC = {
        "Shop_Balloon": "tabBar.insertSubview를 통해 샵 탭 위에 구매 유도 말풍선(bubble_purchase_ticket)을 동적으로 삽입",
        "Thread_Safety": "MainTabBarViewModel에 @MainActor를 선언하여 비동기 작업 후 UI 명령(Output)이 항상 메인 스레드에서 발행되도록 보장",
        "Sequence_Binding": "팝업 간의 연결은 클로저(popUpPushAgreeHandler 등)를 통해 뷰모델의 Input으로 피드백되어 다음 단계가 트리거됨"
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
