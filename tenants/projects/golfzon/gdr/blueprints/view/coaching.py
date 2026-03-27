#
#  coaching.py - AI Coaching Module Blueprint (GDR - Legacy)
#

class CoachingSpec:
    NAME = "View/Coaching"
    DESC = "AI 스윙 분석 및 코칭 리포트 화면 (리팩토링 미완료 레거시 영역 ⚠️)"
    PATH = "GDR/view/coaching"
    
    # --- [Core Architectural Flow (Legacy MVC)] ---
    # View.viewWillAppear -> VC.updateRecentDiagnosis() -> Model.requestSwingResults (Callback) -> UI Update
    CORE_FLOW = {
        "1_Lifecycle": "viewWillAppear 시점에 Lottie 애니메이션 재생 및 최근 진단 내역 갱신",
        "2_Data_Fetch": "SwingResult.shared.requestSwingResults 호출 (Alamofire + SwiftyJSON 기반 레거시 네트워크)",
        "3_UI_Rendering": "네트워크 응답 수신 후 ViewController 내에서 직접 Label, ImageUI 텍스트 및 알파값 조절",
        "4_Navigation": "UIStoryboard를 직접 인스턴스화하여 present 호출 (Scrap, SequenceDetail, CameraShooting 등)"
    }
    
    # --- [Key Components] ---
    COMPONENTS = {
        "ViewController": {
            "class": "CoachingViewController",
            "desc": "로직과 UI가 혼재된 레거시 VC. 데이터 요청, 결과 처리, 화면 전환을 모두 담당"
        },
        "Legacy_Model": {
            "class": "SwingResult",
            "desc": "데이터 구조(SwiftyJSON 기반)와 네트워킹 로직이 결합된 Fat Model"
        },
        "Sub_Modules": {
            "Scrap": "분석 결과 목록 (스크랩)",
            "SequenceDetail": "스윙 시퀀스별 상세 분석 결과",
            "CameraShooting": "AI 분석용 스윙 촬영 카메라",
            "AnalysisResult": "종합 분석 점수 및 차트 리포트"
        }
    }

    # --- [Legacy Characteristics] ---
    CHARACTERISTICS = [
        "⚠️ No ViewModel: 비즈니스 로직이 ViewController에 직접 구현됨",
        "⚠️ Manual Mapping: Codable 대신 SwiftyJSON을 사용하여 수동으로 모델 매핑",
        "⚠️ Completion Handlers: async/await 대신 클로저 기반의 비동기 처리",
        "⚠️ Direct Navigation: AppNavigator를 거치지 않고 직접Storyboard에서 VC를 꺼내서 이동"
    ]

    @classmethod
    def get_spec(cls):
        return {
            "name": cls.NAME,
            "desc": cls.DESC,
            "path": cls.PATH,
            "flow": cls.CORE_FLOW,
            "components": cls.COMPONENTS,
            "characteristics": cls.CHARACTERISTICS
        }
