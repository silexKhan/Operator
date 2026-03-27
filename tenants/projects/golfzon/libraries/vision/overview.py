#
#  overview.py - GolfzonVision Library High-Level Summary
#

class Overview:
    """
    [대장님 🎯] 골프존 앱 전역에서 사용하는 하이브리드 웹뷰 및 스캐너, 핵심 유틸리티 라이브러리 요약서
    """
    NAME = "GolfzonVision"
    LANGUAGES = ["Swift"]
    
    # --- [Paths] ---
    ROOT_PATH = "/Users/silex/workspace/library/Vision"
    
    # 핵심 모듈 영역
    DOMAINS = [
        "Hybrid/Web",       # VisionWKWebViewController, JS Bridge (Executer)
        "Core/PRIME",       # PRIME (Unified Token & UserAgent Sync)
        "Scanner",          # QRCode / Barcode Scan ViewControllers
        "Core/Network",     # SocketManager, LocationManager (Vision Style)
        "UI/Components"     # LoadingIndicator, NetworkErrorView
    ]

    @classmethod
    def get_briefing(cls):
        return {
            "library": cls.NAME,
            "path": cls.ROOT_PATH,
            "languages": cls.LANGUAGES,
            "domains": cls.DOMAINS
        }
