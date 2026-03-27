#
#  blueprint.py - MCP Hub Architecture Detail
#

class BluePrint:
    MASTER_PLAN = {
        "flow": {
            "Data": "MCP Client (Gemini) -> Silex Hub (Python) -> Domain Tenant -> Target Logic",
            "Navigation": "Tenant Selection -> Path Sync -> Action Trigger -> Result Return"
        },
        "bindings": {
            "TenantManager": "Dynamic domain discovery & activation",
            "HubLogger": "Centralized emoji logging system",
            "MCPServer": "Protocol handling via Anthropic SDK"
        }
    }

    DOMAINS = {
        "mcp": {
            "name": "Silex MCP Domain",
            "desc": "Hub 자기 자신의 관리와 도구 제공을 담당하는 전용 전장입니다.",
            "path": "/Users/silex/workspace/private/MCP/tenants/projects/mcp/",
            "logic": "Self-Management and Tool definition for Hub core",
            "components": {
                "actions": "MCP 전용 도구(audit, overview, blueprint) 정의",
                "axioms": "Python 전용 공리 및 Hub 글로벌 공리 상속",
                "overview": "MCP 프로젝트 개요 정보"
            }
        },
        "core": {
            "name": "MCP Core Engine",
            "desc": "MCP Hub의 심장부로 프로토콜과 서버 기동을 담당합니다.",
            "path": "/Users/silex/workspace/private/MCP/core/",
            "logic": "Asynchronous IO and MCP Protocol handling",
            "components": {
                "mcp_server": "FastAPI/Starlette 기반 MCP 서버 구현",
                "logger": "대장님 스타일의 로그 출력기",
                "config": "환경 설정 주입기"
            }
        },
        "tenants": {
            "name": "Multi-Tenant Manager",
            "desc": "각 프로젝트(GDR, Auth 등)의 공리를 격격히 관리하는 도메인 관리자입니다.",
            "path": "/Users/silex/workspace/private/MCP/tenants/",
            "flow": {
                "Discovery": "actions.py 파일을 찾아 테넌트 자동 등록",
                "Activation": "set_active_tenant를 통한 강제 활성화"
            }
        }
    }

    @classmethod
    def get_master(cls) -> dict:
        return cls.MASTER_PLAN

    @classmethod
    def get_domain_spec(cls, domain: str) -> dict:
        return cls.DOMAINS.get(domain.lower())
