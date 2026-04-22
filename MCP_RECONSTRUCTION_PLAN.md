# 🏛️ MCP Operator Reconstruction Master Plan (2.0 Unified)

## 1. Core Philosophy: "The Unified Commander"
본 시스템은 더 이상 개별 회선이나 유닛의 파편화된 도구(Tool)를 허용하지 않는다. 모든 명령은 **중앙 지휘소(CoreActions)**를 통해 통합 관리되며, 각 회선과 유닛은 규격화된 **'인터페이스(Protocol)'**를 구현하여 이 거대한 유기체의 부품으로 기능한다.

### 핵심 원칙
- **Protocol-Driven:** Python 코드(`actions.py`) 없이 JSON 규약(`protocols.json`, `overview.json`)만으로도 회선/유닛이 즉시 생성되고 동작해야 한다. (Fallback to Base)
- **Polymorphic Commands:** `mcp_operator_[circuit]_[action]` 식의 네이밍을 금지한다. 오직 5대 통합 함수(`get`, `update`, `create`, `execute`, `mission`)만을 제공하며, 파라미터로 대상을 식별한다.
- **Inheritance-Based Dev:** 특수한 비즈니스 로직이 필요한 경우에만 Base 클래스를 상속받아 개발하며, 그 외에는 규약 추가만으로 시스템 확장이 가능해야 한다.

---

## 2. Structural Blueprint (Architecture Reconstruction)

### A. Unified Foundations (engine/interfaces.py)
모든 구성 요소의 뿌리를 규격화한다.
1. **`BaseComponent` (NEW):** 회선과 유닛의 공통 조상. `get_identity()`, `load_protocols()` 로직 보유.
2. **`BaseCircuit(BaseComponent)`:** Swift Protocol 스타일의 회선 부모. 기본 도구 처리 및 유닛 오케스트레이션 수행.
3. **`BaseUnit(BaseComponent)`:** 기술 전문가 유닛의 부모. `audit()` 및 전문 지식 제공 인터페이스 통합.

### B. Registry Engine Refactoring (registry/manager.py)
- **Dynamic Factory:** 디렉토리 스캔 시 `actions.py`가 있으면 로드하고, 없으면 `BaseCircuit/Unit`을 인스턴스화하여 즉시 투입.
- **Strict Validation:** 생성 시 필수 JSON 파일 부재 시 즉시 거부(Failure-Fast).

---

## 3. Unified Command API Specification (Flat Interface)

AI 에이전트에게 노출될 도구 목록은 아래와 같이 **'완전 평탄화'**된다.

| 통합 도구 | 주요 파라미터 | 역할 |
| :--- | :--- | :--- |
| **`get`** | `target` (overview\|protocol\|spec\|status), `name` (대상명) | 시스템, 회선, 유닛의 모든 메타데이터 통합 조회 |
| **`update`** | `target`, `name`, `data` (JSON) | 규약, 상태, 미션 정보를 실시간으로 수정 |
| **`create`** | `target` (circuit\|unit\|spec), `name`, `template` | 규격화된 뼈대를 가진 신규 구성 요소 물리적 생성 |
| **`execute`** | `action` (audit\|mission\|reload), `scope_name` | 지정된 범위에 대해 고부하 액션 수행 |
| **`mission`** | `context` (Objective/Criteria) | Sentinel 주도의 자율 7단계 파이프라인 트리거 |

---

## 4. Sentinel Transformation (The Pipeline Driver)
Sentinel은 이제 단순 유닛이 아니라 **'파이프라인 실행 엔진'** 그 자체가 된다.
- **Context Routing:** 미션이 하달되면 해당 프로젝트의 언어(Python, Swift 등)를 자동 감지.
- **Auditor Chaining:** 공통 감사(Sentinel) + 전문 감사(Language Unit)를 사슬처럼 엮어 최종 무결성 증명.
- **Automatic Archiving:** PASS 판정 시 물리적 파일 정리 및 컨텍스트 초기화 전담.

---

## 5. Implementation Roadmap (Phased Execution)

### Phase 1: Foundation (기반 구축)
- `BaseComponent`, `BaseUnit` 클래스 신설 및 `BaseCircuit` 고도화.
- `CircuitManager`를 'JSON-First' 팩토리 구조로 전면 개편.

### Phase 2: Flattening (도구 평탄화)
- `server.py`의 모든 개별 도구 매핑 삭제.
- `CoreActions`를 5대 통합 API 전용 핸들러로 리팩토링.
- 모든 회선의 `actions.py`를 삭제하거나 껍데기(Header)만 남김.

### Phase 3: Sentinel Sync (지휘 체계 연동)
- 7단계 파이프라인을 통합 API(`execute_mission`)에 완전히 녹여냄.
- 언어 감지 기반의 동적 Auditor 라우팅 로직 완성.

### Phase 4: Final Validation (검증 및 전환)
- 기존 `research`, `gdr` 회선을 새로운 구조로 마이그레이션.
- 구식 도구가 목록에 하나라도 남을 경우 '실패'로 간주하고 전수 청소.

---

**"이 문서는 확정된 설계도이며, 승인 즉시 파이프라인을 통해 물리적으로 집행된다."**
