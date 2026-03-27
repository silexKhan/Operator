#
#  gdrshop.py - GDR Shop Module Blueprint (GDR)
#

class GDRShopSpec:
    NAME = "View/GDRShop"
    DESC = "이용권 및 패스 구매를 위한 샵 화면 (Web-Embed 하이브리드 방식 🕸️)"
    PATH = "GDR/view/gdrshop"
    
    # --- [Core Architectural Flow] ---
    # GDRShopVC -> Storyboard Embed Segue -> WebViewController -> Load URL (API.PURCHASE_PRODUCT)
    CORE_FLOW = {
        "1_Container": "GDRShopViewController가 컨테이너 역할을 수행하며, Main.storyboard의 탭바에서 직접 로드됨",
        "2_Web_Embedding": "prepare(for:sender:) 시점에 WebViewController(Embed)를 획득하고 샵 전용 설정 주입",
        "3_Configuration": "이용권 구매 페이지(API.PURCHASE_PRODUCT) 로드 및 네비바 테마/배경색 커스터마이징",
    }
    
    # --- [Key Components] ---
    COMPONENTS = {
        "ViewController": {
            "class": "GDRShopViewController",
            "desc": "샵 웹뷰를 감싸는 껍데기(Shell) 뷰 컨트롤러"
        },
        "Embedded_View": {
            "class": "WebViewController",
            "desc": "실제 샵 콘텐츠(웹)를 렌더링하고 브릿지 통신을 담당하는 Vision 라이브러리 기반 웹뷰"
        }
    }

    # --- [Special Logic & UI] ---
    LOGIC = {
        "Hybrid_Settings": {
            "isDarkModeEnabled": "True (내비바 테마 대응)",
            "isBackgroundThemeAware": "False (본문 영역은 화이트 배경 고정)",
            "navigationControllerState": "0 (기본 상태)"
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
