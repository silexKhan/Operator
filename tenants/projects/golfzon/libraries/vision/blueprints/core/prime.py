#
#  prime.py - PRIME Sync Module Blueprint (GolfzonVision)
#

class PrimeSpec:
    NAME = "Core/PRIME"
    DESC = "Native와 Web 간의 인증 세션 및 환경 설정을 동기화하는 중앙 저장소"
    PATH = "Sources/GolfzonVision/PRIME.swift"
    
    # --- [Core Architectural Flow] ---
    CORE_FLOW = {
        "1_Token_Sync": "AppDelegate/Login 성공 시 PRIME.shared에 accessToken 및 sesssionID 주입",
        "2_UA_Sync": "AppStepper에서 조립된 커스텀 UserAgent를 PRIME.shared.UserAgent에 보관",
        "3_Header_Injection": "VisionWKWebViewController가 요청을 보낼 때마다 headerField를 참조하여 HTTP 헤더 구성",
        "4_Session_Sharing": "정적 WKProcessPool과 PRIME 정보를 결합하여 앱 내 모든 웹뷰 인스턴스가 동일 세션 유지"
    }
    
    # --- [Key Components] ---
    COMPONENTS = {
        "Store": {
            "class": "PRIME",
            "desc": "accessToken, sessionID, UserAgent, headerField 등을 관리하는 싱글톤 클래스"
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
