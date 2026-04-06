# SystemLogs Architect

## Equation (방정식)
`SystemLogs = ∂(WebSocketData) / ∂t`
> "로그는 시간에 따른 웹소켓 데이터의 변화량이다."

## TDD Fences (울타리)
1. **Unidirectional Data Flow**: Props를 통한 로그 수신만 허용하며, 로그 배열 자체를 수정하지 않는다.
2. **Auto-Scroll Integrity**: 하단 스크롤 동기화는 `logEndRef`를 통해 외부로부터 제어되거나 내부적으로 완결되어야 한다.
3. **Immutability Check**: 수신된 로그 엔트리는 불변(Immutable) 상태로 유지한다.
4. **Offline Resilience**: 연결 끊김 상태(`DISCONNECTED`)에서도 이미 수신된 로그의 무결성을 유지하며 화면에 표시한다.
