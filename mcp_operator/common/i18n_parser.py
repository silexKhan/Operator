from typing import Dict, Any, Union
from pydantic import BaseModel, Field, ValidationError

class I18NData(BaseModel):
    """다국어 데이터 스키마 정의"""
    ko: str = Field(default="[MISSING_TRANSLATION]")
    en: str = Field(default="[MISSING_TRANSLATION]")

class I18NParser:
    """
    [ADR-01] Python Native & Pydantic 기반의 표준 I18N 파서.
    데이터의 정합성을 보장하고 누락된 필드를 안전하게 처리합니다.
    """
    
    def parse(self, data: Union[Dict[str, Any], Any]) -> Dict[str, str]:
        """
        입력 데이터를 분석하여 표준 다국어 사전으로 변환합니다.
        
        Args:
            data: 파싱할 원본 데이터 (Dict 형식 기대)
            
        Returns:
            Dict[str, str]: ko/en 필드가 보장된 결과값
            
        Raises:
            ValueError: 입력 형식이 올바르지 않은 경우 (P-0 준수)
        """
        if not isinstance(data, dict):
            raise ValueError(f"Invalid data format: Expected dict, got {type(data).__name__}")
            
        try:
            # Pydantic을 통한 데이터 정합성 검증 및 기본값 주입
            validated = I18NData(**data)
            return validated.model_dump()
            
        except ValidationError as e:
            # 예상치 못한 데이터 오류 시 상세 로그와 함께 중단
            raise ValueError(f"Data validation failed: {str(e)}")
