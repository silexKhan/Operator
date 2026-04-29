# MCP Improvement Design

작성일: 2026-04-28
대상 범위: `/Users/silex/workspace/private/MCP`
선행 문서: `docs/active/MCP_PROJECT_ANALYSIS.md`

## 0. 이 문서의 목적

이 문서는 MCP Operator 프로젝트를 이어받는 다른 AI 또는 개발자가 같은 판단 기준으로 개선 작업을 수행하도록 만든 실행 설계서다.

핵심 목표는 기능을 새로 늘리는 것이 아니다. 현재 프로젝트 안에 섞여 있는 MCP 1.x/2.0 명명, 백엔드/UI 상태 이원화, Hovercraft API dead path, auditor 인터페이스 불일치, 로그 경로 불일치를 정리해서 “MCP 서버와 관리 UI가 같은 시스템을 보고 같은 명령 체계를 쓰는 상태”로 되돌리는 것이다.

## 1. 작업 전제

1. 프로젝트 루트는 `/Users/silex/workspace/private/MCP`다.
2. 백엔드 MCP 서버는 Python 패키지 `mcp_operator`다.
3. 관리 UI는 `hovercraft` 하위 Next.js 앱이다.
4. 현재 MCP 서버의 공식 도구명은 `operator_*` 형식이다.
5. Hovercraft는 현재 MCP 도구 호출보다 파일 시스템 직접 읽기/쓰기에 더 의존한다.
6. 기존 파일 전체 덮어쓰기는 금지하고, 필요한 지점만 국소 수정한다.
7. 상태, 미션, 회선, 유닛, 로그 중 하나라도 이중 source of truth가 있으면 운영 오류로 본다.

## 2. 최종 목표 상태

개선 완료 후 시스템은 아래 구조로 이해되어야 한다.

```text
AI Client
  |
  | MCP stdio tool call: operator_*
  v
mcp_operator/engine/server.py
  |
  v
mcp_operator/engine/actions.py
  |
  v
CircuitManager + Registry
  |
  +-- data/state.json              # 단일 상태 저장소
  +-- mission.json                  # 단일 글로벌 미션 저장소
  +-- mcp_operator/registry/...     # 회선/유닛 정의

Hovercraft UI
  |
  v
hovercraft/app/api/*
  |
  v
shared file adapter or operator API bridge
  |
  v
same state/mission/registry/log files as backend
```

중요한 판단 기준:

- 백엔드와 UI가 서로 다른 active circuit을 보여주면 실패다.
- 서버에 없는 도구명을 테스트나 UI가 호출하면 실패다.
- auditor가 생성자 불일치 때문에 조용히 `BaseUnit`으로 폴백하면 실패다.
- UI Monitor가 실제 서버 로그를 읽지 못하면 실패다.
- `npm run lint`가 error를 내면 Hovercraft 안정화는 완료되지 않은 것이다.

## 3. 개선 축 요약

| 축 | 현재 문제 | 목표 |
| --- | --- | --- |
| State | `data/state.json`과 `hovercraft/data/state.json`이 서로 다른 상태를 가진다 | `data/state.json`을 단일 source of truth로 만든다 |
| Tool Naming | `operator_*`, `mcp_operator_*`, 과거 이름이 혼재한다 | `operator_*`만 공식 도구명으로 사용한다 |
| Hovercraft Bridge | `McpClient` export/callTools/execute route가 맞지 않는다 | UI API 호출 경로를 실제 구현과 일치시킨다 |
| Auditor | `SwiftAuditor`, `PlanningAuditor` 생성자 키워드가 코어 호출과 다르다 | 모든 auditor가 동일 생성자 계약을 따른다 |
| Circuit Units | `actions.py`와 `overview.json`의 유닛 목록이 다르다 | 하나의 정의를 기준으로 실행/표시를 일치시킨다 |
| Logs | 생산/소비 로그 파일명이 다르다 | 하나의 표준 로그 파일을 쓰고 UI도 같은 파일을 읽는다 |
| Tests/Lint | Python 일부만 통과, UI lint 실패 | Python smoke + Hovercraft lint/build까지 통과한다 |

