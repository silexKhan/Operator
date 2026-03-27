#
#  version.py - ServiceValidator Module Blueprint (GolfzonCommon)
#

class VersionSpec:
    NAME = "App/Version"
    DESC = "앱 서비스 이용 가능 여부(업데이트, 점검) 및 버전 유효성 검증"
    PATH = "Sources/GolfzonCommon/app/version"
    
    # --- [Core Architectural Flow] ---
    # validateService() -> requestAppVersionData() -> Check Maintenance -> [If Not] -> Compare Versions -> Return Result
    CORE_FLOW = {
        "1_Version_Fetch": "서버로부터 강제업데이트, 권장업데이트, 점검 여부 정보 수신",
        "2_Maintenance_Gate": "maintenance 플래그가 True인 경우 즉시 .underMaintenance 반환",
        "3_AppStore_Sync": "서버 정보와 별개로 앱스토어 실시간 버전을 교차 검증 (선택 사항)",
        "4_Priority_Logic": "강제 업데이트 필요 여부를 최우선으로 판단한 후 권장 업데이트 여부 결정",
        "5_Actionable_Result": "UI 계층에서 즉시 팝업을 띄우거나 강제 종료할 수 있는 Enum 형태의 결과 반환"
    }
    
    # --- [Key Components] ---
    COMPONENTS = {
        "Validator": {
            "class": "ServiceValidator",
            "desc": "버전 비교 로직 및 점검 상태를 판별하는 핵심 엔진"
        },
        "Protocol": {
            "class": "ServiceValidating",
            "desc": "테스트 용이성을 위한 인터페이스 정의"
        },
        "Model": {
            "ServiceValidationResult": "normal, recentUpdate, forcedUpdate, underMaintenance, serverDown 결과셋 정의"
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
