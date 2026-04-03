# [SPEC] Python Clean Architecture Convention

## 1. 개요 (Overview)
본 문서는 파이썬 기반 모든 프로젝트에서 준수해야 할 **Strict Service-Driven** 아키텍처 및 코딩 컨벤션을 정의한다. 오퍼레이터(AI)는 본 명세를 최우선 지침으로 삼아 코드를 생성 및 수정한다.

---

## 2. 아키텍처 원칙 (Architecture Principles)

### 2.1 Dumb Controller (Protocol P-1)
- **Controller/Router**(요청 수신부)는 '바보(Dumb)'여야 한다. 로직을 판단하거나 조건을 처리하지 않는다.
- 요청 데이터(Request)를 수집하여 **Service**에 넘기고, **Service**가 반환한 결과(Response)를 단순히 전달만 한다.

### 2.2 Service Input/Output Specification (Protocol P-2)
- 모든 입력과 출력은 **Pydantic Model**로 명확히 정의한다.
- **명세화 지침:** Input/Output 클래스는 시스템의 **최종 명세서**이다. 각 필드에는 상세한 주석(`Field(description=...)`)을 작성하여, 해당 클래스만 보아도 전체 기능 구조를 파악할 수 있어야 한다.

### 2.3 구현 예시 (Implementation Example)

```python
from enum import Enum, unique
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field

# 1. Enum 정의: 상태와 유형을 명확히 규정 (Protocol P-6)
@unique
class LoginStatus(str, Enum):
    """[Specification] 로그인 처리 결과 상태"""
    SUCCESS = "success"
    FAILED = "failed"
    LOCKED = "locked"

# 2. 입출력 명세: 시스템의 Interface이자 계약서 (Protocol P-2)
class UserLoginRequest(BaseModel):
    """[Specification] 사용자 로그인 요청 명세"""
    user_id: str = Field(..., description="사용자 식별자 (ID)")
    password: str = Field(..., description="로그인 비밀번호")

class UserLoginResponse(BaseModel):
    """[Specification] 사용자 로그인 응답 명세"""
    status: LoginStatus = Field(..., description="로그인 처리 결과 상태")
    message: str = Field(..., description="사용자에게 표시할 결과 메시지")
    token: Optional[str] = Field(None, description="인증 성공 시 발급되는 JWT 토큰")

# 3. Service: 비즈니스 로직의 핵심 (Protocol P-1, P-4)
class AuthService:
    async def login_handler(self, request: UserLoginRequest) -> UserLoginResponse:
        """[Core Pipeline] 로그인 비즈니스 로직 진입점"""
        
        # [Rule] 상세 로직은 내부 메서드로 분리하여 본체의 가독성 유지
        user_data = await self._authenticate_handler(request.user_id, request.password)
        
        # [Rule] match-case를 사용한 명확한 상태 분기 (Protocol P-7)
        match user_data.get("status"):
            case "valid":
                return UserLoginResponse(
                    status=LoginStatus.SUCCESS,
                    message="로그인 성공",
                    token="generated_token"
                )
            case "locked":
                return UserLoginResponse(status=LoginStatus.LOCKED, message="계정 잠김")
            case _: # [Safety] Wildcard 예외 처리 필수
                return UserLoginResponse(status=LoginStatus.FAILED, message="인증 실패")

    async def _authenticate_handler(self, user_id, password) -> Dict[str, Any]:
        """[Internal] 실제 DB 조회 및 암호 검증 수행 (상세 구현 분리)"""
        pass
```

---

## 3. 코딩 컨벤션 (Coding Standards)

### 3.1 명명 규칙 (Naming Convention)
- **Handler:** 서비스의 핵심 진입점 메서드는 반드시 **`[Action]handler`**로 명명한다.
- **Internal:** 내부 비즈니스 로직 메서드는 언더바(`_`)로 시작한다.

### 3.2 비동기 우선 (Async Safety - Protocol P-3)
- 모든 I/O 작업은 반드시 **`async/await`**을 사용하여 비동기로 처리한다.

### 3.3 명세화 주석 (Documentation - Protocol P-4)
- 모든 클래스와 함수에는 **Docstring**을 사용하여 역할과 인자, 반환값을 상세히 설명한다.

### 3.4 엄격한 상태 관리 (Strict Enum - Protocol P-6)
- 하드코딩된 값은 금지하며, 반드시 **`Enum`**을 사용하고 Pydantic 모델과 연동한다.

### 3.5 패턴 매칭 (Structural Pattern Matching - Protocol P-7)
- 복잡한 분기(`if-elif`) 대신 **`match-case`**를 사용하고 반드시 **`case _:`**를 포함한다.

### 3.6 배포 전 자가 검증 (Pre-flight Check - Protocol P-8)
- 코드 수정 후 리로드 전, 반드시 다음 정적 분석을 수행한다.
    1. `python3 -m py_compile [files]`: 문법 검사
    2. `mypy [files]`: 타입 및 참조 검사
- 오퍼레이터는 위 검증을 통과한 코드만 시스템에 반영한다.

---

## 5. 변경 이력 (Changelog)
- **2026.04.03**: Python Clean Architecture 초안 작성
- **2026.04.03**: Strict Enum 및 match-case 패턴 매칭 규약 추가
- **2026.04.03**: 런타임 에러 방지를 위한 Pre-flight Check(정적 분석) 규약 추가
