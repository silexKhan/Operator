# MCP 정밀 구조 명세서 (MCP Architecture Specification)

이 문서는 MCP(Mission Control & Protocol) 프로젝트의 파이썬 소스 코드 전수에 대한 정밀 분석 결과이다. 시스템의 구조, 역할, 특징 및 규약 강제 메커니즘을 정의한다.

---

## 1. 시스템 개요 (System Overview)
MCP는 AI 에이전트의 행동을 규제하고, 도메인별 미션(GDR, Research 등)을 수행하며, 중앙 집중식 통제 및 정밀 코드 감사를 수행하는 **지휘 AI 프레임워크**이다.

### 핵심 아키텍처 원칙:
- **Clean Architecture:** 계층적 분리를 통한 유지보수성 확보
- **Async-First:** 모든 I/O 및 통신 로직의 비동기 처리 (`asyncio`)
- **Strict Schema:** `Pydantic` 모델을 통한 엄격한 데이터 규격화
- **Dynamic Switching:** `Circuit` 시스템을 통한 런타임 도메인 전환

---

## 2. 도메인별 정밀 분석 (Domain Deep Dive)

### A. Core Domain (엔진 핵심)
엔진의 지휘, 맥락 공급, 안전성 확보를 담당한다.

| 파일명 | 주요 클래스/함수 | 역할 | 특징 |
| :--- | :--- | :--- | :--- |
| `server.py` | `MCPServer`, `App` | MCP 서버 엔트리포인트 및 API 핸들러 | FastAPI 기반 비동기 서버, 런타임 리로드 지원 |
| `actions.py` | `CoreActions` | 시스템 전역 핵심 액션 컨트롤러 | 모든 도메인에서 공통으로 사용되는 기본 기능 정의 |
| `scanner.py` | `CodeScanner` | 정적/동적 코드 분석 엔진 | `ast` 모듈을 이용한 문법 검사 및 위험 요소 탐색 |
| `protocols.py` | `ProtocolLoader` | 전사/회선별 규약 로더 | AI 시스템 프롬프트에 동적 규칙 주입 |
| `harness.py` | `ActionHarness` | AI 행동 규제 및 런타임 가드 | 실행 전 액션의 안전성을 물리적으로 검증/차단 |
| `interfaces.py` | `IMCPComponent` | 시스템 표준 인터페이스 정의 | 추상 베이스 클래스(ABC)를 통한 구조적 강제 |
| `logger.py` | `MCPLogger` | 정밀 추적 로깅 시스템 | 컨텍스트 기반 구조화된 로그 생성 |

### B. Circuit Domain (회선 및 도메인 로직)
도메인별 특화 기능을 격리하고 동적으로 교환하는 시스템이다.

| 파일명 | 주요 클래스/함수 | 역할 | 특징 |
| :--- | :--- | :--- | :--- |
| `manager.py` | `CircuitManager` | 회선 교환 및 상태 관리자 | 싱글톤 패턴, 런타임 회선 전환 로직 구현 |
| `base.py` | `BaseCircuit` | 회선 최상위 추상 클래스 | 모든 회선이 상속해야 할 기본 필드 및 메서드 정의 |
| `registry/mcp/` | `MCPCircuit` | 지휘부 전용 회선 | 시스템 설정, 유닛 관리 등 내부 통제 기능 |
| `registry/gdr/` | `GDRCircuit` | GDR 도메인 특화 회선 | GDR 코드 감사, 규약 준수 확인 등 도메인 로직 |
| `registry/research/` | `ResearchCircuit` | 리서치 및 분석 회선 | 웹 검색, 논문 요약 등 외부 정보 수집 및 분석 |

### C. Units & Shared (전문 유닛 및 공통 인프라)
특정 작업에 특화된 도구와 시스템 전역에서 사용하는 공통 자산이다.

| 파일명 | 주요 클래스/함수 | 역할 | 특징 |
| :--- | :--- | :--- | :--- |
| `shared/models.py` | `BaseModel`, `Response` | 시스템 전역 데이터 규격화 | `Pydantic` 기반의 엄격한 타입 체크 및 직렬화 |
| `shared/utils.py` | `get_project_root` | 공통 유틸리티 함수 | 경로 계산, 시간 포맷팅 등 재사용 가능 로직 |
| `units/python/` | `PythonAuditor` | 파이썬 코드 정밀 감사 유닛 | `ruff`, `mypy` 등과 연동된 코드 품질 검증 |
| `units/sentinel/` | `SentinelAuditor` | 미션 달성도 평가 유닛 | 대장님의 지시사항과 결과물의 일치도 평가 |
| `main.py` | `main()` | CLI 엔트리포인트 | 인자 처리 및 시스템 초기화 시퀀스 제어 |
| `mcp_cli.py` | `MCP_CLI` | 대화형 CLI 인터페이스 | 사용자-AI 간의 인터랙티브 셸 구현 |

---

## 3. 핵심 매커니즘 (Key Mechanisms)

### 1) AI 행동 규제 (Safety Guard)
AI가 생성한 코드는 실행 전 반드시 **`scanner.py`**와 **`harness.py`**를 거친다.
- **정적 분석:** `ast` 파싱을 통해 위험한 함수(`eval`, `os.system` 등) 사용 여부 확인
- **런타임 가드:** 설정된 규약(`protocols.py`)에 반하는 행동을 실시간으로 차단

### 2) 동적 회선 교환 (Dynamic Switching)
대장님이 "회선 전환" 명령을 내리면 **`CircuitManager`**는 다음을 수행한다.
1. 기존 회선의 상태 저장 (Snapshot)
2. 새로운 회선의 `overview.py` 및 `actions.py` 로드
3. AI 시스템 프롬프트에 새로운 도메인 지식 주입

### 3) 클린 아키텍처 메시지 흐름 (Message Flow)
`CLI -> main.py -> server.py -> CoreActions -> CircuitManager -> SpecificCircuit -> SharedModels -> Response`

---

## 4. 향후 고도화 제언
- **Unit Isolation:** 개별 유닛을 독자적인 프로세스(Sub-process)로 분리하여 물리적 보안 강화
- **State Persistence:** `state.json` 외에 로컬 DB(SQLite) 도입을 통한 대규모 세션 관리 최적화
- **Plugin System:** 새로운 회선을 소스 코드 수정 없이 추가할 수 있는 플러그인 인터페이스 구축

---
*작성 일시: 2026-04-03*
*분석 주체: MCP Operator (with Sentinel & Generalist Units)*