## 4. 설계 원칙

### 4.1 Source of Truth 원칙

상태와 메타데이터는 “어디가 진짜인가”가 명확해야 한다.

권장 단일 저장소:

- 시스템 상태: `data/state.json`
- 글로벌 미션: `mission.json`
- 회선 개요: `mcp_operator/registry/circuits/registry/<circuit>/overview.json`
- 회선 규약: `mcp_operator/registry/circuits/registry/<circuit>/protocols.json`
- 유닛 규약: `mcp_operator/registry/units/<unit>/protocols.json`
- 서버 로그: `logs/server.log`

`hovercraft/data/state.json`은 제거하거나, 과도기에는 읽지 않게 만든다. 새 AI가 바로 삭제하면 UI가 깨질 수 있으므로 첫 단계에서는 “사용하지 않는 상태”로 만들고, 검증 후 삭제 여부를 결정한다.

### 4.2 Backward Compatibility 원칙

상태 스키마 변경은 한 번에 깨지게 만들지 않는다.

권장 state v2:

```json
{
  "active_circuit": "mcp",
  "current_path": "",
  "lang": "ko"
}
```

과도기 읽기 규칙:

1. `active_circuit`이 있으면 우선 사용한다.
2. 없으면 기존 `active_circuit_override`를 사용한다.
3. 둘 다 없으면 `mcp`를 기본값으로 사용한다.

과도기 쓰기 규칙:

1. 새 코드는 `active_circuit`만 쓴다.
2. `active_circuit_override`는 한 릴리스 동안 읽기 fallback으로만 둔다.
3. 모든 호출부가 바뀐 뒤 `active_circuit_override`를 제거한다.

### 4.3 Tool Contract 원칙

MCP 도구명은 서버가 노출하는 이름만 진짜다.

공식 도구 목록:

- `operator_connect`
- `operator_get_status`
- `operator_set_circuit`
- `operator_reload`
- `operator_get`
- `operator_update`
- `operator_create`
- `operator_execute`
- `operator_execute_mission`

다른 이름은 legacy로 취급한다.

legacy 예시:

- `get_operator_status`
- `set_active_circuit`
- `mcp_operator_get`
- `mcp_operator_update`
- `reload_operator`
- `mcp_operator_browse_directory`
- `mcp_operator_mcp_operator_get`

legacy 이름을 유지하려면 서버에서 명시적 alias map을 제공해야 한다. 그렇지 않으면 테스트와 UI에서 제거한다.

### 4.4 Thin UI API 원칙

Hovercraft의 API route는 복잡한 비즈니스 로직을 갖지 않는다.

권장:

- 파일 경로 계산은 `hovercraft/src/lib/operatorPaths.ts` 같은 단일 helper로 모은다.
- JSON read/write는 `hovercraft/src/lib/operatorStore.ts` 같은 단일 helper로 모은다.
- route 파일은 request 파싱, helper 호출, response 반환만 한다.

피해야 할 상태:

- route마다 `path.join(process.cwd(), "..", ...)`가 반복되는 상태
- 어떤 route는 `hovercraft/data/state.json`, 어떤 route는 `../data/state.json`을 보는 상태
- fallback으로 절대 경로 `/Users/silex/...`를 하드코딩하는 상태

## 5. 작업 패키지 설계

아래 순서대로 진행한다. 앞 단계가 끝나지 않으면 뒤 단계로 넘어가지 않는다.

## Phase 1. 상태 저장소 단일화

### 목표

백엔드와 Hovercraft가 같은 active circuit, 같은 language, 같은 circuit list를 보게 만든다.

### 변경 대상

- `data/state.json`
- `mcp_operator/registry/circuits/manager.py`
- `hovercraft/app/api/mcp/state/route.ts`
- `hovercraft/app/api/mcp/events/route.ts`
- `hovercraft/app/api/mcp/update/route.ts`
- `hovercraft/scripts/setup.js`

