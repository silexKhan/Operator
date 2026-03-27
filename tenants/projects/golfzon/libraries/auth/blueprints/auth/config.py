#
#  config.py - Auth Configuration Blueprint (GolfzonAuth)
#

class ConfigSpec:
    NAME = "Auth/Config"
    DESC = "인증 라이브러리의 전역 설정 및 클라이언트 보안 키 관리"
    PATH = "Sources/GolfzonAuth/common/Configuration.swift"
    
    # --- [Core Architectural Flow] ---
    CORE_FLOW = {
        "1_Integration": "초기화 시 GolfzonCommon의 AppEnvironment와 자동 동기화 (AppType, DeployType)",
        "2_Key_Management": "AppType(GDR, GLP 등)에 따라 authKey, clientId, defaultClientSecret를 차등 적용",
        "3_Secret_Persistence": "갱신된 clientSecret를 CommonDefaults(UserDefaults)를 통해 영속화 및 복원",
        "4_Dynamic_Update": "updateSecretKey()를 통해 서버로부터 받은 최신 보안 키를 실시간으로 라이브러리에 반영"
    }
    
    # --- [Key Components] ---
    COMPONENTS = {
        "Configuration": {
            "class": "Configuration",
            "desc": "라이브러리 전체의 동작 모드와 보안 자격 증명을 관리하는 중앙 통제 클래스"
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
