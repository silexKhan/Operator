# 📑 UI_REORGANIZATION_SPEC.md (Hovercraft UI 개편 명세서)

"The UI is the window to the Machine. Clean the window."

## 1. 개요 (Overview)
본 문서는 호버크래프트(Hovercraft) UI의 불필요한 장식적 요소를 제거하고, MCP 시스템의 규약 준수 및 실질적 제어에 집중하는 **'실전형 지휘소(Operational Command Center)'**로의 개편을 명세한다.

## 2. 컴포넌트 재구성 전략 (Reorganization Strategy)

| 현재 컴포넌트 | 개편 방향 | 기능 정의 (Functional Goal) |
| :--- | :--- | :--- |
| **CoreAccess** | **유지 및 강화** | 회선 전환, 전역/회선 규약 실시간 시각화, 명령 입력창 강화 |
| **SystemLogs** | **유지 및 강화** | 백엔드 실시간 로그 스트리밍, 감사 위반 사례 강조(Highlighting) |
| **ShipStatus** | **Resource Monitor** | CPU/MEM 부하, MCP 서버 연결 지연시간(Latency), 업타임 실시간 표시 |
| **SentinelTracking** | **Security Dashboard** | 규약 위반(Audits) 탐지 이력, 실시간 보안 위협 수준 표시 |
| **RadarUplink** | **제거 또는 대체** | (대체 시) 'Mission Specs' 조회창으로 변경하여 현재 미션의 상세 정보 상시 노출 |
| **ZionComms** | **제거 또는 대체** | (대체 시) 'Unit Protocols' 요약창으로 변경하여 배속된 유닛의 세부 규칙 상시 노출 |

## 3. 시각적 가이드라인 (Visual Guidelines)
- **Data over Aesthetics:** 움직이는 단순 애니메이션보다 실질적인 수치(Percentage, Latency)와 상태 텍스트를 우선한다.
- **Protocol First:** 사용자가 어떤 회선에 있든, 적용 중인 **'지배 규약'**이 항상 시야에 들어와야 한다.
- **Alert System:** 규약 위반 발생 시 로그와 보안 대시보드에 즉각적인 시각적 경고(Red Glow)를 적용한다.

## 4. 구현 단계 (Implementation Phases)
1. **[Phase 1]:** 각 윈도우 컴포넌트 소스 분석 및 '빈 껍데기' 로직 식별 (Current Step)
2. **[Phase 2]:** 불필요한 컴포넌트(`RadarUplink`, `ZionComms`) 제거 및 `page.tsx` 그리드 재배치
3. **[Phase 3]:** 대체 컴포넌트(`MissionSpecs`, `ResourceMonitor`) 신규 개발 및 데이터 바인딩
4. **[Phase 4]:** 실시간 감사 데이터 연동 및 경고 시스템(Sentinel Alert) 고도화

---

## 🛠️ Technical Implementation Notes (Troubleshooting)

### A. 빌드 및 환경 설정 (Next.js 16 + Tailwind CSS v4)
- **이슈:** `tailwindcss`와 `@tailwindcss/postcss` 플러그인 중복 호출 시 `globals.css` 평가 에러 발생.
- **해결:** `postcss.config.mjs`에서 `'tailwindcss': {}`를 제거하고 `@tailwindcss/postcss`만 사용하도록 고정한다.

### B. 데이터 연동 (IPC State)
- **상태 파일:** 오퍼레이터 엔진이 생성하는 실제 상태 파일은 `../data/state.json`이다. (`mcp_state.json` 아님)
- **API 엔드포인트:** `/api/mcp/state`는 상기 파일을 Surgical Read 하여 UI에 'ONLINE' 상태와 현재 회선 정보를 제공해야 한다.

