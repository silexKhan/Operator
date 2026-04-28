# Planning Unit Architecture & Convention Guide

이 가이드는 사용자 경험(UX) 중심의 정밀한 기획 문서 작성을 지향합니다.

## 1. 문서 필수 구조 (Mandatory Structure)

모든 기획 문서는 다음의 순서와 목차 구조를 엄격히 준수해야 합니다.

1.  **# [제목]**: 미션의 핵심 목표
2.  **# 1. User Workflow**: 사용자의 전체 여정을 단계별로 나열 (예: 진입 -> 탐색 -> 선택 -> 완료)
3.  **# 2. Table of Contents (TOC)**: 하위 상세 기획의 인덱스
4.  **# 3. Detailed Specifications**: TOC에 명시된 항목별 상세 페이지/기능 기획

## 2. 핵심 컨벤션 (Planning Standards)

- **Workflow-Driven:** 기능 중심이 아닌 사용자 여정 중심으로 목차를 구성합니다.
- **Header Matching:** TOC의 항목명과 `##` 상세 섹션의 제목은 토씨 하나 틀리지 않고 일치해야 합니다.
- **Scenario Inclusion:** 각 상세 기획에는 반드시 '정상 흐름'과 '예외 흐름'이 포함되어야 합니다.

## 3. 기획 예시 (영화표 예매 예시)

```markdown
# 영화표 예매 시스템 기획서

# 1. User Workflow
영화 목록 탐색 -> 영화 선택 -> 상영 시간 및 좌석 선택 -> 결제 진행 -> 예매 완료 확인

# 2. Table of Contents (TOC)
- 메인 영화 리스트 페이지
- 상영 시간 및 좌석 선택 레이어
- 결제 통합 모듈
- 예매 완료 및 티켓 확인 페이지

# 3. Detailed Specifications

## 메인 영화 리스트 페이지
- [기능] 현재 상영작 및 개봉 예정작 필터링...
- [UI] 포스터 중심의 그리드 레이아웃...

## 상영 시간 및 좌석 선택 레이어
...
```
