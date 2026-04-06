# 🌐 MCP_ARCHITECT: The Nexus Controller

## 🧩 The Equation (시스템 방정식)
**Σ(Tool Request) + Enum(OperatorTool) ➔ [McpCircuit: Router] ➔ (Internal Handler | Core Bridge) = Output(Response)**

- 모든 도구 요청은 `OperatorTool` 열거형을 통해 정적 무결성을 검증받는다.
- `McpCircuit`은 지능이 없는 'Dumb Controller'로서, 로직을 직접 수행하지 않고 핸들러나 브릿지로 위임한다.

## 🛡️ TDD Fence (TDD 울타리)
1. **[P-1] Dumb Controller:** 컨트롤러 내에 비즈니스 로직을 직접 구현하지 마십시오.
2. **[P-2] Schema Integrity:** 모든 도구 명세(`get_tools`)에는 `properties`가 반드시 명시되어야 합니다.
3. **[P-6] Enum Management:** 가용 도구는 반드시 `OperatorTool` Enum에 정의되어야 합니다.
4. **[P-7] Response Consistency:** 모든 응답은 `TextResponse` 또는 `JsonResponse` 규격을 준수해야 합니다.

## 🏛️ Matrix Design Note
이 회선은 시스템의 중심점입니다. 어떠한 경우에도 로직의 '중력'이 이곳에 쏠리지 않도록 분산 구조를 유지하십시오.
