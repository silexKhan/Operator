# 🚀 HOVERCRAFT: MCP 오퍼레이터 지휘 센터 기획서 (PRD)

| 버전 | 일자 | 작성자 | 상태 |
| :--- | :--- | :--- | :--- |
| v2.0 | 2026-04-13 | Planning Unit | **FINAL (Detailed Truth Wall Locked)** |

---

## 1. 목적 (Purpose)
본 프로젝트의 목적은 MCP 오퍼레이터 엔진의 상태를 시각화하여 사용자(대장님)가 시스템을 직관적으로 제어할 수 있는 실시간 지휘 인터페이스를 제공하는 것이다. **(모든 기능은 아래 명시된 UI 구조와 상태 전이 방정식을 엄격히 준수하여 구현되어야 한다.)**

## 2. 공통 아키텍처 및 통신 규약 (Core Equations)
*   **[E-1] SSE 상태 동기화:** `app/page.tsx`는 `/api/mcp/events` 엔드포인트와 EventSource 객체를 생성하여 연결한다.
    *   `state` 이벤트 수신 시: `systemStatus` 객체(active_circuit, circuits, details)를 갱신.
    *   `log` 이벤트 수신 시: `logs` 배열에 항목 추가 (최대 50개 유지).
*   **[E-2] I18N 전환 로직:** KO/EN 버튼 클릭 시 `/api/mcp/update` (target: "state", data: { lang: "ko"|"en" }) 호출 후 SSE 응답으로 언어가 변경된다.

---

## 3. 상세 윈도우 컴포넌트 명세 (Window Specifications)

### [REQ-001] Unit Explorer (CoreAccess.tsx - 'Units' 탭)
**목적:** 등록된 범용 유닛 목록을 조회하고, 특정 유닛의 미션(Overview)과 행동 규약(Rules)을 편집.

*   **UI 레이아웃 (Split View):**
    *   **좌측 패널 (List):** `availableUnits` (API: `/api/mcp/protocols?type=units_list`) 배열을 매핑하여 유닛 목록 버튼 렌더링. 클릭 시 해당 유닛이 `selectedUnit`으로 설정됨.
    *   **우측 패널 (Detail & Editor):** `selectedUnit`의 상세 정보(`OVERVIEW`, `RULES`) 표시. (API: `/api/mcp/protocols?type=unit&name={unitName}`)
*   **상태 전이 및 동작 (Behaviors):**
    *   **Overview 편집:** `textarea` 클릭 후 내용 수정. `onBlur` 이벤트 발생 시 `handleSaveUnitOverview` 발동하여 자동 저장 (target: "unit_protocols").
    *   **Rules 목록 및 편집:** `RULES` 배열을 매핑하여 렌더링. 특정 Rule 클릭 시 해당 항목이 `textarea`로 전환되며 `Cancel` 및 `Update` 버튼 활성화.
    *   **Rule 추가:** 헤더 영역의 `+ Add Rule` 버튼 클릭 시 `selectedUnitData.RULES` 배열 끝에 임시 텍스트 추가 후 에디터 모드로 진입.
    *   **Update 기능:** `Update` 버튼 클릭 시 수정된 룰셋 배열을 `/api/mcp/update` (target: "unit_protocols")로 전송하고 버튼 상태를 `isSaving`("...")으로 변경.

### [REQ-002] Protocol Directives (UnitProtocols.tsx - 'Protocols' 탭)
**목적:** 현재 활성화된 회선(Active Circuit) 전용의 Global Directives 편집.

*   **UI 레이아웃 (Split View):**
    *   **좌측 패널 (Navigation):** `systemStatus.details.protocols` 배열 매핑. 인덱스 번호(01, 02...)와 규약 일부 텍스트 노출. 클릭 시 `selectedRuleIndex` 설정.
    *   **우측 패널 (Editor Area):** 
        *   선택된 인덱스가 없을 경우: "Select a Directive" 안내 아이콘(account_tree) 표시.
        *   선택된 경우: 거대한 `textarea` 노출, 상단 우측에 `Update Directive` 저장 버튼(publish 아이콘) 배치.
*   **상태 전이 및 동작 (Behaviors):**
    *   저장 버튼 클릭 시 `/api/mcp/update` (target: "circuit_protocols") 호출. 해당 배열 인덱스 내용 치환 후 전송.

### [REQ-003] Mission & Objectives (MissionSpecs.tsx - 'Overview' 탭)
**목적:** 활성화된 회선의 핵심 목표(Objective)와 달성 조건(Criteria) 가시화 및 수정.

*   **UI 레이아웃 (Card View):**
    *   **상단 헤더:** 미션 정보 요약 및 `Modify Mission` / `Save Changes` 토글 버튼.
    *   **본문 4개 섹션:** 
        1. Primary Objective (H4 타이틀)
        2. Success Criteria (체크박스형 리스트)
        3. Architect's Summary (기타 설명)
        4. Technology Dependencies (배속된 유닛 배지 목록)
*   **상태 전이 및 동작 (Behaviors):**
    *   **Edit 모드 전환:** `Modify Mission` 클릭 시 Objective는 `input`으로, Summary는 `textarea`로, Criteria는 삭제(delete 아이콘)가 가능한 `input` 리스트로 변경. `+ Add Criterion` 버튼 등장.
    *   **AC 매핑 (Check Logic):** Criteria 텍스트 내에 "완료", "확인", "배치" 등의 키워드가 포함되어 있으면 UI 상에서 자동으로 초록색 체크(`check_circle`) 처리.

### [REQ-004] Circuit Orchestration (`app/page.tsx` - 'Circuits' 탭)
**목적:** 전체 회선 목록을 그리드로 보고, 새 회선 생성 및 세부 정보로 진입.

*   **UI 레이아웃 및 상태 전이:**
    *   **Grid View (`!selectedCircuit`):** `systemStatus.circuits` 배열을 카드로 렌더링. 활성 회선 카드는 초록색 외곽선(Active 뱃지).
    *   **회선 설정 수정:** 각 카드의 우측 상단 `edit` 아이콘(hover 시 등장) 클릭 시 화면 중앙에 `Configure Circuit` 모달(Dimmed 배경) 팝업. 모달에서 설명, Objective, Criteria 수정 가능.
    *   **새 회선 생성:** `Create New Circuit` 버튼 클릭 -> JS `prompt` 호출 -> `/api/mcp/update` (target: "circuit_overview") 전송하여 신규 생성.
    *   **상세 진입 (`selectedCircuit`):** 카드의 본체 클릭 시 화면이 전환되며 해당 회선의 세부 정보(Global Protocols 폴딩 영역, 특정 규약 편집 영역, 소속 유닛 목록) 렌더링. 상단 `arrow_back` 버튼으로 그리드 복귀.

## 4. 인수 조건 및 제약 (Fences & Walls)
*   **[F-1] No Assumption:** 위 명세에 기술되지 않은 버튼, 입력창, 애니메이션 효과를 AI가 임의로 유추하여 추가하는 것을 절대 금지한다.
*   **[F-2] State Mapping:** 모든 수정(Edit) 상태는 별도의 Local State(예: `isEditing`, `editedRuleText`, `selectedRuleIndex`)로 관리되어야 하며, 저장 성공 응답을 받기 전까지 전역 상태를 오염시켜서는 안 된다.
*   **[F-3] API Contract:** 모든 수정 저장 행위는 반드시 `POST /api/mcp/update` 엔드포인트를 사용하며, payload는 `target`, `name`, `data` 구조를 엄격히 지켜야 한다.
