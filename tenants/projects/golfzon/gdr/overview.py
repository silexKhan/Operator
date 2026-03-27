#
#  overview.py - GDR Project High-Level Summary
#

class Overview:
    """
    [대장님 🎯] 프로젝트의 정체성과 주요 경로를 담은 가벼운 요약서
    """
    NAME = "GDR (Golfzon Driving Range)"
    LANGUAGES = ["Swift", "Objective-C"]
    
    # --- [Paths] ---
    ROOT_PATH = "/Users/silex/workspace/project/GDR"
    LEGACY_PATH = "/Users/silex/workspace/project/legacy/legacy_gdr"
    
    # --- [Dependencies] ---
    # [대장님 🎯] 이 프로젝트가 의존하는 공용 라이브러리 테넌트 목록
    DEPENDENCIES = ["GolfzonCommon", "GolfzonAuth", "GolfzonVision", "GolfzonNasmo"]
    
    # 핵심 도메인 (자세한 내용은 BluePrint 참조)
    DOMAINS = ["App/Core", "Common/Network", "Common/Schemes", "View/Initializer", "View/Login", "View/Main", "View/Home", "View/Coaching", "View/GDRShop", "View/Statistics", "View/More"]
    
    # [대장님 🎯] 탭바 5대 핵심 메뉴 (Tab Configuration)
    MAIN_TABS = [
        "1. Main (홈 대시보드 - View/Home)",
        "2. AI_Main (AI 분석 데이터 - View/Coaching ⚠️)",
        "3. Shop (이용권/패스 구매 - View/GDRShop)",
        "4. Nasmo (나스모 영상 목록 - View/Statistics ⚠️)",
        "5. More (설정/내정보)"
    ]

    # --- [External / Admin Links] ---
    # [대장님 🎯] 비즈니스 운영 및 관리를 위한 주요 사이트 목록
    ADMIN_URLS = {
        "GDR_POS_MANAGEMENT": "https://pos.spazon.com/Src/Login/LoginForm.aspx" # GDR SHOP 상품 구매 시 매장 결제 관리 사이트 💳
    }

    @classmethod
    def get_briefing(cls):
        return {
            "project": cls.NAME,
            "path": cls.ROOT_PATH,
            "languages": cls.LANGUAGES,
            "domains": cls.DOMAINS,
            "tabs": cls.MAIN_TABS,
            "admin_urls": cls.ADMIN_URLS
        }
