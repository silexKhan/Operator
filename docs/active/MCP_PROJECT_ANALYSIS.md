# MCP Project Analysis

분석일: 2026-04-28
분석 범위: `/Users/silex/workspace/private/MCP`

## 1. 범위와 제외 항목

이번 분석은 MCP 프로젝트 디렉터리만 대상으로 했다. `.venv`, `.git`, `hovercraft/node_modules`, `hovercraft/.next`, `logs`, `__pycache__` 같은 생성물과 런타임 산출물은 구조 분석에서 제외했다.

제외 후 확인된 파일 규모는 약 221개이며, 주요 구성은 Python 60개, JSON 59개, Markdown 42개, TypeScript 21개, TSX 12개다. 핵심 소스는 `mcp_operator` 88개 파일, `hovercraft` 63개 파일로 나뉜다.

## 2. 한 줄 요약

이 프로젝트는 AI 클라이언트가 사용할 MCP 도구 서버와, 회선(Circuit) 및 유닛(Unit) 규약을 파일 시스템 기반으로 관리하는 Operator 엔진, 그리고 이를 시각화/편집하는 Next.js 관리 UI(Hovercraft)를 함께 포함한 거버넌스 프레임워크다.

## 3. 최상위 구조

```text
MCP/
├── mcp_operator/              # Python MCP 서버와 회선/유닛 레지스트리
├── hovercraft/                # Next.js 관리 UI와 파일 기반 API 라우트
├── data/                      # 백엔드 엔진 상태와 미션 데이터
├── docs/                      # 개념/설계/활성 작업 문서
├── scripts/                   # CLI와 검증 보조 스크립트
├── tests/                     # unittest 기반 I18N 테스트
├── mission.json               # 루트 글로벌 미션
├── i18n_parser.py             # Pydantic 기반 ko/en 파서
└── requirements.txt           # Python 런타임 의존성
```

## 4. 백엔드 엔진 구조

### 4.1 MCP 서버

진입점은 `mcp_operator/main.py`다. stdout을 MCP stdio 통신 채널로 보존하기 위해 전역 `print`를 stderr로 보내고, `OperatorServer`를 실행한다.

실제 MCP 서버는 `mcp_operator/engine/server.py`의 `OperatorServer`가 담당한다. 현재 노출되는 도구는 다음 9개다.

- `operator_connect`
- `operator_get_status`
- `operator_set_circuit`
- `operator_reload`
- `operator_get`
- `operator_update`
- `operator_create`
- `operator_execute`
- `operator_execute_mission`

서버는 도구 호출을 `_tool_map`으로 고정하고, 비즈니스 로직은 `CoreActions`에 위임한다. `operator_connect`는 회선 전환, 전체 리포트 로드, 상태 메시지 반환을 한 번에 수행하는 AI 전용 연결 동작이다.

### 4.2 CoreActions

`mcp_operator/engine/actions.py`는 통합 API의 중심이다.

- `get_handler`: 상태, 회선/유닛 개요, 규약, 미션, state, blueprint 조회
- `update_handler`: 미션, state, global protocol 등 일부 JSON 업데이트
- `create_handler`: circuit/unit 생성
- `execute_handler`: audit, mission, reload 신호 처리
- `audit_rules`: 활성 회선에 배속된 유닛 auditor를 순회 실행

응답은 `mcp_operator/common/models.py`의 `TextResponse`, `JsonResponse`로 MCP `TextContent` 리스트 형태로 통일한다.

### 4.3 회선 관리자

`mcp_operator/registry/circuits/manager.py`의 `CircuitManager`는 `mcp_operator/registry/circuits/registry` 아래를 스캔해서 회선을 등록한다.

- `actions.py`가 있으면 커스텀 `BaseCircuit` 하위 클래스를 로드한다.
- `overview.json` 또는 `protocols.json`만 있으면 기본 `BaseCircuit` 인스턴스를 만든다.
- 활성 회선은 `data/state.json`의 `active_circuit_override`로 유지된다.

현재 확인된 회선은 `research`, `mcp`, `gdr`, `golfzon5path`다.

### 4.4 유닛과 감사기

유닛은 `mcp_operator/registry/units` 아래에 있다.

- `python`: AST 기반 타입 힌트, docstring, 아키텍처 키워드 검사
- `markdown`: PRD 필수 섹션, 용어, 생략 표현 검사
- `sentinel`: 미션 기반 7단계 문서/테스트/감사 파이프라인 검사
- `swift`: Swift MVVM/Input/Output/createInput, 강제 언래핑, weak self 검사
- `planning`: User Workflow, TOC, 상세 헤더 정합성 검사

