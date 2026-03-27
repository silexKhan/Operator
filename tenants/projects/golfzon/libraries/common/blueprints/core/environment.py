#
#  environment.py - AppEnvironment Module Blueprint (GolfzonCommon)
#

class EnvironmentSpec:
    NAME = "Core/Environment"
    DESC = "실행 중인 앱의 번들 ID 분석 및 배포 환경(Dev, QA, Live) 판별"
    PATH = "Sources/GolfzonCommon/core/environment"
    
    # --- [Core Architectural Flow] ---
    CORE_FLOW = {
        "1_Detection": "Bundle.main.bundleIdentifier를 기반으로 앱 종류(AppType)와 배포 환경(DeployType) 자동 판별",
        "2_Setup": "AppEnvironment.setup()을 통해 AppDelegate 등에서 수동 환경 설정 가능",
        "3_Information": "appVersion, bundleID 등 빌드 정보를 싱글톤(.shared)을 통해 앱 전역에 제공",
        "4_Debug_Flag": "deployType이 .live가 아닌 경우 isDebug를 True로 반환하여 디버그 기능 제어"
    }
    
    # --- [Key Components] ---
    COMPONENTS = {
        "Manager": {
            "class": "AppEnvironment",
            "desc": "앱 환경 정보의 Single Source of Truth"
        },
        "Enums": {
            "AppType": "GDR, GDR_Legacy 등 골프존 앱 군별 식별자 및 관련 URL 정의",
            "DeployType": "dev, qa, close, live 배포 환경 정의"
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
