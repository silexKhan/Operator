#
#  drawing.py - Drawing Tools Module Blueprint (GolfzonNasmo)
#

class DrawingSpec:
    NAME = "Drawing/Tools"
    DESC = "나스모 영상 위에 선, 원, 사각형 등을 그리는 분석용 가이드 툴"
    PATH = "Sources/DualNasmo/Classes/Drawing"
    
    # --- [Core Architectural Flow] ---
    CORE_FLOW = {
        "1_Canvas_Setup": "DrawingView가 플레이어 상단에 투명 오버레이로 배치됨",
        "2_Shape_Creation": "ShapeManager를 통해 특정 타입(circle, rect, line)의 도형 인스턴스 생성",
        "3_Interaction": "제스처(UIPanGestureRecognizer)를 통해 도형의 크기 조절, 이동 및 회전 수행",
        "4_Undo_System": "registerUndo()를 통해 도형의 상태(Frame, Color)를 스택에 저장하여 실행 취소 지원",
        "5_Rendering": "draw() 메서드에서 UIBezierPath와 Core Graphics를 사용하여 고성능 커스텀 렌더링"
    }
    
    # --- [Key Components] ---
    COMPONENTS = {
        "Manager": {
            "class": "ShapeManager",
            "desc": "도형의 상태 관리, 제스처 처리 및 Undo/Redo 로직 총괄"
        },
        "Shape": {
            "class": "Shape",
            "desc": "실제 도형의 기하학적 정의 및 그리기 로직 (Circle, Rect, Line)"
        },
        "Protocol": {
            "class": "ShapeInteractable",
            "desc": "도형의 선택 가능 여부 및 이동 가능 여부를 판별하는 인터페이스"
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
