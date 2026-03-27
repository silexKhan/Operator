#
#  schemes.py - App Scheme & DeepLink Routing Blueprint (GDR)
#

class SchemeSpec:
    NAME = "Common/Schemes"
    DESC = "앱 외부(딥링크, 푸시)에서 유입되는 URL 스키마 및 라우팅 제어"
    PATH = "GDR/common/AppSchemes.swift"
    
    # --- [Core Architectural Flow] ---
    # External Event -> SceneStepper.processScheme -> AppSchemes.handle(url:) -> Action (Navigation/Logic)
    CORE_FLOW = {
        "1_Interception": "SceneDelegate/Stepper에서 URL을 수신하여 AppSchemes.shared.handle 호출",
        "2_Host_Parsing": "RequestURL 구조체를 통해 호스트(Host)와 쿼리 파라미터를 분석",
        "3_Routing_Logic": "Host Enum(auth, reservation, ai 등)에 따라 적절한 뷰컨트롤러 소환 및 데이터 주입",
        "4_Pending_System": "로그인 전 등 특정 상황에서 URL을 처리할 수 없을 때 savePendingUrl로 보관 후 나중에 소비(consume)",
        "5_Main_Reset": "moveToMainHome() 호출 시 모든 모달을 닫고 첫 번째 탭의 최상단으로 강제 이동"
    }
    
    # --- [Supported Hosts & Actions] ---
    HOSTS = {
        "auth": "accessToken 또는 mbsessionid를 통해 자동 로그인 세션 구성",
        "reservation": "GTMReservationStatusViewController(예약현황)로 이동",
        "myschedule": "ScheduleViewController로 이동 및 특정 날짜 포커싱",
        "openweb": "DynamicConfig(Whitelist) 검증 후 내부 웹뷰로 특정 URL 오픈",
        "ai/airesult": "AI 코칭 탭으로 이동하거나 특정 분석 결과 상세 화면 노출",
        "aistart": "분석용 영상을 다운로드(loadFileSync)한 후 AI 분석 팝업 실행",
        "mainhome": "앱의 상태를 초기 홈 화면으로 완전 리셋"
    }

    # --- [Special Features] ---
    FEATURES = {
        "DeepLink_Security": "DynamicConfigManager.shared.currentConfig.deeplink.allows 리스트를 통한 허용된 도메인만 웹뷰 오픈",
        "Video_Sync_Loader": "AI 분석을 위해 원격 동영상을 로컬 캐시(Documents)에 동기적으로 저장하는 유틸리티 내장",
        "TopVC_Awareness": "UIApplication.topViewController()를 실시간으로 추적하여 네비게이션 컨텍스트 결정"
    }

    @classmethod
    def get_spec(cls):
        return {
            "name": cls.NAME,
            "desc": cls.DESC,
            "path": cls.PATH,
            "flow": cls.CORE_FLOW,
            "hosts": cls.HOSTS,
            "features": cls.FEATURES
        }