### 상세 지침

1. `data/state.json`을 state v2로 전환한다.

권장 결과:

```json
{
  "active_circuit": "mcp",
  "current_path": "",
  "lang": "ko"
}
```

2. `CircuitManager._load_state_handler()`는 다음 우선순위로 읽는다.

```text
state["active_circuit"] -> state["active_circuit_override"] -> None
```

3. `CircuitManager._save_state_handler()`는 `active_circuit`만 저장한다.

4. Hovercraft API는 `hovercraft/data/state.json` 대신 `../data/state.json`을 읽는다.

5. `hovercraft/scripts/setup.js`는 `hovercraft/data/state.json`을 만들지 않는다. 필요하다면 루트 `data/state.json` 존재 여부만 확인한다.

6. Hovercraft response에서 circuit list가 필요하면 state 파일에 저장하지 말고 registry 디렉터리를 스캔한다.

### 성공 기준

- `operator_get_status`의 active circuit과 `/api/mcp/state`의 active circuit이 같다.
- Hovercraft에서 회선 전환 후 `data/state.json`만 변경된다.
- `hovercraft/data/state.json`을 임시로 삭제하거나 이름 변경해도 UI state 조회가 동작한다.

## Phase 2. MCP 도구명 통일

### 목표

테스트, CLI, UI 브릿지가 현재 서버의 `operator_*` 도구명만 사용하게 만든다.

### 변경 대상

- `mcp_operator/tests/verify_mcp.py`
- `hovercraft/app/api/mcp/route.ts`
- `hovercraft/app/api/mcp/browser/route.ts`
- `hovercraft/src/lib/mcpClient.ts`
- 필요 시 `scripts/mcp_cli.py`

### 상세 지침

1. `verify_mcp.py`에서 호출명을 모두 현재 이름으로 바꾼다.

예:

```text
get_operator_status       -> operator_get_status
set_active_circuit        -> operator_set_circuit
mcp_operator_get          -> operator_get
mcp_operator_update       -> operator_update
mcp_operator_execute      -> operator_execute
reload_operator           -> operator_reload
```

2. Hovercraft가 실제 MCP 서버를 호출하지 않는다면 `McpClient.callTool()`의 `/api/mcp/execute` dead path를 제거한다.

3. Hovercraft가 실제 MCP 서버를 호출해야 한다면 `/api/mcp/execute/route.ts`를 명시적으로 만든다. 이 경우 request body는 다음 계약을 따른다.

```json
{
  "tool": "operator_get",
  "args": {
    "target": "status"
  }
}
```

4. `McpClient` 클래스를 named export할지, singleton만 export할지 결정한다.

권장:

```ts
export class McpClient {
  // ...
}

export const mcpClient = new McpClient();
```

5. `callTools()`가 필요한 route가 남아 있으면 구현한다. 필요 없으면 route를 파일 기반 helper로 바꾼다.

### 성공 기준

- `rg "mcp_operator_|get_operator_status|set_active_circuit|reload_operator" hovercraft mcp_operator scripts` 결과가 의도된 legacy 문서 외에는 없다.
- `.venv/bin/python mcp_operator/tests/verify_mcp.py`가 현재 도구명 기준으로 통과한다.

## Phase 3. Hovercraft 파일 접근 계층 정리

### 목표

Hovercraft API route마다 흩어진 `fs`/`path` 로직을 단일 helper로 모아 경로 오류를 막는다.

### 신규 파일 제안

- `hovercraft/src/lib/operatorPaths.ts`
- `hovercraft/src/lib/operatorStore.ts`

### `operatorPaths.ts` 책임

```ts
export function getMcpRoot(): string;
export function getStatePath(): string;
export function getMissionPath(): string;
export function getLogsPath(): string;
export function getCircuitsRegistryPath(): string;
export function getCircuitPath(name: string): string;
export function getUnitsRegistryPath(): string;
export function getUnitPath(name: string): string;
export function assertSafeName(name: string): string;
```

