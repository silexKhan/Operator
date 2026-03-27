#
#  common.py - Common Utils Module Blueprint (GolfzonCommon)
#

class CommonSpec:
    NAME = "Utils/Common"
    DESC = "앱 전반에서 재사용되는 기초 유틸리티 및 익스텐션"
    PATH = "Sources/GolfzonCommon/utils"
    
    # --- [Key Components] ---
    COMPONENTS = {
        "Clipboard": {
            "class": "ClipboardManager",
            "desc": "UIPasteboard 기반 텍스트 복사 및 획득 유틸리티"
        },
        "DateTime": {
            "class": "DateCheckManager",
            "desc": "서버 시간 동기화 및 날짜 포맷팅 검증"
        },
        "Extensions": {
            "Bundle+Ext": "버전 정보 및 앱 이름 획득 유틸리티",
            "Dictionary+Ext": "데이터 안전 추출 및 변환 익스텐션"
        }
    }

    @classmethod
    def get_spec(cls):
        return {
            "name": cls.NAME,
            "desc": cls.DESC,
            "path": cls.PATH,
            "components": cls.COMPONENTS
        }
