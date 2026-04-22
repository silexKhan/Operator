# ADR: Adoption of Strict Type Hinting in Core Actions

## 1. Decision
- `CoreActions`의 모든 메서드와 내부 유틸리티 함수에 명시적 타입 힌트와 표준 Docstring을 적용한다.

## 2. Reason
- AI 에이전트가 코드를 분석할 때 '짐작'하는 영역을 줄이고, `PythonAuditor`와 같은 물리 검증 도구가 코드를 정확히 인식하도록 돕기 위함.

## 3. Trade-off
- 코드의 줄 수가 약간 늘어날 수 있으나, 정적 분석 도구를 통한 조기 에러 적발의 이득이 더 크다.
