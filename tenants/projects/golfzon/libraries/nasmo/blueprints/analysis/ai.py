#
#  ai.py - AI Swing Analysis Module Blueprint (GolfzonNasmo)
#

class AiSpec:
    NAME = "Analysis/AI"
    DESC = "GolfNet AI를 이용한 스윙 포즈 검출 및 구간 분석 엔진"
    PATH = "Sources/DualNasmo/Classes/DualPlayer/ViewModel/AnalysisProcess.swift"
    
    # --- [Core Architectural Flow] ---
    CORE_FLOW = {
        "1_Extraction": "VideoProcess를 통해 비디오의 모든 프레임을 60fps 이미지로 추출",
        "2_AI_Inference": "GolfzonAI 프레임워크를 호출하여 각 프레임별 스윙 포즈(GolfNetPose) 검출",
        "3_Pose_Mapping": "검출된 AI 포즈를 UI용 VideoPosePosition(Address~Finish)으로 매핑 및 정제",
        "4_Caching": "분석된 포즈 데이터를 해시(djb2) 기반 파일로 저장하여 재진입 시 즉시 로드",
        "5_Box_Prediction": "사용자 영역(PredictionRect)을 추론하여 플레이어 뷰의 줌 및 센터링 가이드 제공"
    }
    
    # --- [Key Components] ---
    COMPONENTS = {
        "Analysis_Orchestrator": {
            "class": "AnalysisProcess",
            "desc": "프레임 추출, AI 추론, 데이터 정제, 캐싱을 총괄하는 비즈니스 로직 클래스"
        },
        "AI_Integration": {
            "framework": "GolfzonAI",
            "desc": "실질적인 딥러닝 모델 추론 수행"
        },
        "Data_Models": {
            "GolfNetPose": "AI가 정의한 8~16단계 스윙 상태",
            "VideoPosePosition": "앱 UI에서 사용하는 표준 8단계 스윙 포지션"
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
