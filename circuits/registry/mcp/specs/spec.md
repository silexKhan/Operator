# [SPEC] MCP Operator 시스템 명세서

## 1. 시스템 메타데이터 (Metadata)
- **ID**: MCP_OPERATOR_CORE
- **VERSION**: 1.1.0
- **AUTHORITY**: 사용자 (User)
- **OBJECTIVE**: 전 조직의 산출물을 일관된 표준(Protocols)으로 통제하고 회선을 중계함.

## 2. 핵심 구성 요소 정의 (Component Definitions)

### 2.1 Operator (중앙 관제 유닛)
- **Role**: 모든 통신의 중계 및 최종 규약 검증.
- **Key Actions**: 
  - Path Sync: 사용자의 지시를 분석하여 적절한 회선 식별.
  - Result Audit: 작업 완료 후 규약 준수 여부 최종 확인.
- **Target File**: `main.py`, `core/` 하위 모듈.

### 2.2 Circuits (도메인 격리 회선)
- **Role**: 특정 프로젝트 전용 작업 환경 제공.
- **Structure**: 
  - `actions.py`: 도구 정의 및 실행 로직.
  - `protocols.py`: 회선 전용 행동 수칙.
  - `blueprint.py`: 동적 설계도 및 스펙 인덱서.
- **Path**: `circuits/registry/{category}/{name}/`

### 2.3 Protocols (행동 구속 규약)
- **Type A (Global)**: `core/protocols.py`에 정의된 최상위 헌법 (불변 원칙).
- **Type B (Circuit)**: 각 회선별로 정의된 가변 기술 표준.
- **Priority**: Global > Circuit > Spec (상충 시 Global 우선).

### 2.4 Sentinel Engineering (Auto-pilot)
- **Logic**: Input -> [Sentinel Core Mission] -> [Autonomous Execution] -> [Audit].
- **Auto-pilot Mechanism**:
  - Detection: `specs/` 내 스펙 변화 감지 시 자율 주행 모드 자동 활성화.
  - Mission Setup: `sentinel_set_mission`을 통한 실시간 목표 수립.
  - Evaluation: 모든 산출물에 대해 `sentinel_evaluate`를 통한 품질 승인(PASS) 필수.
- **Target File**: `units/sentinel/` 및 전체 에셋 동기화.

### 2.5 Specs (실무 기획 명세)
- **Location**: `{circuit_path}/specs/*.md`
- **Mechanism**: 
  - Lazy Load: 초기 연결 시 목차만 로드하여 토큰 절약.
  - Surgical Fetch: 필요 시 `get_spec_content`를 통해 상세 내용 주입.

## 3. 작업 실행 프로토콜 (Operational Workflow)

1. **지시 분석 (Analysis)**: 사용자 지시 사항의 의도와 대상 도메인 식별.
2. **스펙 검사 (Spec-Check)**:
   - 가용한 `spec_index`를 스캔하여 관련 문서 확인.
   - 관련 문서가 존재하면 상세 내용을 읽어 구현 목표(Goal) 수립.
3. **명세 부재 처리 (Exception Handling)**:
   - 지시 사항이 스펙에 정의되지 않았거나 상충되는 경우 작업을 보류함.
   - 사용자에게 "명세 부재"를 보고하고 추가 지시를 대기함.
4. **구현 및 검증 (Act & Validate)**:
   - 규약(Protocols)을 준수하며 스펙(Specs)대로 구현.
   - 하네스(Harness) 규격에 어긋나지 않는지 최종 자가 진단.

## 4. 웹 관제소 (Web Control Interface)
사용자가 시스템 전반을 시각적으로 조망하고, 복잡한 회선 간의 관계를 관리하기 위한 인터페이스입니다. 데이터의 로드 방식에 따라 실시간 반영 여부가 결정됩니다.

### 4.1 구축 목적 (Objective)
- 가시성 확보: 수많은 회선 간의 물리적 연결 상태와 의존성(Dependency)을 시각화.
- 직접 제어: 소스 코드 수정 없이 웹 UI를 통해 규약(Protocols) 및 설정을 파일 시스템에 즉시 기록.
- 중앙 집중 관제: 모든 회선의 상태와 설정을 단일 지점에서 통합 관리.

### 4.2 데이터 갱신 및 리로드 규정 (Reload Policy - Full Sync)
시스템 구조 개선(JSON 기반 데이터 분리)을 통해 이제 대부분의 데이터가 엔진 재기동 없이 즉시 반영됩니다.

| 관리 대상 | 반영 상태 | 기술적 메커니즘 |
| :--- | :--- | :--- |
| **Web 대시보드 데이터** | **HOT (실시간)** | 물리적 JSON 및 MD 파일을 직접 읽어 파싱하므로 즉시 반영됨. |
| **Action 로직** | **HOT (실시간)** | CircuitManager가 `importlib.reload`를 수행하여 수정된 새 로직이 즉각 실행됨. |
| **AI 컨텍스트 카드** | **HOT (실시간)** | 규약(Protocols)을 메모리가 아닌 JSON 파일에서 직접 로드하여 즉시 반영됨. |
| **회선 목록 (Circuits)** | **WARM (반실시간)** | `sync_path` 명령을 명시적으로 실행해야 물리 폴더를 재스캔(Discover)함. |
| **MCP 환경 설정** | **COLD (재시작 필수)** | `mcp.json` 등 시스템 설정은 외부 MCP Host가 기동 시점에 읽으므로 전체 프로세스 재기동이 필수임. |

## 5. 환경 제어 (Environment Control)
- Runtime: Mac/Linux (./start.sh), Windows (web/start.bat).
- Control Interface: Web Dashboard (http://localhost:3000).
- Security: 보안 및 민감 데이터 노출 금지 (Global Protocol 0-3 준수).

---

## [부록] 시스템 아키텍처 상세 정의 (Core Concept)

### A.1 회선 (Circuit) 및 규약 (Protocol)
- **Circuit**: 특정 도메인(개발, 기획, 관리 등)에 특화된 독립적인 작업 환경.
- **Protocol**: 각 회선에서 AI가 반드시 준수해야 하는 행동 지침 및 기술 규정.
- **Spec (스펙)**: 회선 내 `specs/` 폴더에 보관된 기획 문서. AI가 무엇을(What) 해야 하는지 정의함.

### A.2 미션 수행 워크플로우
1. 사용자의 지시 사항을 분석한다.
2. 현재 활성화된 회선의 **Protocol**과 **Spec**을 동시에 참조한다.
3. 기획 의도(Spec)에 어긋나지 않으면서 행동 규칙(Protocol)을 준수하는 최적의 솔루션을 도출하고 실행한다.

