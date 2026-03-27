#
#  overview.py - GolfzonNasmo (DualNasmo) Library High-Level Summary
#

class Overview:
    """
    [대장님 🎯] 스윙 영상(나스모) 재생, 비교분석(Dual), 드로잉 툴 및 비디오 동기화를 지원하는 라이브러리 요약서
    """
    NAME = "GolfzonNasmo"
    LANGUAGES = ["Swift"]
    
    # --- [Paths] ---
    ROOT_PATH = "/Users/silex/workspace/library/Nasmo"
    
    # 핵심 모듈 영역 (전수 조사 완료 🔍)
    DOMAINS = [
        "Player/Single",    # SingleNasmo (Standard Playback)
        "Player/Dual",      # DualPlayer (Multi-video Sync Playback)
        "Analysis/AI",      # AnalysisProcess (GolfNet AI Pose Detection)
        "Drawing/Tools",    # Shape, ShapeManager (Drawing on Video with Undo)
        "Utils/Video",      # VideoProcess (FFmpeg, 60fps Encoding, Alpha MOV)
        "Utils/Cache",      # CacheUtils (Pose & Frame Data Persistence)
        "Scenes/Main",      # DualNasmo, SingleNasmo, SelectNasmo ViewControllers
    ]

    @classmethod
    def get_briefing(cls):
        return {
            "library": cls.NAME,
            "path": cls.ROOT_PATH,
            "languages": cls.LANGUAGES,
            "domains": cls.DOMAINS
        }
