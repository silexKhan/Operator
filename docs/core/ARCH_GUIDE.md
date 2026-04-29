# [ARCH] MCP Operator System Architecture Guide

## 1. 설계 철학 (Design Philosophy)
본 시스템은 **"Strict Service-Driven Architecture"**를 따르며, 이는 Swift의 Strict MVVM 철학을 파이썬에 이식한 형태이다. 모든 코드는 **명세(Specification) 우선**, **결벽증적 역할 분리**, **런타임 안정성**을 최우선 가치로 삼는다.

---

## 2. 지휘 계통 및 레이어 구조 (Layered Architecture)

### 2.1 Entry Layer (`main.py`)
- **역할:** 가상 환경(venv) 내에서 서버 엔진을 기동하는 최상위 엔트리포인트.
- **핵심:** 프로젝트 루트를 `sys.path`에 주입하여 모듈 간의 상대 참조 정합성을 보장한다.

### 2.2 Server Layer (`core/server.py` - `OperatorServer`)
- **역할:** MCP 표준 프로토콜을 구현하며 외부(Gemini 등)와의 통신을 중계하는 **중앙 오케스트레이터**.
- **Dumb Server 원칙:** 서버 클래스는 비즈니스 로직을 직접 수행하지 않고, 도구(Tool) 호출을 `CoreActions` 또는 각 `Circuit` 핸들러로 배분(Dispatch)하는 역할만 수행한다.
- **핵심 메서드:** `_setup_mcp_handlers`, `_dispatch_tool_handler`, `_refresh_tool_cache_handler`.

### 2.3 Action Layer (`core/actions.py` - `CoreActions`)
- **역할:** 시스템 전체를 관장하는 핵심 비즈니스 로직의 **통합 제어소**.
- **Handler Separation:** 모든 공개 메서드(status, active_circuit 등)는 핸들러로 기능하며, 실제 연산과 조합 로직은 `_build_xxx`, `_resolve_xxx`와 같은 내부 메서드로 철저히 분할되어 있다.

### 2.4 Infrastructure Layer (`circuits/manager.py` - `CircuitManager`)
- **역할:** 물리적 파일 시스템으로부터 회선(Circuit)을 자동 탐색하고 생명주기를 관리하는 **중앙 교환기**.
- **Persistence:** 시스템의 활성화 상태를 `state.json`에 영구 저장하고 동기화한다.

### 2.5 Analysis Engine (`core/scanner.py` - `CodeScanner`)
- **역할:** AST(Abstract Syntax Tree)를 사용하여 소스 코드를 정적으로 분석하고 동적 설계도를 추출하는 **지능형 분석기**.

---

## 3. 핵심 클래스 역할 상세 명세 (Class Roles)

| 클래스명 | 위치 | 주요 역할 (Responsibility) |
| :--- | :--- | :--- |
| **OperatorServer** | `core/server.py` | MCP 서버 구동, 도구/프롬프트 등록, 비동기 이벤트 루프 관리 |
| **CoreActions** | `core/actions.py` | 회선 전환 로직, 지휘소 카드(Context Card) 조립, 스펙 파일 탐색 |
| **CircuitManager** | `circuits/manager.py` | `actions.py` 자동 감지, 모듈 동적 리로드, 회선 인스턴스 맵핑 |
| **CodeScanner** | `core/scanner.py` | 마크다운 스펙 제목 추출, 파이썬 파일 구조(Class/Method) 파싱 |
| **McpCircuit** | `circuits/.../mcp/actions.py` | 오퍼레이터 전용 도구(코드 감사, 미션 설정 등) 핸들링 |
| **ResponseHandler** | `shared/models.py` | 모든 응답을 MCP 표준(`TextContent`)으로 직렬화하는 규격 엔진 |

---

## 4. 코딩 컨벤션 및 표준 규약 (Standard Protocols)

### 4.1 핸들러 명명 규칙 (P-4)
- 서비스 진입점은 반드시 **`[Action]_handler`** 형식을 사용한다.
- 상세 구현부는 언더바(`_`)로 시작하는 내부 메서드로 분리하여 가독성을 확보한다.

### 4.2 명세 기반 입출력 (P-2)
- 모든 데이터 교환은 **Pydantic Model** 또는 명확한 타입 힌트가 적용된 객체를 사용한다.
- `shared/models.py`의 `ResponseHandler`를 통해서만 응답을 생성하여 데이터 무결성을 유지한다.

### 4.3 현대적 패턴 활용 (P-7)
- 3개 이상의 분기나 상태 제어 시 `if-elif` 대신 **`match-case`**를 사용한다.
- 예외 방지를 위해 반드시 `case _:` (Wildcard)를 포함한다.

### 4.4 배포 전 검증 (P-8)
- 모든 코드 수정 후 서버 리로드 전 `py_compile` 및 `mypy`를 통한 정적 분석을 수행하여 런타임 에러를 사전에 차단한다.

---

**Last Updated:** 2026.04.03 (Refactored by Gemini AI Operator)
