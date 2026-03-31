#
#  overview.py - GDR Project Summary (Dynamic Path Edition) 🛡️⚡️
#

import os

class Overview:
    """
    [대장님 🎯] 골프존 GDR 프로젝트의 작전 지침서입니다.
    """
    NAME = "Project Alpha (Golfzon GDR)"
    
    DESCRIPTION = (
        "엄격한 MVVM 아키텍처를 기반으로 레거시 골프 시뮬레이션 시스템을 현대화하는 핵심 회선입니다. "
        "전문화된 유닛(Unit) 관제 하에 AI는 이 구역에서 정의된 5대 규약을 준수하여 임무를 수행합니다."
    )

    # [대장님 🎯] 배속된 전문 기술 유닛(Unit) 리스트입니다. 🍎📝
    UNITS = ["swift", "markdown"]

    # [대장님 🎯] 워크스페이스 구조를 기반으로 동적 경로를 제안합니다. 🕵️‍♂️🚀
    # MCP 루트에서 상위로 두 번 올라가서 project 폴더를 찾습니다.
    # root -> private -> workspace -> project -> Project Alpha
    BASE_WORKSPACE = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))))
    PROJECT_PATH = os.path.join(BASE_WORKSPACE, "project", "Project Alpha")
    
    DEPENDENCIES = ["mcp"]

    @classmethod
    def get_briefing(cls) -> dict:
        return {
            "name": cls.NAME,
            "description": cls.DESCRIPTION,
            "path": cls.PROJECT_PATH,
            "dependencies": cls.DEPENDENCIES,
            "units": cls.UNITS,
            "goal": "Modernizing legacy system with Strict MVVM"
        }
