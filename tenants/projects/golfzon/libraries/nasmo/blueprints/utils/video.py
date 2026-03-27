#
#  video.py - Video Processing Module Blueprint (GolfzonNasmo)
#

class VideoSpec:
    NAME = "Utils/Video"
    DESC = "FFmpeg 기반 프레임 추출, 60fps 인코딩 및 투명도 비디오 생성 유틸리티"
    PATH = "Sources/DualNasmo/Classes/Utils/Video/VideoProcess.swift"
    
    # --- [Core Architectural Flow] ---
    CORE_FLOW = {
        "1_Frame_Extraction": "MobileFFmpeg를 사용하여 원본 비디오에서 초당 60프레임의 JPEG 이미지 시퀀스 획득",
        "2_KeyFrame_Boost": "탐색 성능 향상을 위해 원본 영상을 60fps MOV로 재인코딩(KeyFrame 증가)",
        "3_Alpha_Encoding": "HEVC with Alpha 코덱을 사용하여 투명 배경을 가진 MOV 분석 영상 생성 지원",
        "4_Validation": "AVAsset을 로드하여 재생 가능 여부 및 비디오 트랙 존재 여부 비동기 검증"
    }
    
    # --- [Key Components] ---
    COMPONENTS = {
        "FFmpeg_Engine": {
            "library": "MobileFFmpeg",
            "desc": "고성능 비디오 처리 및 프레임 추출 명령어 실행"
        },
        "Encoder": {
            "class": "VideoProcess",
            "desc": "AVAssetReader/Writer를 이용한 커스텀 비디오 인코딩 파이프라인 구현"
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
