#
#  home.py - Home Dashboard Module Blueprint (GDR)
#

class HomeSpec:
    NAME = "View/Home"
    DESC = "앱의 메인 홈 대시보드. 유저 맞춤형 컨텐츠(이용권, 예약, 나스모, 연습기록) 및 광고 배너 통합 관리"
    PATH = "GDR/view/home"
    
    # --- [Core Architectural Flow] ---
    # HomeVC.ready -> VM.refreshAllData -> [Parallel Tasks Grouped by Priority] -> publishFinalState -> Diffable DataSource Apply
    CORE_FLOW = {
        "1_Prioritized_Fetch": {
            "Critical": "UserInfo, UserDetail (이용권, 예약 현황)",
            "Essential": "Nasmo, Practice Statistics, Recommand GDR/Pro",
            "Lowest": "Main/Center/Campaign Banners"
        },
        "2_Data_Orchestration": "SWR(Stale-While-Revalidate) 기반으로 캐시 선노출 후 서버 데이터로 부드러운 갱신(Fade)",
        "3_Smart_Filtering": "HomeViewRowModel의 isVisible 필터를 통해 데이터가 없는 섹션 자동 제외",
        "4_Diffable_Update": "ID + Signature(Hash) 조합의 지문을 비교하여 변경된 행만 부분 업데이트 수행",
        "5_Action_Routing": "Cell Action -> VM.handleCellAction -> AppNavigator.navigate(to:) 호출"
    }
    
    # --- [Key Components] ---
    COMPONENTS = {
        "View": {
            "class": "HomeViewController",
            "desc": "UITableViewDiffableDataSource를 사용하는 Dumb View. 스크롤 및 탭 이벤트를 VM으로 전달"
        },
        "ViewModel": {
            "class": "HomeViewModel",
            "desc": "홈 화면의 지휘통제실. 3단계 우선순위 병렬 로딩 및 Row 모델 조립(Publishing) 담당"
        },
        "Model": {
            "HomeViewRowModel": "ID와 Signature를 가진 Hashable 행 모델. Payload(enum)로 섹션 타입 구분",
            "HomeType": "각 섹션의 Identifier와 기획된 정렬 순서(sortOrder) 정의"
        },
        "Worker": {
            "class": "HomeAPIWorker",
            "desc": "NetworkService를 사용하여 10여 가지 이상의 API를 SWR 방식으로 호출"
        }
    }

    # --- [Special Logic & UI] ---
    LOGIC = {
        "Signature_Hasing": "페이로드 내부를 다 훑지 않고 개수/ID/첫이미지 등을 조합한 Int 지문으로 데이터 변경 식별",
        "Shop_Selection_Context": "이용권/매장/상품/레슨권 선택 상태를 유지하여 SelectShopActionSheet와 동기화",
        "Location_Awareness": "GDRLocationManager를 통해 위경도를 획득하여 주변 추천 매장 리스트 실시간 갱신"
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
