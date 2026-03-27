#
#  more.py - 'More' Tab Module Blueprint (GDR)
#

class MoreSpec:
    NAME = "View/More"
    DESC = "앱의 더보기/설정 탭. 사용자 프로필, 퀵 메뉴(스케줄, 이용권, 구매내역, 쿠폰), 하단 메뉴 리스트 및 광고 배너 관리"
    PATH = "GDR/view/more"
    
    # --- [Core Architectural Flow] ---
    # MoreVC.viewDidLoad -> VM.readyHandler -> [1. Profile Update] -> [2. Info/Banner Fetch] -> [3. Menu Context Sync]
    CORE_FLOW = {
        "1_Profile_Sync": "UserInfo.shared 및 AuthSession 기반으로 닉네임과 프로필 이미지(inferredImageURL) 즉시 반영",
        "2_Background_Fetch": "MoreAPIWorker를 통해 최신 유저 정보와 서브 옵션 배너를 비동기로 로드 (SWR 적용)",
        "3_Dynamic_UI": "광고 배너 유무에 따라 NSLayoutConstraint의 Priority를 조절하여 레이아웃을 동적으로 최적화",
        "4_Menu_Composition": "유저의 프로(Pro/GtmPro) 여부에 따라 MoreMenuListViewController의 메뉴 구성을 실시간 업데이트",
        "5_Action_Dispatch": "프로필/설정/퀵메뉴 탭 시 AppNavigator 또는 전용 스트림(push/present)을 통해 화면 이동 수행"
    }
    
    # --- [Key Components] ---
    COMPONENTS = {
        "View": {
            "class": "MoreViewController",
            "desc": "상단 프로필, 4대 퀵 메뉴, 배너 뷰를 포함한 더보기 메인 쉘"
        },
        "ViewModel": {
            "class": "MoreViewModel",
            "desc": "비즈니스 로직 및 네비게이션 트리거 담당. ProfileImageAvailable 프로토콜을 통한 이미지 URL 추론 지원"
        },
        "Sub_Controllers": {
            "MoreMenuListViewController": "하단 메뉴 리스트(공지사항, 가이드, 약관 등) 담당",
            "MyInfoViewController": "개인 정보 수정 및 닉네임 변경",
            "SettingViewController": "앱 설정(알림, 다크모드 등) 관리",
            "ScheduleViewController": "연습/레슨 예약 스케줄 관리"
        }
    }

    # --- [Special Logic & UI] ---
    LOGIC = {
        "Profile_Image_Inference": "Kingfisher를 사용하여 추론된 URL로부터 프로필 이미지를 캐싱 및 로드",
        "Layout_Priority_Toggle": "배너가 없을 때 높이 제약조건의 우선순위를 낮춰서(priority: 250) 화면에서 숨김 처리",
        "Hybrid_Navigation": "내정보/설정은 Native로, 이용권/쿠폰 등은 Web(Vision)으로 분기하여 네비게이션 수행"
    }

    @classmethod
    def get_spec(cls):
        return {
            "name": cls.NAME,
            "desc": cls.DESC,
            "path": cls.PATH,
            "flow": cls.CORE_FLOW,
            "components": cls.COMPONENTS,
            "logic": cls.LOGIC
        }
