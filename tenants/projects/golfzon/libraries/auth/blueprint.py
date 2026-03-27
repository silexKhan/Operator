#
#  blueprint.py - GolfzonAuth Blueprint Router
#

import importlib
from typing import Optional

class BluePrint:
    """
    [대장님 🎯] GolfzonAuth의 도메인별 설계도를 필요할 때만 로드하는 라우터
    """
    
    @staticmethod
    def get_master():
        return {
            "flow": "App -> AuthManager -> (AuthService & AuthStorage) -> Token/Session",
            "purpose": "Provide unified authentication and screen login services for Golfzon ecosystem"
        }

    @staticmethod
    def get_domain_spec(domain: str) -> Optional[dict]:
        # [대장님 🎯] 하위 디렉토리(예: auth/core) 대응을 위해 경로 치환
        domain_path = domain.lower().replace("/", ".")
        try:
            module_path = f"tenants.projects.golfzon.libraries.auth.blueprints.{domain_path}"
            module = importlib.import_module(module_path)
            
            # 클래스 이름 규칙: 마지막 단어 추출 (core -> CoreSpec)
            domain_name = domain.split("/")[-1]
            class_name = f"{domain_name.capitalize()}Spec"
            spec_class = getattr(module, class_name)
            return spec_class.get_spec()
        except (ImportError, AttributeError):
            return None