`CoreActions._get_unit_auditor()`는 `<UnitName>Auditor` 클래스를 동적으로 import하고 `logger`, `circuit_manager` 키워드 인자로 생성한다. 이 규약에 맞는 생성자를 가진 유닛은 정상 로드되고, 맞지 않으면 조용히 기본 `BaseUnit`으로 폴백한다.

## 5. Hovercraft UI 구조

`hovercraft`는 Next.js 16.2.1, React 19.2.4, TypeScript, Tailwind 4 기반이다. `npm run dev` 실행 전 `scripts/setup.js`가 `hovercraft/data/state.json`을 초기화한다.

주요 UI 진입점은 `hovercraft/app/page.tsx`다. 화면은 Overview, Protocols, Units, Circuits, Monitor 탭 중심으로 구성되어 있고, 주요 창 컴포넌트는 `hovercraft/src/components/windows` 아래에 있다.

주요 API 라우트는 다음 역할을 한다.

- `/api/mcp/state`: `hovercraft/data/state.json`과 활성 회선의 overview/protocols 로드
- `/api/mcp/events`: `state.json` 변경 감시 및 로그 SSE 스트리밍
- `/api/mcp/protocols`: 회선/유닛/글로벌 규약 조회
- `/api/mcp/update`: state, overview, protocols, unit protocols, global protocols 파일 직접 수정
- `/api/mcp/create`, `/api/mcp/delete`: 회선 디렉터리 생성/삭제
- `/api/mcp/units/*`: 유닛 조회/생성/삭제/감사 관련 라우트

Hovercraft API 대부분은 MCP 도구 호출이 아니라 `fs`로 JSON 파일을 직접 읽고 쓰는 방식이다. 따라서 UI와 백엔드 엔진이 같은 상태 파일을 보고 있는지 정합성이 중요하다.

## 6. 데이터와 상태 흐름

백엔드 기준 상태 파일은 `data/state.json`이며 현재 형태는 다음과 같다.

```json
{
  "active_circuit_override": "mcp",
  "current_path": ""
}
```

Hovercraft 기준 상태 파일은 `hovercraft/data/state.json`이며 현재 형태는 다음과 같다.

```json
{
  "active_circuit": "golfzon5path",
  "circuits": ["research", "mcp", "gdr", "golfzon5path"],
  "lang": "en"
}
```

즉, 백엔드 MCP 서버의 활성 회선은 `mcp`이고 UI가 보는 활성 회선은 `golfzon5path`다. 이 상태 이원화는 현재 프로젝트에서 가장 먼저 정리해야 할 정합성 리스크다.

미션도 루트 `mission.json`과 `data/mission.json`이 함께 존재한다. `CoreActions.get_mission_logic()`은 루트 `mission.json`을 읽지만, Hovercraft의 일부 fallback은 `data/mission.json`을 참조한다.

## 7. 확인된 회선

| 회선 | 역할 | 주요 유닛 |
| --- | --- | --- |
| `mcp` | Operator 시스템 자체 관리 | `python`, `markdown`, `sentinel`, `planning` |
| `research` | 불확실한 주제 탐구와 분석 | `markdown`, `sentinel` |
| `gdr` | Golfzon GDR 앱 분석/관리 | `markdown`, `sentinel`, `swift` |
| `golfzon5path` | Golfzon5 경로용 회선 | `markdown`, `sentinel`, `planning` |

주의: `mcp_operator/registry/circuits/registry/mcp/actions.py`의 런타임 유닛 목록은 `["planning", "design", "dev", "sentinel", "python"]`이고, `mcp/overview.json`의 유닛 목록은 `["python", "markdown", "sentinel", "planning"]`이다. 물리 유닛 `design`, `dev`는 존재하지 않는다. 감사 로직은 런타임 `actions.py`의 `self.units`를 사용하므로 문서/JSON과 실제 감사 대상이 다를 수 있다.

## 8. 검증 결과

실행한 검증:

```bash
python3 -m unittest tests/test_i18n_parser.py
```

결과: 3개 테스트 통과.

```bash
npm run lint
```

결과: 실패. 총 28개 문제(14 errors, 14 warnings)가 보고되었다. 주요 유형은 `no-explicit-any`, 미사용 변수, React hook dependency, `setState` in effect, `@ts-ignore` 사용이다.

## 9. 주요 리스크와 정리 필요 항목

1. 백엔드 상태와 UI 상태가 분리되어 있다.
   - 백엔드: `data/state.json`
   - UI: `hovercraft/data/state.json`
   - 현재 활성 회선 값도 서로 다르다.

