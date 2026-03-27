#
#  biometric.py - Biometric Auth Module Blueprint (GolfzonAuth)
#

class BiometricSpec:
    NAME = "Biometric"
    DESC = "FaceID 및 TouchID를 이용한 생체 인식 보안 인증"
    PATH = "Sources/GolfzonAuth/biometric"
    
    # --- [Core Architectural Flow] ---
    CORE_FLOW = {
        "1_Availability": "BiometricAuthManager.shared.canEvaluatePolicy()를 통해 생체인증 지원 여부 확인",
        "2_Authentication": "evaluatePolicy() 호출 시 시스템 팝업 노출 및 사용자 인증 수행",
        "3_Result_Mapping": "인증 결과를 BiometricStatus(success, failure, lockout 등) Enum으로 변환하여 반환",
        "4_Error_Handling": "사용자 취소, 생체 정보 미등록, 인증 실패 등 다양한 케이스에 대한 정교한 에러 대응"
    }
    
    # --- [Key Components] ---
    COMPONENTS = {
        "Manager": {
            "class": "BiometricAuthManager",
            "desc": "LocalAuthentication 프레임워크를 감싸는 고수준 인터페이스"
        },
        "Type": {
            "enum": "BiometricType",
            "desc": "none, touchID, faceID 등 현재 장비가 지원하는 생체 인증 종류"
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