`assertSafeName()`은 path traversal을 막는다.

허용:

```text
letters, numbers, dash, underscore
```

금지:

```text
../
/
\
empty string
```

### `operatorStore.ts` 책임

```ts
export function readJsonFile<T>(filePath: string, fallback: T): T;
export function writeJsonFile<T>(filePath: string, data: T): void;
export function listCircuitNames(): string[];
export function listUnitNames(): string[];
export function readSystemState(): SystemState;
export function writeSystemState(next: Partial<SystemState>): SystemState;
export function readCircuitDetails(name: string): CircuitDetails;
```

### route별 목표 형태

`hovercraft/app/api/mcp/state/route.ts`

- `readSystemState()`
- `listCircuitNames()`
- active circuit details 추가
- response 반환

`hovercraft/app/api/mcp/protocols/route.ts`

- `units_list`, `circuits_list`, `unit`, `circuit_full`, `global` 분기만 유지
- 모든 경로는 helper 사용

`hovercraft/app/api/mcp/update/route.ts`

- state, overview, protocol, unit_protocols, global_protocols 업데이트만 담당
- 직접 `path.join()` 반복 제거

### 성공 기준

- `rg "process.cwd\\(\\).*\\.\\." hovercraft/app/api hovercraft/src/lib` 결과가 `operatorPaths.ts` 외에는 없다.
- `rg "/Users/silex" hovercraft` 결과가 없다.

## Phase 4. Auditor 인터페이스 통일

### 목표

모든 auditor가 CoreActions에서 같은 방식으로 생성되고, 조용한 폴백 없이 실제 감사 로직이 실행되게 한다.

### 변경 대상

- `mcp_operator/registry/units/swift/auditor.py`
- `mcp_operator/registry/units/planning/auditor.py`
- `mcp_operator/engine/actions.py`
- 관련 테스트 또는 새 smoke test

### 상세 지침

모든 auditor 생성자는 다음 형태를 지원해야 한다.

```py
def __init__(self, logger=None, circuit_manager=None):
    self.logger = logger
    self.circuit_manager = circuit_manager
```

현재 `SwiftAuditor`와 `PlanningAuditor`는 `manager` 이름을 사용하므로 `circuit_manager`를 받게 수정한다. 기존 호출 호환이 필요하면 `manager=None`도 optional로 둔다.

권장:

```py
def __init__(self, logger=None, circuit_manager=None, manager=None):
    self.logger = logger
    self.circuit_manager = circuit_manager or manager
```

`CoreActions._get_unit_auditor()`의 bare `except: pass`는 최소한 logger에 실패 원인을 남긴다.

권장:

```py
except Exception as e:
    if self.logger:
        self.logger.log(f"Auditor load failed ({unit_name}): {str(e)}", 1)
```

### 성공 기준

- `operator_execute` with `{"action": "audit", "params": {"file_path": "<swift file>"}}`가 SwiftAuditor 결과를 낸다.
- `operator_execute` with markdown file path가 Planning/MarkdownAuditor 결과를 낸다.
- auditor import 실패가 로그에 남는다.

## Phase 5. 회선 유닛 정의 일원화

### 목표

UI에 표시되는 유닛과 실제 감사에 쓰이는 유닛이 같게 만든다.

### 현재 충돌

`mcp_operator/registry/circuits/registry/mcp/actions.py`

```py
self.units = ["planning", "design", "dev", "sentinel", "python"]
```

`mcp_operator/registry/circuits/registry/mcp/overview.json`

```json
["python", "markdown", "sentinel", "planning"]
```

실제 물리 유닛에는 `design`, `dev`가 없다.

### 권장 설계

1. `overview.json`의 `units`를 표준 source of truth로 둔다.
2. `BaseCircuit.get_units()`가 가능하면 `overview.json`에서 `units`를 읽게 한다.
3. 커스텀 `actions.py`의 `self.units`는 fallback 또는 특수 override로만 사용한다.
4. 존재하지 않는 유닛은 CircuitManager 또는 audit 단계에서 warning을 낸다.

