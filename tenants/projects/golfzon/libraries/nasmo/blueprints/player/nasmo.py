#
#  player.py - Dual & Single Player Module Blueprint (GolfzonNasmo)
#

class PlayerSpec:
    NAME = "Player/Nasmo"
    DESC = "스윙 영상 재생(Single) 및 비교분석(Dual) 엔진"
    PATH = "Sources/DualNasmo/Classes"
    
    # --- [Core Architectural Flow] ---
    CORE_FLOW = {
        "1_Single_Mode": "SingleNasmoView를 통해 단일 영상 재생, 루프, 드로잉 툴 기본 지원",
        "2_Dual_Mode": "DualPlayerViewController에서 두 개의 PlayerView를 오케스트레이션하여 비교 재생",
        "3_Sync_Logic": "SyncDualVideoUseCase를 통해 두 영상의 프레임 속도를 조절하여 스윙 구간별 동기화 수행",
        "4_Time_Mapping": "convertOriginalTimeToSyncedTime()을 이용하여 원본 영상 시간을 동기화된 가상 시간으로 변환",
        "5_Playback_Control": "DualPlayerController가 두 AVPlayer의 재생, 일시정지, 탐색(Seek) 명령을 동시 전달"
    }
    
    # --- [Key Components] ---
    COMPONENTS = {
        "Single_Player": {
            "class": "SingleNasmoView",
            "desc": "표준 나스모 재생 및 드로잉 오버레이를 포함한 독립형 뷰"
        },
        "Dual_Player": {
            "class": "DualPlayerView",
            "desc": "두 영상을 배치하고 챕터별 동기화 재생을 수행하는 복합 뷰"
        },
        "Controller": {
            "class": "DualPlayerController",
            "desc": "플레이어의 재생 상태(Play/Pause), 속도, 탐색 명령을 관리하는 지휘 계층"
        },
        "Sync_UseCase": {
            "class": "SyncDualVideoUseCaseImpl",
            "desc": "영상 간 프레임 동기화 및 구간별 가상 시간 매핑을 담당하는 비즈니스 엔진"
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
