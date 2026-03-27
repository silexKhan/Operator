#
#  overview.py - GolfzonCommon Library High-Level Summary
#

class Overview:
    """
    [대장님 🎯] 골프존 앱 전역에서 사용하는 공통 유틸리티 및 아키텍처 지원 라이브러리 요약서
    """
    NAME = "GolfzonCommon"
    LANGUAGES = ["Swift"]
    
    # --- [Paths] ---
    ROOT_PATH = "/Users/silex/workspace/library/GolfzonCommon"
    
    # 핵심 모듈 영역 (전수 조사 완료 🔍)
    DOMAINS = [
        "Core/Config",      # DynamicConfigManager (Whitelist, AppConfig)
        "Core/Environment", # AppEnvironment (AppType, DeployType, Build Info)
        "App/Version",      # ServiceValidator (Update, Maintenance)
        "App/Resource",     # DownloadManager (Remote Resource Handling)
        "Security/UI",      # SecureView (Screen Recording/Snapshot Protection)
        "Utils/Security",   # JailbreakDetector (integrity Check)
        "Utils/Crypto",     # CryptoManager (AES, HMAC, XOR Encryption)
        "System/Services",  # Location, Biometrics, Motion, Photo Library
        "Utils/Log",        # FlowLogger, FileLogManager
        "Utils/Common",     # Clipboard, DateTime, Extensions
    ]

    @classmethod
    def get_briefing(cls):
        return {
            "library": cls.NAME,
            "path": cls.ROOT_PATH,
            "languages": cls.LANGUAGES,
            "domains": cls.DOMAINS
        }