### 대안

커스텀 `actions.py`를 source of truth로 유지할 수도 있다. 이 경우 Hovercraft의 circuit details도 Python 클래스를 통해 읽어야 하므로 구현 난도가 올라간다. 현재 프로젝트는 JSON 중심 UI이므로 `overview.json` 기준이 더 실용적이다.

### 성공 기준

- `/api/mcp/protocols?type=circuit_full&name=mcp`의 units와 `operator_execute` audit 대상 units가 같다.
- 존재하지 않는 `design`, `dev` 유닛은 더 이상 감사 대상에 들어가지 않는다.

## Phase 6. 로그 경로 통합

### 목표

서버가 쓰는 로그와 UI SSE가 읽는 로그를 일치시킨다.

### 표준 로그 파일

```text
logs/server.log
```

### 변경 대상

- `mcp_operator/engine/logger.py`
- `mcp_operator/engine/server.py`
- `hovercraft/app/api/mcp/events/route.ts`
- `hovercraft/app/api/mcp/logs/route.ts`
- `hovercraft/package.json`

### 상세 지침

1. `OperatorLogger`는 이미 `logs/server.log`에 기록한다. 이것을 표준으로 유지한다.
2. `OperatorServer.broadcast_message()`의 `logs/mcp_live.log` 기록은 유지할 이유가 있으면 별도 event log로 문서화하고, 아니면 `logs/server.log`로 통합한다.
3. Hovercraft SSE의 `LOG_FILE`을 `../logs/server.log`로 바꾼다.
4. `npm run dev`가 쓰는 `../logs/ui.log`는 UI dev server 로그로 유지해도 된다. 단, Monitor에서 서버 로그로 혼동하지 않게 한다.

### 성공 기준

- 서버 시작 후 `logs/server.log`에 기록된다.
- Hovercraft Monitor 또는 SSE log event가 같은 파일의 신규 라인을 보여준다.
- `rg "mcp_server.log|mcp_live.log" .` 결과가 문서 또는 의도된 별도 event log 외에는 없다.

## Phase 7. Hovercraft lint/type 안정화

### 목표

`npm run lint`를 error 0개로 만든다.

### 현재 실패 유형

- `@typescript-eslint/no-explicit-any`
- unused vars
- React hook dependency
- `react-hooks/set-state-in-effect`
- `@ts-ignore` 대신 `@ts-expect-error` 필요

### 상세 지침

1. 공통 타입을 `hovercraft/src/types/mcp.ts`에 확장한다.

필요 타입 예:

```ts
export type I18nText = string | { ko?: string; en?: string; [key: string]: string | undefined };

export interface SystemState {
  active_circuit: string;
  current_path?: string;
  lang?: "ko" | "en";
}

export interface CircuitOverview {
  name: string;
  description?: I18nText;
  dependencies?: string[];
  units?: string[];
  mission?: Mission;
}

export interface ProtocolFile {
  RULES?: string[];
  rules?: string[];
  protocols?: string[];
}
```

2. route에서 `any` 대신 `unknown` + 타입 가드 또는 위 타입을 사용한다.

3. 실제로 사용하지 않는 상태는 제거한다. 단, UI 기능 예정 상태라면 TODO 주석 대신 실제 연결까지 구현한다.

4. `CircuitDetailView`의 effect 내부 동기 setState는 파생 상태를 줄이는 방향으로 정리한다.

권장:

- modal open 시점의 handler에서 edit state 초기화
- render 중 `getI18nText()` 파생값 사용
- `useMemo`로 derived value 계산

5. `next.config.ts`는 `@ts-ignore`를 `@ts-expect-error`로 바꾸거나, 타입 확장으로 제거한다.

### 성공 기준

```bash
cd hovercraft
npm run lint
```

위 명령이 exit code 0으로 끝난다.

## Phase 8. 테스트 체계 복구

### 목표

“무엇을 실행하면 MCP가 정상인지”를 명확히 한다.

