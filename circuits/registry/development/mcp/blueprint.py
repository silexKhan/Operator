#
#  blueprint.py - Dynamic Architecture Detail (Circuit & Protocol Edition) 📞⚡️
#

import os
from core.scanner import CodeScanner

class BluePrint:
    PROJECT_ROOT = "/Users/silex/workspace/private/MCP"
    
    @classmethod
    def get_master(cls) -> dict:
        """[대장님 🎯] 전체 시스템의 데이터 흐름과 메인 설계를 반환합니다. 🛡️⚡️"""
        return {
            "flow": {
                "Data": "MCP Client (Gemini) -> Operator (교환) (Python) -> Circuit Line -> Protocol Logic",
                "Navigation": "Circuit Selection -> Path Sync -> Action Trigger -> Result Return"
            },
            "bindings": {
                "CircuitManager": "Dynamic line discovery & connection",
                "OperatorLogger": "Centralized emoji logging system",
                "MCPServer": "Protocol handling via Hub Engine"
            }
        }

    @classmethod
    def get_domain_spec(cls, domain: str) -> dict:
        """[대장님 🎯] 특정 도메인을 실시간으로 분석하여 상세 설계도를 생성합니다. 🕵️‍♂️🔥"""
        scanner = CodeScanner(cls.PROJECT_ROOT)
        # 용어 정규화: Circuits 체계 준수 🛡️
        target_domain = "circuits" if domain.lower() in ["tenants", "circuits"] else domain.lower()
        
        if target_domain in ["core", "circuits", "language"]:
            metadata = scanner.scan_directory(target_domain)
            
            res = {
                "name": metadata.get("name", "Unknown Domain"),
                "desc": f"실시간 소스 코드 분석을 통한 {target_domain} 도메인 동적 설계도입니다.",
                "path": metadata.get("path"),
                "logic": f"Dynamic {target_domain} Logic extracted by AST",
                "components": {}
            }
            
            for rel_path, info in metadata.get("files", {}).items():
                components_str = []
                for cls_name, cls_info in info.get("classes", {}).items():
                    methods_str = [f"{m['name']}({', '.join(m['args'])})" for m in cls_info.get("methods", [])]
                    components_str.append(f"Class: {cls_name} [{', '.join(methods_str)}]")
                
                funcs_str = [f"{f['name']}({', '.join(f['args'])})" for f in info.get("functions", [])]
                if funcs_str:
                    components_str.append(f"Global Funcs: {', '.join(funcs_str)}")
                
                res["components"][rel_path] = " | ".join(components_str)
            
            return res
            
        return {"error": f"'{domain}' 도메인은 동적 분석 대상이 아닙니다."}

    @classmethod
    def get_full_structure(cls) -> dict:
        """[대장님 🎯] 웹 UI 구축을 위한 전 프로젝트의 JSON 명세 및 의존성 지도를 생성합니다. 🌐✨"""
        scanner = CodeScanner(cls.PROJECT_ROOT)
        
        # [대장님 🎯] 물리적 폴더명인 circuits를 정확히 스캔합니다! 🛡️⚡️
        structure = {
            "core": scanner.scan_directory("core"),
            "circuits": scanner.scan_directory("circuits"),
            "language": scanner.scan_directory("language"),
        }

        registry_path = os.path.join(cls.PROJECT_ROOT, "circuits", "registry")
        registered_circuits = []
        for root, dirs, files in os.walk(registry_path):
            if "actions.py" in files:
                registered_circuits.append(os.path.basename(root))
        
        structure["registered_circuits"] = registered_circuits
        structure["dependency_graph"] = cls._extract_dependencies(registered_circuits)
        
        return structure

    @classmethod
    def _extract_dependencies(cls, circuits: list) -> dict:
        nodes = []
        for c in circuits:
            # MCP_Operator는 특별 대우 🛡️
            group = 3 if c.lower() == "mcp" else 1
            nodes.append({"id": c.upper(), "group": group})
        return {"nodes": nodes, "links": []}
