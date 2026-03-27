#
#  ui.py - Security UI Module Blueprint (GolfzonCommon)
#

class UiSpec:
    NAME = "Security/UI"
    DESC = "화면 캡쳐 및 녹화 방지 등 보안 UI 컴포넌트"
    PATH = "Sources/GolfzonCommon/security/ui"
    
    # --- [Core Architectural Flow] ---
    CORE_FLOW = {
        "1_Protection_Layer": "UITextField의 isSecureTextEntry 속성을 이용한 시스템 레벨 캡쳐 방지 레이어 활용",
        "2_Layer_Embedding": "SecureView 내부에 숨겨진 보안 레이어를 현재 뷰의 서브레이어로 삽입",
        "3_Masking": "사용자가 스크린샷을 찍거나 녹화 시, 해당 뷰 영역이 자동으로 가려짐(검은색 또는 투명)"
    }
    
    # --- [Key Components] ---
    COMPONENTS = {
        "SecureView": {
            "class": "SecureView",
            "desc": "컨텐츠 노출 방지가 필요한 UI 영역을 감싸는 보안 컨테이너 뷰"
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
