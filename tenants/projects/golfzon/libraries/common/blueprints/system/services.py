#
#  services.py - System Services Module Blueprint (GolfzonCommon)
#

class ServicesSpec:
    NAME = "System/Services"
    DESC = "iOS 시스템 기능(위치, 생체인증, 모션 센서, 사진 라이브러리) 통합 브릿지"
    PATH = "Sources/GolfzonCommon/system"
    
    # --- [Core Architectural Flow] ---
    CORE_FLOW = {
        "1_Abstraction": "LocationManager, MotionManager 등 각 시스템 프레임워크를 Swift 최신 패턴(Combine/Async)으로 래핑",
        "2_Permissions": "기능 사용 전 권한 상태(PhotoLibraryStatus, BiometricStatus)를 안전하게 판별",
        "3_Data_Streaming": "Location, Motion 데이터를 스트림 형태로 제공하여 실시간 처리 지원",
        "4_Auth_Integration": "FaceID/TouchID를 이용한 간편 본인 인증 기능(BiometricAuthManager) 제공"
    }
    
    # --- [Key Components] ---
    COMPONENTS = {
        "Location": {
            "class": "LocationManager",
            "desc": "CLLocationManager 래퍼. 위경도 및 권한 관리"
        },
        "Biometrics": {
            "class": "BiometricAuthManager",
            "desc": "LocalAuthentication 기반 생체 인증 처리"
        },
        "Motion": {
            "class": "MotionManager",
            "desc": "CoreMotion 기반 가속도/자이로 센서 데이터 관리"
        },
        "Photo": {
            "class": "PhotoLibrary",
            "desc": "Photos 프레임워크 기반 갤러리 접근 및 메타데이터 획득"
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
