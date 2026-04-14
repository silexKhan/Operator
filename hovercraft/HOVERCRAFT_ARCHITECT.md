# 🏛️ HOVERCRAFT ARCHITECT'S EQUATION

"The UI is the window to the Machine."

## 1. The Purpose (존재의 목적)
- 본 유닛은 매트릭스(백엔드)의 복잡한 데이터 흐름을 시각화하고, 대장님(사용자)의 명령을 그래픽 인터페이스로 변환하여 전달하는 **'시각적 중재자'**이다.

## 2. The Equation (불변의 방정식)
- **E-1 (Reactive IPC Pull):** 실시간 상태 동기화는 `/api/mcp/state` Polling 및 SSE 채널로 일원화한다.
- **E-2 (Layout Metrics Wall):** 시스템 전체 레이아웃은 `w-64` 사이드바와 `h-14` 헤더로 고정하며, 카드 간의 간격은 `gap-6`, 내부 패딩은 `p-8`을 기본값으로 한다.
- **E-3 (Anatomy of StandardModal):** 모든 모달은 `fixed inset-0 z-50` 배경(`bg-black/60 backdrop-blur-sm`) 위에서 `max-w-2xl` 너비를 가지며, 헤더(`h-14`), 본문(`p-6`), 하단 버튼 영역(`px-6 py-4 bg-neutral-900/80 border-t`)으로 해부학적 구조를 고정한다.
- **E-4 (State Transition Wall):** 유닛 및 규약 편집 시 'Active Item'은 반드시 `bg-emerald-500/10`, `border-emerald-500/50`을 적용하고, 편집 텍스트는 `font-mono text-emerald-400`을 강제한다.
- **E-5 (Absolute Token Wall):** 배경색은 `bg-neutral-950`(Main)과 `bg-neutral-900`(Card), 보더는 `border-neutral-800`을 리터럴하게 사용한다. AI가 임의로 색상 가중치를 계산하지 않도록 한다.
- **E-6 (Font System Wall):** 모든 폰트는 `next/font/google`을 통해 로컬로 자동 최적화 로드하며, 기본 폰트는 `Inter`, 모노 영역은 `JetBrains Mono`로 강제한다. 외부 `<link>` 태그 사용은 금지한다.

## 3. TDD Fences (활동 범위 및 울타리)
- **F-0 (Framework Anomaly):** Next.js v16.2.1 규약 엄수 (node_modules/next/dist/docs/ 참조).
- **F-1 (Reference Integrity):** 파일 이동 시 `CLAUDE.md` 내 경로 즉시 갱신.
- **F-2 (Usability Constraint):** 버튼/입력창은 최소 `h-10`(40px) 이상을 확보하며, 클릭 시 `scale-95` 또는 `opacity-80` 피드백을 150ms 이내에 제공한다.

## 4. Prohibited Boundaries (금지된 경계)
- **B-1:** 비즈니스 로직의 `src/` 또는 `app/` 외부 유출 금지.
- **B-2:** `prompt` 및 `alert` 같은 브라우저 네이티브 다이얼로그 사용을 엄격히 금지하며, 반드시 시스템 내부 컴포넌트로 대체한다.
- **B-3:** 정보 전달에 기여하지 않는 그림자(`shadow-xl` 이상), 그라데이션, 화려한 애니메이션은 개발력 낭비로 간주하여 차단한다.
