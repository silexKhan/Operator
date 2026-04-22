# [UI_GUIDE] 호버크래프트 UI 가이드라인

## 1. 개요 (Overview)
본 가이드는 MCP 통합 지휘소 UI인 '호버크래프트'의 시각적 일관성과 기능적 무결성을 유지하기 위한 설계 표준을 정의한다.

## 2. 디자인 시스템 (Design System)
- **Primary Color:** `#007AFF` (MCP Blue)
- **Secondary Color:** `#5856D6` (Circuit Purple)
- **Success:** `#34C759`
- **Error:** `#FF3B30`
- **Background:** `#F2F2F7` (Light Mode), `#1C1C1E` (Dark Mode)

## 3. 다국어 레이아웃 대응 (I18N Layout)
- **Flexible Width:** 텍스트 길이에 따라 자동으로 확장되는 버튼 및 레이블 사용.
- **Minimum Tap Target:** 모든 대화형 요소는 최소 44x44pt 크기를 유지하여 언어별 텍스트 공간 확보.
- **Line Height:** 다국어 폰트 가독성을 위해 최소 1.4 이상의 line-height 권장.

## 4. 타이포그래피 및 간격 (Typography & Spacing)
- **Font:** SF Pro, Pretendard (Fallback: Sans-serif)
- **Spacing Unit:** 8px 그리드 시스템 기반 (8, 16, 24, 32, 48, 64).
- **Alignment:** 기본적으로 시작 정렬(Start)을 사용하며, 우측 정렬은 필요한 경우에만 제한적으로 사용.

## 5. UI 검증 (UI Validation)
- 모든 신규 컴포넌트는 `SENTINEL` 감사를 통과해야 함.
- Tailwind CSS를 사용하는 경우, 커스텀 테마 설정을 준수하여 임의의 값을 사용하지 않음.
