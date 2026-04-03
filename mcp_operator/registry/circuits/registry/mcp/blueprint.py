#
#  blueprint.py - Dynamic Architecture Detail (Circuit & Protocol Edition) 
#

import os
import inspect
from mcp_operator.engine.scanner import CodeScanner
from mcp_operator.engine.protocols import GlobalProtocols

from mcp_operator.common.utils import get_project_root

class BluePrint:
    PROJECT_ROOT = get_project_root()
    
    @classmethod
    def get_master(cls) -> dict:
        """[사용자] 전체 시스템의 데이터 흐름과 메인 설계를 반환합니다. 
        추가로 'specs/' 폴더 내의 기획 문서 목차(Metadata)를 제공합니다. (Lazy Load) 
        """
        scanner = CodeScanner(cls.PROJECT_ROOT)
        circuit_path = os.path.dirname(__file__)
        specs_metadata = scanner.scan_specs(circuit_path)

        return {
            "flow": {
                "Data": "MCP Client (Gemini) -> Operator (교환) (Python) -> Circuit Line -> Protocol Logic",
                "Navigation": "Circuit Selection -> Path Sync -> Action Trigger -> Result Return",
                "Spec_Mode": "Lazy Load (Index-based) "
            },
            "bindings": {
                "CircuitManager": "Dynamic line discovery & connection",
                "OperatorLogger": "Centralized emoji logging system",
                "MCPServer": "Protocol handling via Hub Engine"
            },
            "spec_index": specs_metadata if specs_metadata else "No spec documents found in 'specs/'"
        }

    @classmethod
    def get_spec_detail(cls, spec_file: str) -> dict:
        """[사용자] 특정 스펙 파일의 상세 내용을 로드합니다. (Surgical Load) """
        scanner = CodeScanner(cls.PROJECT_ROOT)
        circuit_path = os.path.dirname(__file__)
        content = scanner.read_spec_content(circuit_path, spec_file)
        
        if content:
            return {"file": spec_file, "content": content}
        return {"error": f"Spec file '{spec_file}' not found."}

    @classmethod
    def get_domain_spec(cls, domain: str) -> dict:
        """[사용자] 특정 도메인을 실시간으로 분석하여 상세 설계도를 생성합니다. """
        scanner = CodeScanner(cls.PROJECT_ROOT)
        # 용어 정규화: Circuits 체계 준수 
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
    def get_full_structure(cls, manager=None) -> dict:
        """[사용자] 웹 UI 구축을 위한 오퍼레이터의 가용 역량(Capability) 지도를 생성합니다. """
        scanner = CodeScanner(cls.PROJECT_ROOT)
        
        # 1. 시스템 기본 정보
        active_circuit = manager.get_active_circuit() if manager else None
        structure = {
            "system": {
                "status": "Online",
                "active_circuit": active_circuit.get_name() if active_circuit else "None",
                "project_root": cls.PROJECT_ROOT
            },
            "global_protocols": GlobalProtocols.get_rules(),
            "circuits": []
        }

        # 2. 회선별 상세 역량 맵핑
        if manager:
            for name, circuit in manager.circuits.items():
                try:
                    circuit_dir = os.path.dirname(inspect.getfile(circuit.__class__))
                    
                    # 운영 메타데이터 스캔 (overview, protocols)
                    meta = scanner.scan_operational_metadata(circuit_dir)
                    
                    # 유닛별 미션/규약 정밀 분석
                    units_detail = []
                    for unit_name in meta.get("units", []):
                        units_detail.append(scanner.read_unit_protocols(unit_name))
                    
                    circuit_info = {
                        "id": name.upper(),
                        "name": meta.get("name"),
                        "description": meta.get("description"),
                        "units": units_detail,
                        "protocols": meta.get("rules", []),
                        "actions": [
                            {"name": t.name, "description": t.description} 
                            for t in circuit.get_tools()
                        ],
                        "dependencies": meta.get("dependencies", []),
                        "is_active": (active_circuit == circuit)
                    }
                    structure["circuits"].append(circuit_info)
                except Exception:
                    continue
        
        return structure
