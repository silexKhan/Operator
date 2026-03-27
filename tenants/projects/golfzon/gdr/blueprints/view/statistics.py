#
#  statistics.py - Practice Statistics Module Blueprint (GDR - Legacy Hybrid)
#

class StatisticsSpec:
    NAME = "View/Statistics"
    DESC = "연습 현황 및 월간 리포트를 확인하는 통계 화면 (Web-Embed 기반 레거시 하이브리드 ⚠️)"
    PATH = "GDR/view/statistics"
    
    # --- [Core Architectural Flow] ---
    # StatisticsVC -> Storyboard Embed Segue -> WebViewController (Load: API.USER_NASMO) -> Web Interceptor (Logic)
    CORE_FLOW = {
        "1_Container": "StatisticsViewController가 웹뷰 컨테이너 역할을 하며, 탭바에서 직접 로드됨",
        "2_Web_Embedding": "세그웨이('staticsWeb')를 통해 WebViewController를 임베드하고 초기 URL 주입",
        "3_Web_Interception": "웹뷰 내부의 특정 URL 호스트(showFavorite, changeFavorite)를 가로채서 네이티브 UI 상태(type) 동기화",
        "4_External_Update": "AppNavigator에서 0.01s 지연 후 updateData(sendURL:)를 호출하여 특정 메뉴로 강제 이동 지원"
    }
    
    # --- [Key Components] ---
    COMPONENTS = {
        "ViewController": {
            "class": "StatisticsViewController",
            "desc": "통계 화면의 메인 껍데기. 상단 리포트 버튼 상태와 웹뷰 간의 상호작용 관리"
        },
        "Embedded_View": {
            "class": "WebViewController",
            "desc": "연습 기록 및 통계 웹 페이지를 렌더링하는 실질적인 뷰"
        }
    }

    # --- [Special Logic & UI] ---
    LOGIC = {
        "Web_Bridge_Interceptor": {
            "showFavorite": "URL 쿼리의 'type' 값을 읽어 상단 별표(즐겨찾기)/리포트 아이콘 이미지 교체",
            "changeFavorite": "'isChange=true' 감지 시 웹뷰를 강제로 새로고침(reload)"
        },
        "Report_Navigation": {
            "Type_1 (Star)": "별표 아이콘일 때 API.FAVORITE 화면을 모달로 노출",
            "Type_Other (Report)": "리포트 아이콘일 때 API.MONTHLY_REPORT 화면으로 푸시 이동"
        },
        "Appearance": "isDarkModeEnabled = false, isBackgroundThemeAware = false (웹 콘텐츠 가독성을 위해 화이트 배경 고정)"
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
