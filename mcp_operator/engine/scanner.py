#
#  scanner.py - Dynamic Codebase Inspector & Metadata Extractor (Strict Clean Architecture)
#

import os
import ast
from typing import Dict, List, Any, Optional, Tuple
from mcp_operator.engine.logger import OperatorLogger

class CodeScanner:
    """
    [Main Class] 프로젝트 소스 코드를 정적/동적으로 분석하여 메타데이터를 추출하는 엔진입니다. (Protocol P-1)
    
    [Specification] 반환 데이터 구조 (Project Structure Schema)
    - core/circuits/units: 각 도메인의 파일 트리 및 구조 (Class, Method, Docstring)
    - active_units: 현재 시스템에 물리적으로 존재하는 기술 유닛 목록
    - specs: 프로젝트 루트 및 회선별 기획 문서 목차
    """
    
    def __init__(self, root_path: str):
        """
        CodeScanner 초기화
        :param root_path: 분석 대상 프로젝트의 최상단 루트 경로
        """
        self.root_path = root_path
        self.logger = OperatorLogger("CodeScanner")

    # -------------------------------------------------------------------------
    # [Handlers] 공개 분석 인터페이스 (Protocol P-4)
    # -------------------------------------------------------------------------

    def scan_specs_handler(self, circuit_path: str) -> Dict[str, str]:
        """[Handler] 특정 경로 하위의 'specs/' 폴더 내 마크다운 문서 목차를 스캔합니다."""
        return self._scan_markdown_files(os.path.join(circuit_path, "specs"))

    def read_spec_handler(self, circuit_path: str, spec_file: str) -> Optional[str]:
        """[Handler] 특정 스펙 파일의 리터럴 텍스트 내용을 안전하게 읽어옵니다."""
        return self._read_file_safe(os.path.join(circuit_path, "specs", spec_file))

    def scan_directory_handler(self, subdir: str) -> Dict[str, Any]:
        """[Handler] 특정 도메인 디렉토리를 순회하며 소스 코드 구조 설계도를 생성합니다."""
        target_path = os.path.join(self.root_path, subdir)
        if not os.path.exists(target_path):
            return {"error": f"Path not found: {target_path}"}

        return self._process_directory_tree(subdir, target_path)

    @classmethod
    def get_project_structure(cls, project_root: str, registered_circuits: List[str] = None) -> Dict[str, Any]:
        """
        [Handler] 전체 프로젝트의 구조적 요약을 통합 생성합니다. (웹 UI 동기화용)
        """
        scanner = cls(project_root)
        
        # 1. 물리적 유닛 탐색
        active_units = scanner._discover_active_units()

        # 2. 전체 구조 조립
        structure = {
            "core": scanner.scan_directory_handler("core"),
            "circuits": scanner.scan_directory_handler("circuits"),
            "units": scanner.scan_directory_handler("units"),
            "active_units": active_units,
            "specs": scanner.scan_specs_handler(project_root),
            "registered_circuits": registered_circuits or [],
            "dependency_graph": {
                "nodes": [{"id": name, "label": name.upper()} for name in (registered_circuits or [])],
                "links": []
            }
        }
        return structure

    # -------------------------------------------------------------------------
    # [Internal Helpers] 상세 분석 로직 (Protocol P-4)
    # -------------------------------------------------------------------------

    def _process_directory_tree(self, name: str, path: str) -> Dict[str, Any]:
        """디렉토리를 순회하며 파이썬 파일들을 분석합니다."""
        metadata = {
            "name": f"Dynamic {name.capitalize()} Domain",
            "path": path,
            "files": {}
        }

        for root, _, files in os.walk(path):
            for file in files:
                if self._is_target_file(file):
                    file_path = os.path.join(root, file)
                    rel_path = os.path.relpath(file_path, path)
                    metadata["files"][rel_path] = self._parse_source_code(file_path)
        return metadata

    def _parse_source_code(self, file_path: str) -> Dict[str, Any]:
        """AST를 사용하여 단일 파일의 구문을 정밀 분석합니다."""
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                node = ast.parse(f.read())

            return {
                "docstring": ast.get_docstring(node) or "No documentation provided.",
                "classes": self._extract_classes(node),
                "functions": self._extract_functions(node)
            }
        except Exception as e:
            return {"error": f"Failed to parse source: {str(e)}"}

    def _extract_classes(self, parent_node: ast.AST) -> Dict[str, Any]:
        """AST 노드에서 클래스 정의 정보를 추출합니다."""
        classes = {}
        for item in [n for n in parent_node.body if isinstance(n, ast.ClassDef)]:
            classes[item.name] = {
                "docstring": ast.get_docstring(item) or "No class description.",
                "methods": self._extract_methods(item)
            }
        return classes

    def _extract_methods(self, class_node: ast.ClassDef) -> List[Dict[str, Any]]:
        """클래스 노드 내부에서 메서드 정보를 추출합니다."""
        methods = []
        for item in [n for n in class_node.body if isinstance(n, ast.FunctionDef)]:
            args = [arg.arg for arg in item.args.args if arg.arg != "self"]
            methods.append({
                "name": item.name,
                "args": args,
                "docstring": ast.get_docstring(item) or "No method description."
            })
        return methods

    def _extract_functions(self, parent_node: ast.AST) -> List[Dict[str, Any]]:
        """모듈 수준의 독립 함수 정보를 추출합니다."""
        functions = []
        for item in [n for n in parent_node.body if isinstance(n, ast.FunctionDef)]:
            args = [arg.arg for arg in item.args.args]
            functions.append({
                "name": item.name,
                "args": args,
                "docstring": ast.get_docstring(item) or "No function description."
            })
        return functions

    def _scan_markdown_files(self, path: str) -> Dict[str, str]:
        """디렉토리 내의 마크다운 파일들의 제목을 추출합니다."""
        metadata = {}
        if not os.path.exists(path) or not os.path.isdir(path):
            return metadata

        for file_name in [f for f in os.listdir(path) if f.endswith(".md")]:
            file_path = os.path.join(path, file_name)
            metadata[file_name] = self._extract_md_title(file_path) or file_name
        return metadata

    def _extract_md_title(self, file_path: str) -> Optional[str]:
        """마크다운 파일의 첫 번째 H1 제목을 추출합니다."""
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                first_line = f.readline().strip()
                return first_line.lstrip("# ").strip() if first_line.startswith("#") else None
        except: return None

    def _read_file_safe(self, path: str) -> Optional[str]:
        """파일을 안전하게 읽어 반환합니다."""
        if os.path.exists(path):
            try:
                with open(path, "r", encoding="utf-8") as f: return f.read()
            except Exception as e:
                self.logger.log(f"Error reading file {path}: {str(e)}", 1)
        return None

    def _discover_active_units(self) -> List[str]:
        """물리적 디렉토리 구조를 기반으로 활성 유닛 목록을 반환합니다."""
        units_path = os.path.join(self.root_path, "units")
        if not os.path.exists(units_path): return []
        return [d for d in os.listdir(units_path) if os.path.isdir(os.path.join(units_path, d)) and not d.startswith("__")]

    def _is_target_file(self, file_name: str) -> bool:
        """분석 대상 파이썬 파일 여부를 판별합니다."""
        return file_name.endswith(".py") and not file_name.startswith("__")
