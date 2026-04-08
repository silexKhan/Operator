# 🛰️ MCP Architecture Specification (시스템 정밀 구조 명세)

본 문서는 **Operator (교환)** 시스템의 물리적 소스 코드 구조와 런타임 메커니즘을 상세히 기술합니다.

---

## 1. 전역 아키텍처 (Global Architecture)

시스템은 **중앙 지휘(Engine)**, **도메인 격리(Circuits)**, **전문 도구(Units)** 세 개의 핵심 레이어로 분리됩니다.

### 디렉토리 구조 상세 (Project Layout)
```text
/MCP (Root)
├── mcp_operator/               # 백엔드 엔진 핵심
│   ├── engine/                 # 교환소(Operator) 핵심 로직
│   │   ├── server.py           # FastAPI/MCP 서버 엔트리
│   │   ├── actions.py          # 전역 핵심 액션 컨트롤러
│   │   ├── scanner.py          # 정적 분석 및 안전 가드 (AST)
│   │   ├── sentinel.py         # 런타임 미션 감시 및 평가
│   │   └── protocols.py        # 시스템 Constitution (규약) 관리
│   ├── registry/               # 기술 자산 등록소
│   │   ├── circuits/           # 도메인별 작업 회선 (Circuits)
│   │   │   ├── manager.py      # 회선 교환 및 상태 관리자
│   │   │   └── base.py         # 추상 회선 베이스 클래스
│   │   └── units/              # 전문 기술 유닛 (Tech Units)
│   │       ├── python/         # Python 코드 정밀 감사 유닛
│   │       ├── swift/          # Swift 코드 분석 유닛
│       └── sentinel/       # 미션 검증 특화 유닛
└── main.py                 # 서버 기동 진입점
├── hovercraft/                 # Next.js 기반 비주얼 관제소
├── data/                       # 상태 영속성 (JSON/DB)
└── requirements.txt            # 파이썬 의존성 목록
```

---

## 2. 핵심 레이어 상세 (Core Layer Analysis)

### A. Engine (지휘소)
AI 에이전트의 모든 요청을 중계하고, 규약을 강제하며, 안전성을 검증합니다.
- **`actions.py`**: 모든 도메인에서 공통적으로 필요한 '상태 확인', '회선 전환', '디렉토리 탐색' 등의 원자적 기능을 구현합니다.
- **`scanner.py`**: AI가 작성하거나 수정한 코드를 실행 전 AST(Abstract Syntax Tree) 레벨에서 분석하여 금지된 함수 호출이나 보안 위협을 차단합니다.
- **`sentinel.py`**: 작업 시작 시 설정된 '미션 목표'와 '성공 기준'을 바탕으로 최종 산출물을 정밀 평가(Autopilot)합니다.

### B. Circuit (작업 회선)
특정 도메인(GDR, Research 등)에 특화된 로직이 격리되어 작동하는 환경입니다.
- **`CircuitManager`**: 런타임에 회선을 실시간으로 교환하며, 전환 시 해당 도메인의 전용 규약(Protocols)을 시스템 프롬프트에 동적으로 주입합니다.
- **Registry 구조**: 신규 도메인 추가 시 `mcp_operator/registry/circuits/registry/` 내에 새로운 모듈을 등록하는 방식으로 확장성을 보장합니다.

### C. Units (전문 도구)
특정 언어나 기술 스택에 특화된 정밀 분석 도구 모음입니다.
- **`Audit Rules`**: 각 유닛은 고유의 감사 규칙을 가지며, 소스 코드의 스타일, 성능, 보안 결함을 진단합니다.

### 🛰️ MCP Operator 2.0 통합 지휘 체계 (Unified API)

시스템 복잡도를 낮추기 위해 파편화된 도구들을 4개의 핵심 인터페이스로 통합하였습니다.

| 통합 함수 (Tool) | 설명 | 주요 Target (Enum) |
| :--- | :--- | :--- |
| **`mcp_operator_get`** | 시스템 정보 및 상태 조회 | `PROTOCOL`, `OVERVIEW`, `BLUEPRINT`, `SPEC`, `MISSION`, `STATUS` |
| **`mcp_operator_update`** | 규약 및 메타데이터 수정 | `PROTOCOL`, `OVERVIEW`, `MISSION` |
| **`mcp_operator_create`** | 신규 구성 요소 생성 | `CIRCUIT`, `UNIT`, `SPEC` |
| **`mcp_operator_execute`** | 고부하 액션 실행 | `AUDIT`, `RELOAD` |

---

## 3. 런타임 흐름 (Operational Flow)

1.  **Server Startup**: `main.py` 실행 시 MCP 서버가 가동되며 기본 `mcp` 회선이 연결됩니다.
2.  **Circuit Switching**: 사용자/AI가 "회선 전환" 요청 시 `CircuitManager`가 기존 상태를 스냅샷으로 저장하고 대상 회선의 로직을 활성화합니다.
3.  **Protocol Injection**: 활성화된 회선과 배속된 유닛들의 규약(`protocols.json`)이 AI의 컨텍스트에 즉시 주입됩니다.
4.  **Sentinel Autopilot Check**: 모든 코드 수정이나 파일 작업은 `Scanner`와 `Sentinel`의 검증을 통과해야 실제 파일 시스템에 반영됩니다.


---

## 4. 기술 스택 (Technical Stack)

- **언어**: Python 3.10+
- **서버 프레임워크**: FastAPI (MCP Protocol 연동)
- **데이터 검증**: Pydantic v2
- **정적 분석**: AST (Python Native), Ruff (Linter), Mypy (Type Checker)
- **프론트엔드**: Next.js 14, TailwindCSS, Lucide-React

---
*최종 업데이트: 2026-04-03*
*작성 주체: MCP Operator (with Core Engine)*
