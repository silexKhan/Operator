#
#  scanner.py - Dynamic Codebase Inspector & Metadata Extractor
#

import os
import ast
from typing import Dict, List, Any, Optional
from core.logger import OperatorLogger

class CodeScanner:
    """
    [대장님 🎯] 프로젝트 소스 코드를 실시간으로 스캔하여 
    클래스, 메서드, 독스트링 정보를 추출하는 동적 설계도 생성기입니다. 🛠️⚡️
    """
    def __init__(self, root_path: str):
        self.root_path = root_path
        self.logger = OperatorLogger("CodeScanner")

    def scan_directory(self, subdir: str) -> Dict[str, Any]:
        """특정 서브디렉토리의 모든 Python 파일을 스캔하여 메타데이터를 반환합니다. 🕵️‍♂️"""
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
        """AST를 사용하여 단일 Python 파일의 구조를 정밀 분석합니다. 🔍"""
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
    def get_project_structure(cls, project_root: str) -> Dict[str, Any]:
        """[대장님 🎯] 전체 프로젝트의 구조적 요약을 생성합니다. (웹 UI용 기초 데이터) 🌐"""
        scanner = cls(project_root)
        structure = {
            "core": scanner.scan_directory("core"),
            "circuits": scanner.scan_directory("circuits"),
            "language": scanner.scan_directory("language")
        }
        return structure
