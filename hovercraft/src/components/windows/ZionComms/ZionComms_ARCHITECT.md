# ZionComms Architect

## Equation (방정식)
`ZionComms = MessageChain + EncryptionKey`
> "메시지 체인과 암호화 키의 조합은 시온의 통신 보안을 완성한다."

## TDD Fences (울타리)
1. **Message Purity**: 외부 통신 내용은 읽기 전용으로 관리하며, 컴포넌트 내부에서 이를 가공하지 않는다.
2. **Identity Isolation**: 발신자(Morpheus, Tank 등)의 식별자는 시스템 로그와 별도의 스타일 가이드를 따른다.
3. **Decoupled Input**: 하단 `tank@neb` 인풋 필드는 통신 시뮬레이션을 위한 독립된 인터페이스로 작동한다.
4. **Style Integrity**: 폰트 크기와 색상 조합은 시온 통신망 전용 테마를 유지한다.
