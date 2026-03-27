#
#  overview.py - GolfzonAuth Library High-Level Summary
#

class Overview:
    """
    [대장님 🎯] 골프존 앱 전역에서 사용하는 인증 및 세션 관리, 스크린 로그인 라이브러리 요약서
    """
    NAME = "GolfzonAuth"
    LANGUAGES = ["Swift"]
    
    # --- [Paths] ---
    ROOT_PATH = "/Users/silex/workspace/library/Auth"
    
    # 핵심 모듈 영역 (전수 조사 완료 🔍)
    DOMAINS = [
        "Auth/Core",        # AuthManager, AuthService, AuthSession, AuthStorage
        "Auth/Config",      # Configuration (ClientSecret, ClientID, AppType Sync)
        "ScreenLogin",      # GDR(MQTT) / GS(SocketIO) Screen Login System
        "Biometric",        # BiometricAuthManager (FaceID/TouchID)
        "Keychain",         # KeychainManager (Secure Storage Bridge)
        "Error/Handling",   # CertificationError, Migration Mapping
    ]
    
    # [대장님 🎯] 이 라이브러리가 의존하는 타 라이브러리
    DEPENDENCIES = ["GolfzonCommon"]

    @classmethod
    def get_briefing(cls):
        return {
            "library": cls.NAME,
            "path": cls.ROOT_PATH,
            "languages": cls.LANGUAGES,
            "domains": cls.DOMAINS
        }