### 권장 검증 명령

루트:

```bash
python3 -m unittest tests/test_i18n_parser.py
.venv/bin/python mcp_operator/tests/verify_mcp.py
```

Hovercraft:

```bash
cd hovercraft
npm run lint
npm run build
```

### 테스트 정리 지침

1. `test_ws.py`는 현재 `ws://localhost:3001`을 기대한다. 실제 서버가 stdio MCP라면 이 테스트는 archive하거나 별도 websocket 서버 테스트로 분리한다.
2. `test_audit.py`는 의도적으로 나쁜 코드 샘플이다. 자동 테스트로 돌릴 목적이면 expected failure를 명시한다.
3. `verify_mcp.py`는 현재 도구명으로 업데이트하고 smoke test의 기준으로 삼는다.
4. 테스트가 상태 파일을 바꾸면 원복 로직을 넣는다.

### 성공 기준

- 자동 검증용 명령과 수동 데모용 스크립트가 문서상 분리된다.
- smoke test가 legacy 도구명을 호출하지 않는다.

## 6. 구현 시 주의할 파일별 메모

### `mcp_operator/engine/server.py`

- 공식 도구 목록이 정의된 곳이다.
- 도구명을 바꿀 때는 `_refresh_tool_cache_handler()`와 `_get_unified_tool_list()`를 같이 바꿔야 한다.
- stdout 오염은 MCP 통신 장애로 이어지므로 print/log는 stderr 또는 file logger를 사용한다.

### `mcp_operator/engine/actions.py`

- 통합 비즈니스 로직의 중심이다.
- `_get_unit_auditor()`의 실패 삼킴은 디버깅 비용을 키운다. 최소 로그를 남긴다.
- `get_handler(target="all")`은 AI 연결 시 큰 맥락을 주는 핵심 응답이므로 응답 schema를 안정적으로 유지한다.

### `mcp_operator/registry/circuits/manager.py`

- 회선 discovery와 active circuit persistence를 담당한다.
- 상태 schema 변경 시 이 파일이 1순위 변경 대상이다.
- default component lambda capture는 추후 주의가 필요하다. 반복문 변수 `name`, `dirpath`를 lambda가 늦게 참조할 수 있으므로 default arg capture를 쓰는 편이 안전하다.

권장:

```py
instance.get_name = lambda name=name: name
instance.get_path = lambda dirpath=dirpath: dirpath
```

### `hovercraft/app/api/*`

- 현재 파일 접근 로직이 route마다 흩어져 있다.
- 보안상 name/path 입력은 반드시 safe name 검증 후 사용한다.
- route에서 절대 경로를 하드코딩하지 않는다.

### `hovercraft/src/lib/mcpClient.ts`

- 현재 `class McpClient`가 named export되지 않는다.
- `/api/mcp/execute` route가 없는데 `callTool()`은 그 경로를 호출한다.
- 먼저 이 파일의 책임을 결정해야 한다.

권장 책임:

- UI 컴포넌트가 Hovercraft API를 편하게 호출하는 browser client
- 실제 MCP stdio server 직접 호출은 하지 않는다

### `hovercraft/app/page.tsx`

- 상태와 handler가 많이 모여 있다.
- lint 정리 시 unused state를 제거하거나 하위 컴포넌트로 책임을 내려야 한다.
- `alert()`는 `HOVERCRAFT_ARCHITECT.md`의 금지 규약과 충돌한다. 내부 modal/toast 컴포넌트로 대체한다.

## 7. 다른 AI를 위한 실행 체크리스트

작업 시작 전에 반드시 확인:

- [ ] 현재 작업 디렉터리가 `/Users/silex/workspace/private/MCP`인지 확인한다.
- [ ] `git status --short`로 기존 사용자 변경을 확인한다.
- [ ] `docs/active/MCP_PROJECT_ANALYSIS.md`와 이 문서를 읽는다.
- [ ] 기존 modified 파일을 임의로 되돌리지 않는다.

