# 🏗️ MCP Operator 시스템 구조 명세서

이 문서는 MCP(Model Context Protocol) 오퍼레이터 시스템의 물리적 디렉토리 구조와 각 파일의 역할을 정의한다.

## 1. 최상위 구조 (Root Layout)

```text
MCP/
├── mcp_operator/          # 시스템의 심장부 (백엔드 엔진)
├── hovercraft/            # 차세대 관리 인터페이스 (React/Next.js)
├── data/                  # 실시간 시스템 상태 및 히스토리 (State Sanctuary)
├── logs/                  # 시스템 통합 로그 저장소
└── mission.json           # 현재 시스템 전체의 글로벌 미션 정의
```

## 2. 세부 모듈 설명

### 🏢 2.1 mcp_operator (Backend Engine)
AI 모델과 실제 시스템을 연결하고, 정해진 규약에 따라 동작을 감사(Audit)하는 핵심 로직이 위치한다.
- **engine/**: 서버 가동 및 센티널(Sentinel) 무결성 검사기 위치.
- **registry/**: 회선(Circuits)과 유닛(Units)의 정의 저장소.
  - **circuits/**: 업무 맥락별 격리된 작업 환경 정의. (예: core, legacy, research)
  - **units/**: 특정 기술 스택이나 역할에 특화된 도구 정의. (예: swift, python, dev, sentinel)

### 🚀 2.2 hovercraft (Management UI)
엔지니어가 시스템 상태를 한눈에 파악하고 제어할 수 있는 GUI 대시보드이다.
- **app/**: Next.js App Router 기반의 페이지 및 API 라우트.
- **src/components/**: 원자 단위로 쪼개진 반응형 UI 컴포넌트들.
- **src/lib/**: 엔진과의 통신을 위한 브릿지 로직.

## 3. 데이터 흐름 (Data Flow Architecture)

1.  **State Sync**: 엔진에서 발생하는 모든 변화는 `data/state.json`에 기록된다.
2.  **Reactive IPC**: Hovercraft UI는 SSE(Server-Sent Events)를 통해 엔진의 상태 변화를 즉시 반영한다.
3.  **Governance Loop**: 엔지니어가 UI에서 설정을 변경하면, 백엔드 API가 이를 물리 파일에 기록하고 센티널이 무결성을 검증한다.

## 4. 확장 가이드

본 시스템은 특정 도메인(Legacy, Research 등)에 특화된 로직이 격리되어 작동하는 환경입니다. 새로운 회선을 추가하거나 유닛을 확장함으로써 어떠한 복잡한 하네스 엔지니어링 프로젝트에도 대응할 수 있습니다.
