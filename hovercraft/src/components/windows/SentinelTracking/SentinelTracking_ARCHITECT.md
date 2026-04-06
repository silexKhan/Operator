# SentinelTracking Architect

## Equation (방정식)
`SentinelTracking = ThreatValue * ProbabilityMatrix`
> "위협 수치와 확률 행렬의 곱은 센티널의 추적 정밀도를 정의한다."

## TDD Fences (울타리)
1. **Encapsulated Logic**: 바이너리 스트리밍 데이터의 시각적 표현은 컴포넌트 내부에서 완결한다.
2. **Read-Only Props**: 상위 컴포넌트로부터 전달받는 위협 데이터는 오직 렌더링 목적으로만 사용한다.
3. **Emergency State**: 비상 상태(`emergency`) UI 트리거는 외부 상태와 독립적으로 작동하거나, 명확한 Props 신호에 의해서만 변경된다.
4. **Binary Integrity**: 하단에 표시되는 바이너리 텍스트는 데이터 무결성 레이어를 상징하며, 사용자 수정을 허용하지 않는다.
