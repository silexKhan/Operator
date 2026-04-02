#
#  overview.py - MCP Operator Core Identity (Dynamic Path Edition) 
#

import os

class Overview:
    """
    [사용자] MCP 오퍼레이터의 압축된 핵심 명세서입니다.
    """
    NAME = "Operator (교환)"
    
    DESCRIPTION = (
        "MCP 기반의 디지털 지휘소입니다. 사용자가 실시간으로 제어하는 Circuits(회선)와 "
        "Protocols(규약)를 통해 AI 모델의 업무 궤도를 정밀하게 관리합니다. "
        "특히 전문 '유닛(Unit) 관제'를 적용하여 AI가 정해진 규약 안에서만 안전하게 작동하도록 "
        "물리적으로 통제하고 품질을 보증하는 지능형 엔진입니다. "
    )

    # [사용자] 배속된 전문 기술 유닛(Unit) 리스트입니다. 
    UNITS = ["python", "markdown", "sentinel"]

    # [사용자] 하드코딩 완전 박멸! 현재 위치를 기준으로 프로젝트 루트를 자동 감지합니다. 
    # mcp -> registry -> circuits -> root (상위 3단계)
    PROJECT_PATH = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
    
    DEPENDENCIES = []

    @classmethod
    def get_briefing(cls) -> dict:
        return {
            "name": cls.NAME,
            "description": cls.DESCRIPTION,
            "path": cls.PROJECT_PATH,
            "dependencies": cls.DEPENDENCIES,
            "units": cls.UNITS,
            "goal": "유닛 관제 기반의 AI 모델 정밀 제어 및 품질 보증"
        }
