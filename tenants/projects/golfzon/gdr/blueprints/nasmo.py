#
#  nasmo.py - Nasmo Domain Specification
#

class NasmoSpec:
    NAME = "Nasmo (Swing Video)"
    DESC = "스윙 영상 재생 및 분석 데이터 처리"
    PATH = "Sources/Nasmo"
    
    CORE_LOGIC = "NasmoViewModel.transform(input: NasmoInput) -> NasmoOutput"
    INTERFACES = {
        "Input": ["viewDidLoad", "videoTap", "filterChanged"],
        "Output": ["videoUrl", "swingData", "loadingStatus", "error"]
    }
    DEPENDENCIES = ["NasmoPlayer (AVFoundation)", "SwingAnalysisEngine (C++ Bridge)"]

    @classmethod
    def get_spec(cls):
        return {
            "name": cls.NAME,
            "desc": cls.DESC,
            "path": cls.PATH,
            "logic": cls.CORE_LOGIC,
            "interfaces": cls.INTERFACES,
            "dependencies": cls.DEPENDENCIES
        }
