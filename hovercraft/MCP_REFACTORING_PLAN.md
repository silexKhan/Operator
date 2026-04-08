# Hovercraft MCP 통합 API 개편 리팩토링 계획

## 1. 개요
MCP Operator 2.0 엔진의 지휘 규약 개편으로 인해 파편화되어 있던 도구(Tool) 호출 인터페이스가 `get`, `update`, `create`, `execute` 4개의 코어 액션으로 통합되었습니다. 이에 따라 Hovercraft 프론트엔드 코드 내에 하드코딩된 레거시 도구 호출 부분을 새로운 통합 API 방식에 맞게 일괄 변경해야 합니다.

## 2. 매핑 테이블 (구현 명세)

| 위치 | 기존 도구 호출 | 신규 통합 도구 호출 |
|---|---|---|
| `app/api/mcp/protocols/route.ts` | `name: "mcp_operator_get_circuit_protocols"`, `args: { circuit_name }` | `name: "mcp_operator_mcp_operator_get"`, `args: { target: "protocol", name: circuit_name }` |
| `app/api/mcp/protocols/route.ts` | `name: "mcp_operator_get_global_protocols"`, `args: {}` | `name: "mcp_operator_mcp_operator_get"`, `args: { target: "protocol" }` |
| `app/api/mcp/update/route.ts` | `name: "mcp_operator_update_circuit_overview"`, `args: { circuit_name, description, units }` | `name: "mcp_operator_mcp_operator_update"`, `args: { target: "overview", name: circuit_name, data: { description, units } }` |
| `app/api/mcp/update/route.ts` | `name: "mcp_operator_update_circuit_protocols"`, `args: { circuit_name, rules }` | `name: "mcp_operator_mcp_operator_update"`, `args: { target: "protocol", name: circuit_name, data: { rules } }` |
| `app/api/mcp/update/route.ts` | `name: "mcp_operator_reload_operator"`, `args: {}` | `name: "mcp_operator_mcp_operator_execute"`, `args: { action: "reload" }` |
| `app/api/mcp/create/route.ts` | `name: "mcp_operator_create_new_circuit"`, `args: { name }` | `name: "mcp_operator_mcp_operator_create"`, `args: { target: "circuit", name }` |
| `app/api/mcp/create/route.ts` | `name: "mcp_operator_reload_operator"`, `args: {}` | `name: "mcp_operator_mcp_operator_execute"`, `args: { action: "reload" }` |
| `app/api/mcp/route.ts` | `name: "mcp_operator_get_full_json_structure"`, `args: {}` | `name: "mcp_operator_mcp_operator_get"`, `args: { target: "blueprint" }` |
| `app/page.tsx` | `action: "get_operator_status"` | `action: "mcp_operator_get"`, 데이터 포맷 `target: "status"` 포함 처리 |

* 참고: `app/api/mcp/delete/route.ts` 와 `app/api/mcp/browser/route.ts` 등에 남아있는 도구들은 새로운 통합 API에 명시적으로 추가되지 않았다면 기존(Legacy) 도구 이름을 그대로 유지하거나 삭제될 수 있습니다 (명세 확인 후 변경).

## 3. 실행 지침
- 위 테이블을 기반으로 `hovercraft/app/api/mcp/` 하위 파일들과 `app/page.tsx`를 검색 및 치환합니다.
- 특히 `update/route.ts`에서 data 패키징 부분을 주의하여 `data: { rules }` 나 `data: { description, units }` 로 잘 말아 넣어야 합니다.
