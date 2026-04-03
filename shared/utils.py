#
#  utils.py - Common Utilities for MCP Operator (Strict Clean Architecture)
#

import os
import json
import sys
from typing import Any, Dict, Optional, Union

def get_project_root() -> str:
    """
    [Utility] 현재 모듈의 위치를 기준으로 MCP 최상단 루트 디렉토리의 절대 경로를 반환합니다.
    """
    return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# -------------------------------------------------------------------------
# [Handlers] JSON 데이터 입출력 엔진 (Protocol P-4)
# -------------------------------------------------------------------------

def read_json_safely(filepath: str, default_val: Any = None) -> Any:
    """
    [Handler] JSON 파일을 안전하게 읽어 반환합니다. 
    """
    if default_val is None:
        default_val = {}
        
    if not os.path.exists(filepath):
        return default_val
        
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, IOError):
        return default_val

def write_json_safely(filepath: str, data: Union[Dict, list], indent: int = 2) -> bool:
    """
    [Handler] 지정된 경로에 데이터를 JSON 형식으로 안전하게 저장합니다.
    stdout 오염 방지를 위해 에러는 stderr로 출력합니다.
    """
    try:
        directory = os.path.dirname(filepath)
        if directory and not os.path.exists(directory):
            os.makedirs(directory, exist_ok=True)
            
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=indent, ensure_ascii=False)
        return True
    except Exception as e:
        # [Critical] stdout 오염 방지: 모든 로그는 stderr로 출력 필수
        print(f"[Critical] Failed to write JSON to {filepath}: {str(e)}", file=sys.stderr)
        return False
