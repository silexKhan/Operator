# CoreAccess Architect

## Equation (방정식)
`CoreAccess = ∫(CommandInput + McpStatusRequest) dt`
> "커맨드 입력과 MCP 상태 요청의 시간 적분은 코어 액세스의 권한을 결정한다."

## TDD Fences (울타리)
1. **Isolation Mandate**: 다른 윈도우의 상태(Logs, Radar 등)에 직접 간섭하지 않는다.
2. **Prop Dependency**: 오직 `requestMcpStatus` 함수를 통해서만 외부 엔진과 소통한다.
3. **Internal State Only**: 내부 인풋 필드의 로컬 상태는 컴포넌트 내부에서만 관리하며, 결과값만 외부로 전파한다.
4. **Style Consistency**: `terminal-window` 및 `text-green-500` 테마를 엄격히 준수한다.
