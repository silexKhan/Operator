#
#  utils.py - Common Utilities for MCP Operator
#

import os
import json
from typing import Any

def get_project_root() -> str:
    """
    현재 파일(shared/utils.py)의 위치를 기준으로 MCP 최상단 루트 디렉토리의 절대 경로를 반환합니다.
    """
    return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def read_json_safely(filepath: str, default_val: Any = None) -> Any:
    """
    JSON 파일을 안전하게 읽어 반환합니다. 파일이 없거나 오류 발생 시 지정된 기본값을 반환합니다.
    """
    if default_val is None:
        default_val = {}
        
    if not os.path.exists(filepath):
        return default_val
        
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return default_val

def write_json_safely(filepath: str, data: Any, indent: int = 2) -> bool:
    """
    지정된 경로에 JSON 형식으로 데이터를 안전하게 저장합니다.
    """
    try:
        # 디렉토리가 없으면 생성
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=indent, ensure_ascii=False)
        return True
    except Exception as e:
        print(f"[Error] Failed to write JSON to {filepath}: {str(e)}")
        return False