Phase별 완료 체크:

- [ ] Phase 1: 백엔드/UI state가 `data/state.json` 하나로 통합됨
- [ ] Phase 2: legacy MCP 도구명 호출 제거
- [ ] Phase 3: Hovercraft path/store helper 도입
- [ ] Phase 4: 모든 auditor 생성자 계약 통일
- [ ] Phase 5: circuit units source of truth 통일
- [ ] Phase 6: 서버 로그와 UI SSE 로그 경로 통일
- [ ] Phase 7: `npm run lint` error 0
- [ ] Phase 8: smoke test 명령 정리 및 통과

최종 검증:

```bash
python3 -m unittest tests/test_i18n_parser.py
.venv/bin/python mcp_operator/tests/verify_mcp.py
cd hovercraft
npm run lint
npm run build
```

## 8. 작업 분할 제안

작업을 한 번에 모두 처리하지 말고 아래 순서로 PR 또는 커밋을 나누는 것이 안전하다.

1. `state-unification`
   - `data/state.json`
   - `CircuitManager`
   - Hovercraft state/events/update route

2. `tool-contract-cleanup`
   - `verify_mcp.py`
   - `mcpClient.ts`
   - dead route 정리 또는 execute route 구현

3. `hovercraft-store-layer`
   - `operatorPaths.ts`
   - `operatorStore.ts`
   - protocols/create/delete/update route 단순화

4. `auditor-contract`
   - Swift/Planning auditor 생성자 수정
   - auditor load 실패 로깅
   - audit smoke test 추가

5. `logs-and-monitor`
   - log file 표준화
   - SSE log route 정리

6. `lint-hardening`
   - TypeScript 타입 추가
   - `any` 제거
   - unused state 제거
   - React hook lint 해결

## 9. 비목표

이번 정리에서 하지 않는 일:

- 새 UI 디자인 전면 개편
- 새 회선/유닛 기능 추가
- MCP 프로토콜 자체 확장
- AI 프롬프트 페르소나 재작성
- 대규모 디렉터리 이동
- `requirements.txt` 의존성 정리
- `package.json` major dependency upgrade

비목표를 지키는 이유는 현재 리스크가 기능 부족이 아니라 정합성 붕괴에 가깝기 때문이다. 먼저 같은 상태, 같은 도구명, 같은 로그, 같은 유닛 정의를 보게 만든 뒤 기능을 추가해야 한다.

## 10. 완료 정의

개선 작업은 아래 조건을 모두 만족할 때 완료로 본다.

1. `operator_connect(name="mcp")` 후 `operator_get_status`와 Hovercraft `/api/mcp/state`가 같은 active circuit을 반환한다.
2. `rg "mcp_operator_|get_operator_status|set_active_circuit|reload_operator" hovercraft mcp_operator scripts` 결과에 실행 코드의 legacy 호출이 없다.
3. `SwiftAuditor`, `PlanningAuditor`, `PythonAuditor`, `MarkdownAuditor`, `SentinelAuditor`가 모두 `CoreActions._get_unit_auditor()`로 생성 가능하다.
4. `mcp` 회선의 표시 유닛과 감사 유닛이 같다.
5. 서버 로그 신규 라인이 Hovercraft SSE log event로 전달된다.
6. `python3 -m unittest tests/test_i18n_parser.py`가 통과한다.
7. `.venv/bin/python mcp_operator/tests/verify_mcp.py`가 통과한다.
8. `cd hovercraft && npm run lint`가 통과한다.
9. `cd hovercraft && npm run build`가 통과한다.

## 11. 우선순위 결론

가장 먼저 해야 할 일은 상태 저장소 단일화다. 그 다음 MCP 도구명 통일, Hovercraft bridge 정리, auditor 생성자 통일 순서로 진행한다. 이 네 가지가 끝나면 시스템은 같은 회선을 보고 같은 도구 계약으로 동작하게 된다. 그 이후에 로그/모니터와 lint/type 안정화를 처리하면 운영 가능한 기반이 된다.
