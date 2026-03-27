#
#  blueprint.py - GDR Blueprint Router (On-Demand)
#

import importlib
from typing import Optional

class BluePrint:
    """
    [대장님 🎯] 도메인별 설계도를 필요할 때만 로드하는 라우터
    """
    
    @staticmethod
    def get_master():
        from tenants.projects.golfzon.gdr.blueprints.master import MasterFlow
        return MasterFlow.get_flow()

    @staticmethod
    def get_domain_spec(domain: str) -> Optional[dict]:
        # [대장님 🎯] 하위 디렉토리(예: common/network) 대응을 위해 경로 치환
        # 입력: "common/network" -> 모듈: "tenants.projects.golfzon.gdr.blueprints.common.network"
        domain_path = domain.lower().replace("/", ".")
        try:
            # 동적으로 도메인 설계도 로드
            module_path = f"tenants.projects.golfzon.gdr.blueprints.{domain_path}"
            module = importlib.import_module(module_path)
            
            # 클래스 이름 규칙: 마지막 단어 추출 (network -> NetworkSpec)
            domain_name = domain.split("/")[-1]
            class_name = f"{domain_name.capitalize()}Spec"
            spec_class = getattr(module, class_name)
            return spec_class.get_spec()
        except (ImportError, AttributeError):
            return None
