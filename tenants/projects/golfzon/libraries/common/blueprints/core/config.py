#
#  config.py - DynamicConfig Module Blueprint (GolfzonCommon)
#

class ConfigSpec:
    NAME = "Core/Config"
    DESC = "앱 구동에 필요한 동적 설정값(Whitelist, Features, API Hosts) 관리"
    PATH = "Sources/GolfzonCommon/core/config"
    
    # --- [Core Architectural Flow] ---
    # requestSequence() -> Load Cache -> requestSignature() -> Compare -> [If Different] -> requestConfig() -> Update Subject & Cache
    CORE_FLOW = {
        "1_Initialization": "DynamicConfigManager.shared.requestSequence() 호출하여 동기화 시작",
        "2_Local_First": "CommonDefaults에서 'AppConfigurations'를 먼저 로드하여 Subject에 즉시 반영 (빠른 사용자 경험)",
        "3_Signature_Check": "서버의 Signature(Hash)를 확인하여 로컬 캐시의 유효성 검증",
        "4_Full_Sync": "Signature 불일치 시 전체 AppConfigModel을 다운로드하여 갱신",
        "5_Reactive_Update": "configPublisher를 통해 설정 변경 사항을 앱 전역으로 전파"
    }
    
    # --- [Key Components] ---
    COMPONENTS = {
        "Manager": {
            "class": "DynamicConfigManager",
            "desc": "설정 갱신 시퀀스 오케스트레이터 및 싱글톤 진입점"
        },
        "Model": {
            "AppConfigModel": "앱 기능 플래그, 딥링크 허용 리스트, 각종 호스트 URL 등을 포함한 통합 설정 모델",
            "Signature": "설정 데이터의 변경 여부를 식별하기 위한 경량 해시 정보"
        },
        "Storage": {
            "CommonDefaults": "Codable 데이터를 UserDefaults에 안전하게 저장하는 래퍼"
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
