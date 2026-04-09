# 🏛️ SPEC: Unified Configuration Editor System (V2 - Modern Dashboard)

## 1. 개요 (Overview)
본 시스템은 기존의 장식적인 터미널 UI를 탈피하고, 실용성과 가독성을 극대화한 **'모던 대시보드(Sidebar + Main Content)'** 구조를 채택한다. 엔진의 모든 상태와 구성을 실시간으로 관제하고, 복잡한 JSON 수정 없이 UI 상에서 즉각적인 정책 변경(Hot-fix)을 수행하는 것을 목적으로 한다.

## 2. 통신 및 데이터 아키텍처 (Communication & Data)

### 2.1 [SSE-B] Reactive Full-Package Stream
- **방식:** Server-Sent Events (SSE) 기반 실시간 푸시.
- **Data Enrichment:** 엔진의 최소 상태(`state.json`)를 백엔드 브릿지가 가공하여, 활성 회선의 `overview`, `protocols`, `units` 상세 정보를 하나의 패키지로 조립하여 전송한다.
- **장점:** UI는 별도의 복잡한 API 호출 없이 수신된 `active_circuit_details` 객체만으로 모든 화면을 렌더링할 수 있다.

### 2.2 [IPC-W] Atomic Write Interface
- **방식:** `POST /api/mcp/update`를 통한 파일 기반 쓰기.
- **보안:** 쓰기 전 `data/history/`에 자동 백업 생성.
- **리로딩:** 파일 수정 후 `state.json`의 타임스탬프를 갱신하여 엔진이 변경 사항을 즉시 리로드하도록 유도한다.

## 3. 화면 구성 및 사용자 경험 (UI/UX)

### 3.1 [Sidebar] Global Navigation
- 시스템 상태(Connected/Disconnected), 현재 활성 회선(Active Circuit) 상시 노출.
- 메뉴: Overview(미션), Protocols(규약), Units(유닛 관리), Monitor(리소스/보안).

### 3.2 [Main Content] Contextual Panels
- **Overview:** 큼직한 폰트의 미션 목표 및 성공 기준 리스트. 인라인 편집 지원.
- **Protocols:** 글로벌/회선 규약의 텍스트 기반 에디터.
- **Units:** 유닛 배속 관리(Checkbox) 및 유닛별 개별 미션/룰 수정 인터페이스.
- **Monitor:** 슬라이더 기반 임계치 조절 및 감사 이력 시각화.

### 3.3 [Bottom] Silent Console
- 시스템 로그를 하단 드로어로 분리하여 작업 중 노이즈 최소화.

## 4. 진행 현황 (Progress Report)

| 과업 (Task) | 상태 (Status) | 내용 |
| :--- | :--- | :--- |
| **Backend API** | ✅ 완료 | 조회, 수정, 백업, 리로드 트리거 로직 구축 |
| **SSE Bridge** | ✅ 완료 | 데이터 인리치먼트(Enrichment) 및 실시간 푸시 구현 |
| **Dashboard UI** | ✅ 완료 | Sidebar + Main Content 모던 레이아웃 전환 |
| **Editor Mode** | ✅ 완료 | 각 패널별 인라인 편집 및 API 연동 완료 |
| **Style Cleanup** | ✅ 완료 | 매트릭스 테마 제거 및 가독성 중심 디자인 적용 |

## 5. 추가 진행 과업 (Future Roadmap)

### 5.1 [UI-P] UI 세부 디테일 강화
- **Transitions:** 탭 전환 및 편집 모드 진입 시 부드러운 애니메이션 추가.
- **Loading States:** API 호출 시 스켈레톤 UI 또는 명확한 로딩 인디케이터 제공.
- **Toast Notifications:** 저장 성공/실패 시 사용자에게 즉각적인 알림 제공.

### 5.2 [SEC] 보안 및 검증 로직
- **JSON Schema Validation:** UI에서 저장 시 데이터 형식이 올바른지 프론트/백엔드 이중 검증.
- **Diff Preview:** 저장 버튼 클릭 전, 변경된 내용(Before vs After)을 시각적으로 확인하는 창 제공.

### 5.3 [FEAT] 고급 기능 확장
- **Circuit Blueprint:** 새로운 회선을 생성할 때 템플릿(GDR용, 리서치용 등) 선택 기능.
- **Audit Visualization:** 보안 위반 이력을 단순히 텍스트가 아닌 타임라인 그래프로 시각화.
- **Remote Terminal:** 하단 로그 패널에서 엔진으로 직접 명령어를 전송할 수 있는 대화형 CLI 기능 활성화.

---
*최종 업데이트: 2026-04-09*
*작성 주체: MCP Operator (Main Bridge)*
