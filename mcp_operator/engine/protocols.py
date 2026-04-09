#
#  protocols.py - Global Universal Protocols (Level 0) with I18N Support
#

import os
from mcp_operator.engine.interfaces import BaseProtocols
from typing import List, Dict, Any
from mcp_operator.common.utils import get_project_root, read_json_safely

class GlobalProtocols(BaseProtocols):
    """
    [사용자] 전사 지배 규약(Global Protocols)입니다.
    I18N을 지원하며, protocols.json 파일에서 실시간으로 로드합니다.
    """

    def __init__(self, lang: str = None):
        """초기화 시 언어를 설정합니다. 
        1. 명시적 인자(lang)
        2. data/state.json의 'lang' 설정
        3. protocols.json의 'DEFAULT_LANGUAGE' (Fallback)
        """
        self.PROJECT_ROOT = get_project_root()
        self._data = self._load_full_data()
        self._current_lang = lang

        if self._current_lang is None:
            # data/state.json에서 현재 언어 설정 로드 시도
            state_path = os.path.join(self.PROJECT_ROOT, "data", "state.json")
            state_data = read_json_safely(state_path)
            if state_data and "lang" in state_data:
                self._current_lang = state_data["lang"]

        # 최종 Fallback
        if self._current_lang is None:
            self._current_lang = self._data.get("DEFAULT_LANGUAGE", "ko")
            
    def _load_full_data(self) -> Dict[str, Any]:
        """JSON 파일 전체를 로드합니다."""
        current_dir = os.path.dirname(os.path.abspath(__file__))
        json_path = os.path.join(current_dir, "protocols.json")
        return read_json_safely(json_path)

    def set_language(self, lang_code: str) -> bool:
        """언어를 변경합니다. 지원하지 않는 언어일 경우 False를 반환합니다."""
        supported_codes = [lang["code"] for lang in self._data.get("SUPPORTED_LANGUAGES", [])]
        if lang_code in supported_codes:
            self._current_lang = lang_code
            return True
        return False

    def get_current_language(self) -> str:
        """현재 활성화된 언어 코드를 반환합니다."""
        return self._current_lang

    def get_supported_languages(self) -> List[Dict[str, str]]:
        """지원되는 언어 목록을 반환합니다."""
        return self._data.get("SUPPORTED_LANGUAGES", [])

    def get_rules(self) -> List[str]:
        """현재 언어에 해당하는 규칙 리스트를 반환합니다."""
        lang_data = self._data.get("LANGUAGES", {}).get(self._current_lang, {})
        rules = lang_data.get("RULES", [])
        if not rules:
            return [f"Protocol 0-0: No rules found for language '{self._current_lang}'"]
        return rules

    def get_message(self, key: str, **kwargs) -> str:
        """현재 언어에 해당하는 메시지를 반환합니다."""
        lang_data = self._data.get("LANGUAGES", {}).get(self._current_lang, {})
        messages = lang_data.get("MESSAGES", {})
        template = messages.get(key, f"Unknown message key: {key}")
        try:
            return template.format(**kwargs)
        except KeyError:
            return template

    @classmethod
    def get_rules_legacy(cls) -> List[str]:
        """[LEGACY] 기존 정적 호출 대응용 (기본 언어로 반환)"""
        instance = cls()
        return instance.get_rules()
