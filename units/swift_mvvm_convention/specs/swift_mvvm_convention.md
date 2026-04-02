# [SPEC] Swift MVVM Architecture Convention

## 1. 개요 (Overview)
본 문서는 GDR 프로젝트 및 Swift 기반 모든 개발 작업에서 준수해야 할 **Strict MVVM** 아키텍처 및 코딩 컨벤션을 정의한다. 오퍼레이터(AI)는 본 명세를 최우선 지침으로 삼아 코드를 생성 및 수정한다.

---

## 2. 아키텍처 원칙 (Architecture Principles)

### 2.1 Dumb View (Protocol S-1)
- **ViewController/View**는 비즈니스 로직을 가질 수 없다.
- UI 렌더링 및 사용자 이벤트 수집(Event Trigger)에만 집중한다.
- 데이터 가공이나 판단 로직은 반드시 ViewModel에서 수행한다.

### 2.2 ViewModel Input/Output (Protocol S-2)
- 모든 ViewModel은 명확한 `Input`과 `Output` 구조체(Struct)를 소유한다.
- 외부(VC)에서는 오직 `transform(input:)` 메서드를 통해서만 통신한다.
- `Combine` 퍼블리셔를 활용하여 선언적 데이터 흐름을 유지한다.

---

## 3. 코딩 컨벤션 (Coding Standards)

### 3.1 옵셔널 처리 (Safety First)
- 강제 언래핑(`!`) 사용을 엄격히 금지한다. (Protocol S-4)
- 반드시 `guard let` 또는 `if let`을 통한 안전한 바인딩을 수행한다.
- 기본값(Default Value) 제공이 가능한 경우 옵셔널 체이닝과 함께 활용한다.

### 3.2 지휘 계통 준수 (Event Chain)
- 하위 View는 ViewModel과 직접 통신하지 않는다. (Protocol S-7)
- `BaseUpdateProtocol`을 사용하여 이벤트를 ViewController로 던지고, VC가 이를 ViewModel의 Input으로 중계한다.

---

## 4. 참고 문서 (Reference)
- [GDR NetworkService Guide]: 신규 네트워크 엔진 활용법 참조.
- [TaskStatusProtocol Guide]: 앱 상태(Foreground/Background) 연동 규격 참조.

---

## 5. 변경 이력 (Changelog)
- **2026.04.02**: 초안 작성 (Sentinel Auto-pilot 기반)
