#
#  blueprint.py - GolfzonCommon Blueprint Router
#

import importlib
from typing import Optional

class BluePrint:
    """
    [대장님 🎯] GolfzonCommon의 도메인별 설계도를 필요할 때만 로드하는 라우터
    """
    
    @staticmethod
    def get_master():
        return {
            "flow": "Project -> GolfzonCommon Modules (Static/Singleton Access)",
            "purpose": "Provide standardized utilities and security/system bridges across all Golfzon apps"
        }

    @staticmethod
    def get_domain_spec(domain: str) -> Optional[dict]:
        domain_path = domain.lower().replace("/", ".")
        try:
            module_path = f"tenants.projects.golfzon.libraries.common.blueprints.{domain_path}"
            module = importlib.import_module(module_path)
            
            domain_name = domain.split("/")[-1]
            class_name = f"{domain_name.capitalize()}Spec"
            spec_class = getattr(module, class_name)
            return spec_class.get_spec()
        except (ImportError, AttributeError):
            return None
