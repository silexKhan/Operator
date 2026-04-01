#
#  scanner.py - Dynamic Codebase Inspector & Metadata Extractor
#

import os
import ast
from typing import Dict, List, Any, Optional
from core.logger import OperatorLogger

class CodeScanner:
    """
    [사용자] 프로젝트 소스 코드를 실시간으로 스캔하여 
    클래스, 메서드, 독스트링 정보를 추출하는 동적 설계도 생성기입니다. 
    """
    def __init__(self, root_path: str):
        self.root_path = root_path
        self.logger = OperatorLogger("CodeScanner")

    def scan_specs(self, circuit_path: str) -> Dict[str, str]:
        """[사용자] 회선 내 'specs/' 폴더의 기획 문서 목차를 스캔합니다. (Lazy Load 대응) """
        specs_path = os.path.join(circuit_path, "specs")
        specs_metadata = {}
        
        if not os.path.exists(specs_path) or not os.path.isdir(specs_path):
            return {}

        for file_name in os.listdir(specs_path):
            if file_name.endswith(".md"):
                file_path = os.path.join(specs_path, file_name)
                try:
                    with open(file_path, "r", encoding="utf-8") as f:
                        first_line = f.readline().strip()
                        # H1(#) 제목 추출 시도, 없으면 파일명 사용
                        title = first_line.lstrip("# ").strip() if first_line.startswith("#") else file_name
                        specs_metadata[file_name] = title
                except Exception as e:
                    specs_metadata[file_name] = f"Error: {str(e)}"
        
        return specs_metadata

    def read_spec_content(self, circuit_path: str, spec_file: str) -> Optional[str]:
        """[사용자] 특정 스펙 파일의 전체 내용을 읽어옵니다. (Surgical Load) """
        spec_path = os.path.join(circuit_path, "specs", spec_file)
        if os.path.exists(spec_path):
            try:
                with open(spec_path, "r", encoding="utf-8") as f:
                    return f.read()
            except Exception as e:
                self.logger.error(f"Failed to read spec {spec_file}: {str(e)}")
        return None

    def scan_operational_metadata(self, circuit_dir: str) -> Dict[str, Any]:
        """[사용자] 회선의 overview.json과 protocols.json을 읽어 운영 메타데이터를 추출합니다. """
        from shared.utils import read_json_safely
        
        overview = read_json_safely(os.path.join(circuit_dir, "overview.json"))
        protocols = read_json_safely(os.path.join(circuit_dir, "protocols.json"))
        
        return {
            "name": overview.get("name", os.path.basename(circuit_dir)),
            "description": overview.get("description", ""),
            "units": overview.get("units", []),
            "dependencies": overview.get("dependencies", []),
            "rules": protocols.get("RULES", [])
        }

    def read_unit_protocols(self, unit_name: str) -> Dict[str, Any]:
        """[사용자] 특정 기술 유닛의 규약(Mission 및 Rules)을 읽어옵니다. """
        from shared.utils import read_json_safely
        unit_path = os.path.join(self.root_path, "units", unit_name, "protocols.json")
        data = read_json_safely(unit_path)
        return {
            "name": unit_name,
            "mission": data.get("OVERVIEW", ""),
            "rules": data.get("RULES", [])
        }

    def scan_directory(self, subdir: str) -> Dict[str, Any]:
        """[사용자] 특정 도메인(폴더)을 실시간으로 분석하여 상세 설계도를 생성합니다. """
        target_path = os.path.join(self.root_path, subdir)
        if not os.path.exists(target_path):
            return {"error": f"Path not found: {target_path}"}

        metadata = {
            "name": f"Dynamic {subdir.capitalize()} Domain",
            "path": target_path,
            "files": {}
        }

        for root, _, files in os.walk(target_path):
            for file in files:
                if file.endswith(".py") and not file.startswith("__"):
                    file_path = os.path.join(root, file)
                    rel_path = os.path.relpath(file_path, target_path)
                    metadata["files"][rel_path] = self._parse_file(file_path)

        return metadata

    def _parse_file(self, file_path: str) -> Dict[str, Any]:
        """AST를 사용하여 단일 Python 파일의 구조를 정밀 분석합니다. """
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                node = ast.parse(f.read())

            file_info = {
                "docstring": ast.get_docstring(node) or "No documentation provided.",
                "classes": {},
                "functions": []
            }

            for item in node.body:
                if isinstance(item, ast.ClassDef):
                    class_info = {
                        "docstring": ast.get_docstring(item) or "No class description.",
                        "methods": []
                    }
                    for sub_item in item.body:
                        if isinstance(sub_item, ast.FunctionDef):
                            args = [arg.arg for arg in sub_item.args.args if arg.arg != "self"]
                            class_info["methods"].append({
                                "name": sub_item.name,
                                "args": args,
                                "docstring": ast.get_docstring(sub_item) or "No method description."
                            })
                    file_info["classes"][item.name] = class_info
                
                elif isinstance(item, ast.FunctionDef):
                    args = [arg.arg for arg in item.args.args]
                    file_info["functions"].append({
                        "name": item.name,
                        "args": args,
                        "docstring": ast.get_docstring(item) or "No function description."
                    })

            return file_info
        except Exception as e:
            return {"error": f"Failed to parse: {str(e)}"}

    @classmethod
    def get_project_structure(cls, project_root: str, registered_circuits: List[str] = None) -> Dict[str, Any]:
        """[사용자] 전체 프로젝트의 구조적 요약을 생성합니다. (웹 UI용 기초 데이터) """
        scanner = cls(project_root)
        
        # 실제 units 폴더 내의 유닛 목록 추출
        units_path = os.path.join(project_root, "units")
        active_units = []
        if os.path.exists(units_path):
            active_units = [d for d in os.listdir(units_path) if os.path.isdir(os.path.join(units_path, d)) and not d.startswith("__")]

        structure = {
            "core": scanner.scan_directory("core"),
            "circuits": scanner.scan_directory("circuits"),
            "units": scanner.scan_directory("units"),
            "active_units": active_units,
            "specs": scanner.scan_specs(project_root),
            "registered_circuits": registered_circuits or [],
            "dependency_graph": {
                "nodes": [{"id": name, "label": name.upper()} for name in (registered_circuits or [])],
                "links": []
            }
        }
        return structure
