# Modern Python Architecture & Convention Guide

이 가이드는 Swift의 MVVM과 유사하게 역할이 명확히 분리된 **Layered Architecture (Service-Repository Pattern)**를 지향합니다.

## 1. 아키텍처 계층 구조

| 계층 (Layer) | 역할 (Responsibility) | 특징 |
| :--- | :--- | :--- |
| **Domain/Models** | 순수 비즈니스 객체 및 스키마 | Pydantic 모델, Enum 사용 (의존성 없음) |
| **Repository** | 데이터 접근 로직 (I/O) | DB, File, 외부 API 등 데이터의 영속성 담당 |
| **Service** | 핵심 비즈니스 로직 | 여러 Repository를 조합하여 복잡한 로직 수행 |
| **API/Interface** | 외부 노출 접점 (Entry Point) | FastAPI Route, CLI Command 등 |

## 2. 핵심 컨벤션 (Modern Python Standards)

- **Type Hinting (PEP 484):** 모든 함수 인자와 반환값에 타입을 명시합니다.
  ```python
  def get_user(user_id: str) -> Optional[User]: ...
  ```
- **Asynchronous Programming (Async/Await):** I/O 바운드 작업은 반드시 비동기로 작성합니다.
- **Data Validation (Pydantic):** 데이터의 형태와 유효성 검증은 Pydantic을 활용합니다.
- **Docstrings (Google Style):** 함수의 목적과 인자, 반환값을 명확히 기술합니다.

## 3. 코드 구조 예시

```python
# [Models]
class User(BaseModel):
    id: str
    name: str

# [Repository]
class UserRepository:
    async def find_by_id(self, user_id: str) -> Optional[User]:
        # 데이터베이스 조회 로직
        return User(id=user_id, name="Example")

# [Service]
class UserService:
    def __init__(self, repo: UserRepository):
        self.repo = repo

    async def get_user_profile(self, user_id: str) -> User:
        user = await self.repo.find_by_id(user_id)
        if not user:
            raise UserNotFoundException()
        return user
```

## 4. 금기 사항 (Anti-Patterns)
- **Global Variables:** 전역 상태 공유를 지양하고 의존성 주입(DI)을 활용합니다.
- **Fat Controllers:** API 핸들러에 비즈니스 로직을 직접 구현하지 않고 Service로 위임합니다.
- **Magic Numbers:** 하드코딩된 값 대신 상수나 Enum을 사용합니다.
