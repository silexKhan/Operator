# 🍎 Standard App 프로젝트: Strict MVVM & Swift 코딩 컨벤션

본 문서는 Swift 기반 모든 모바일 앱 개발 작업에서 준수해야 할 **Strict MVVM** 아키텍처 및 코딩 컨벤션을 정의한다. 오퍼레이터(AI)는 본 명세를 최우선 지침으로 삼아 코드를 생성 및 수정한다.

## 1. 아키텍처 원칙: Strict MVVM

### 1.1 View (ViewController / SwiftUI View)
- **Dumb View Principle**: View는 비즈니스 로직을 전혀 가지지 않는다. 오직 ViewModel의 상태를 화면에 그리고, 사용자 액션을 전달하는 역할만 수행한다.
- **Input/Output Binding**: 모든 UI 갱신은 ViewModel의 `Output` 객체와 연결되어야 한다.
- **Dependency Injection**: ViewController는 ViewModel을 생성자 주입(Initializer Injection) 방식으로 소유한다.

### 1.2 ViewModel
- **Pure Logic**: ViewModel은 UIKit을 임포트하지 않으며, 순수 Swift 타입만 사용하여 로직을 작성한다.
- **Protocol-Based**: ViewModel은 반드시 `ViewModelType` 프로토콜(Input/Output 구조)을 준수해야 한다.
- **State Management**: 상태 관리는 클로저나 Combine의 `@Published`, `CurrentValueSubject` 등을 활용하여 반응형으로 구현한다.

## 2. 코딩 컨벤션 상세 (Swift Standard)

### 2.1 네이밍 규칙
- **Variables**: 명확한 의미를 전달하는 camelCase를 사용한다. (e.g., `userProfileImageUrl`)
- **Functions**: 동사로 시작하며 목적을 분명히 한다. (e.g., `fetchUserData()`, `updateSubmitButtonState()`)
- **Protocols**: `-able`, `-ing`, `-Type` 접미사를 사용하여 역할을 명시한다.

### 2.2 코드 가독성 및 안전성
- **No Force Unwrapping**: `!` 사용을 절대 금지하며, 반드시 `if let` 또는 `guard let`으로 안전하게 추출한다.
- **Enum for State**: 단순 문자열이나 숫자가 아닌 Enum을 통해 상태를 정의하고 타입 안정성을 확보한다.
- **Swift Concurrency**: 비동기 로직은 `async/await`를 우선적으로 사용하며, 메모리 누수 방지를 위해 `[weak self]`를 적절히 배치한다.

## 3. 관련 기술 가이드
- **[App NetworkService Guide]**: 신규 네트워크 엔진 활용법 및 API 에러 핸들링 전략 참조.
- **[UI Kit Standard]**: 전사 표준 UI 컴포넌트 라이브러리 활용 가이드.

---
*본 명세는 Standard App 프로젝트의 기술적 무결성을 위해 주기적으로 업데이트됩니다.*
