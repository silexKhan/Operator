#
#  visionwebview.py - Hybrid Web Module Blueprint (GolfzonVision)
#

class VisionwebviewSpec:
    NAME = "Hybrid/Web"
    DESC = "고성능 하이브리드 웹뷰 시스템 및 네이티브 브릿지 오케스트레이션"
    PATH = "Sources/GolfzonVision/VisionWKWebViewController.swift"
    
    # --- [Core Architectural Flow] ---
    CORE_FLOW = {
        "1_Configuration": "VisionWKWebViewController 초기화 시 PRIME.shared에서 UA 및 전역 쿠키 설정 로드",
        "2_Request_Header": "모든 URL 요청 시 PRIME.shared.headerField의 토큰 정보를 HTTP 헤더에 자동 주입",
        "3_JS_Bridge": "hybridfunction:// 스킴을 가로채어 Executer(Behaviors)를 통해 네이티브 기능 실행",
        "4_File_Bridge": "fileBridge 메시지 핸들러를 통해 웹에서 보낸 데이터를 FileSaver로 사진첩에 저장",
        "5_Intercepting": "requestedUrl() 오버라이딩을 통해 서브클래스에서 특정 URL 요청을 동적으로 필터링"
    }
    
    # --- [Key Components] ---
    COMPONENTS = {
        "WebView": {
            "class": "VisionWKWebViewController",
            "desc": "WKWebView를 래핑하여 인증, 브릿지, 에러 처리를 통합 관리하는 하이브리드 핵심 뷰"
        },
        "Executer": {
            "class": "Executer",
            "desc": "자바스크립트 명령(Alert, ViewOpen, Shake 등)을 실제 네이티브 액션으로 매핑"
        },
        "Bridge": {
            "class": "HybridFunctionExternalBridge",
            "desc": "외부 앱 또는 시스템과의 인터랙션을 담당하는 추가 브릿지 레이어"
        }
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
