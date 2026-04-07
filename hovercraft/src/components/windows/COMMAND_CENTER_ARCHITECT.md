# 🏛️ COMMAND_CENTER_ARCHITECT.md (지휘소 컴포넌트 설계 규약)

"Data is the only truth. Aesthetics is its servant."

## 1. The Core Philosophy (핵심 철학)
본 지휘소 UI는 단순한 시각화를 넘어, MCP 시스템의 **'규약 준수 상태'**와 **'미션 진행 상황'**을 대장님(사용자)이 직관적으로 파악할 수 있게 하는 데 목적을 둔다. 모든 시각 요소는 실제 데이터에 근거해야 한다.

## 2. The Functional Equations (기능 방정식)
- **E-1 (Zero Mock Data):** 모든 컴포넌트는 `setInterval`이나 로컬 상태를 통한 '가짜 데이터 생성'을 금지한다. 데이터는 반드시 WebSocket(Uplink) 또는 API를 통해 수신된 실시간 값이어야 한다.
- **E-2 (Context Persistence):** 회선이 변경되거나 시스템이 리로드되어도, 현재 보고 있는 지배 규약과 미션 정보는 UI 상에서 즉각 동기화되어야 한다.
- **E-3 (Visual Hierarchy):** 규약 위반(Audit Violation)이나 시스템 오류(Error)는 최상위 시각적 우선순위를 가지며, 전용 경고 시스템(Red Glow/Flash)을 통해 사용자에게 즉각 보고되어야 한다.

## 3. Component Standards (컴포넌트 규격)
- **C-1 (Structure):** `src/components/windows/{Name}/{Name}.tsx` 구조를 유지한다.
- **C-2 (Props):** 모든 윈도우 컴포넌트는 부모(`page.tsx`)로부터 통제된 데이터(`systemStatus`, `logs` 등)를 Props로 전달받는 것을 원칙으로 하며, 컴포넌트 내부에서 직접 소켓을 여는 행위를 금지한다.
- **C-3 (Hydration Safety):** Next.js 환경에서의 하이드레이션 오류 방지를 위해, `mounted` 상태 확인 전에는 최소한의 스켈레톤(Skeleton) 또는 서버 사이드 기본값만을 출력한다.

## 4. TDD Fences (활동 범위)
- **F-1 (Refactoring Boundary):** 기존 컴포넌트 수정 시, CSS 클래스명(`terminal-window`, `terminal-header`)은 일관성을 위해 기존 스타일 가이드를 계승한다.
- **F-2 (Data Integrity):** 백엔드에서 내려오는 JSON 데이터의 구조(`type`, `data`, `payload`)를 임의로 변경하지 않고, 프론트엔드에서 안전하게 파싱(Safe Parsing)하여 사용한다.