2. Hovercraft의 MCP 클라이언트 경로가 일부 깨져 있다.
   - `hovercraft/app/api/mcp/route.ts`와 `browser/route.ts`는 `McpClient`를 named import하지만, `hovercraft/src/lib/mcpClient.ts`는 `McpClient` 클래스를 export하지 않는다.
   - 같은 라우트들이 `callTools()`를 호출하지만 실제 구현은 `callTool()`만 있다.
   - `mcpClient.callTool()`은 `/api/mcp/execute`를 호출하지만 해당 route 파일은 없다.

3. 도구 이름이 1.x/2.0 사이에서 혼재되어 있다.
   - 서버 노출 도구는 `operator_*` 형식이다.
   - `mcp_operator/tests/verify_mcp.py`는 `get_operator_status`, `mcp_operator_get`, `mcp_operator_update`, `reload_operator` 같은 과거 이름을 호출한다.
   - Hovercraft 일부 라우트도 `mcp_operator_mcp_operator_get`, `mcp_operator_browse_directory` 같은 현재 서버에 없는 이름을 사용한다.

4. Auditor 생성자 규약이 맞지 않는 유닛이 있다.
   - `CoreActions`는 `auditor_cls(logger=..., circuit_manager=...)`로 생성한다.
   - `SwiftAuditor`와 `PlanningAuditor`는 `circuit_manager` 키워드를 받지 않아 커스텀 auditor 로드가 실패하고 기본 `BaseUnit`으로 폴백될 가능성이 높다.

5. 로그 파일 경로가 통일되어 있지 않다.
   - `OperatorLogger`는 `logs/server.log`에 기록한다.
   - `OperatorServer.broadcast_message()`는 `logs/mcp_live.log`를 쓴다.
   - Hovercraft SSE는 `logs/mcp_server.log`를 읽는다.
   - 기본 실행 로그가 UI Monitor로 보이지 않을 수 있다.

6. 문서화된 UI 원칙과 실제 UI 코드가 일부 충돌한다.
   - `HOVERCRAFT_ARCHITECT.md`는 브라우저 네이티브 `alert` 사용을 금지하지만, `hovercraft/app/page.tsx`에는 실패 처리에 `alert()`가 남아 있다.

7. `hovercraft/start.sh`는 `git config --global`을 수정한다.
   - 프로젝트 기동 스크립트가 사용자 전역 Git 설정을 바꾸므로, 실행 전 명시적 동의가 필요한 성격의 부작용이다.

## 10. 권장 정리 순서

1. 상태 저장소를 하나로 정한다.
   - 권장: 백엔드의 `data/state.json`을 단일 source of truth로 삼고 Hovercraft는 이를 읽게 한다.

2. MCP 2.0 도구 이름을 기준으로 UI/테스트를 갱신한다.
   - `operator_*` 도구명 기준으로 `verify_mcp.py`, Hovercraft 브릿지, API route를 정리한다.

3. Hovercraft API의 dead path를 제거하거나 구현한다.
   - `/api/mcp/execute` route 생성 또는 `mcpClient.callTool()` 제거/수정
   - `McpClient` export와 `callTools()` 구현 여부 결정

4. Auditor 생성자 인터페이스를 통일한다.
   - 모든 auditor가 `logger=None, circuit_manager=None`를 받도록 맞추는 편이 가장 작다.

5. 회선 유닛 정의를 `overview.json`과 `actions.py` 중 하나로 일원화한다.
   - 현재처럼 둘 다 있으면 UI와 감사 실행 결과가 달라진다.

6. 로그 파일명을 통합한다.
   - `logs/server.log`, `logs/mcp_live.log`, `logs/mcp_server.log` 중 하나를 표준으로 정하고 생산자/소비자를 맞춘다.

7. lint를 먼저 0 error로 낮춘다.
   - 현재 TypeScript strict 설정과 lint 규칙이 코드 상태를 제대로 막고 있으므로, UI 안정화의 첫 관문으로 적합하다.

## 11. 현재 결론

MCP Operator의 핵심 개념과 백엔드 구조는 비교적 명확하다. `OperatorServer -> CoreActions -> CircuitManager -> Circuit/Unit Auditor` 흐름은 유지 가능한 형태다. 다만 Hovercraft와 테스트 쪽에는 MCP 1.x 시절 명명과 2.0 통합 API가 섞여 있고, 상태 파일도 백엔드/UI가 분리되어 있어 실제 운영 시 표시 상태와 서버 상태가 어긋날 수 있다.

따라서 다음 작업은 기능 추가보다 정합성 복구가 우선이다. 특히 상태 단일화, 도구명 통일, auditor 생성자 통일, Hovercraft lint/type 오류 해소를 먼저 처리해야 이 프로젝트가 안정적인 MCP 관리 도구로 동작한다.
