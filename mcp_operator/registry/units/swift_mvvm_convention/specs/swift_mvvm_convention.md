# [SPEC] Swift MVVM Architecture Convention

## 1. 개요 (Overview)
본 문서는 GDR 프로젝트 및 Swift 기반 모든 개발 작업에서 준수해야 할 **Strict MVVM** 아키텍처 및 코딩 컨벤션을 정의한다. 오퍼레이터(AI)는 본 명세를 최우선 지침으로 삼아 코드를 생성 및 수정한다.

---

## 2. 아키텍처 원칙 (Architecture Principles)

### 2.1 Dumb View (Protocol S-1)
- **ViewController/View는 '바보(Dumb)'여야 한다.** 로직을 판단하거나 조건을 처리(`if`, `switch` 등)해서는 안 된다.
- 단순히 UI 이벤트를 수집하여 `Input`으로 넣고, `Output`으로 내려오는 데이터를 화면에 그리거나 명령을 실행만 한다.
- **화면 이동(Navigation) 제어:** 
    - **ViewModel**은 화면 이동이 필요한 시점에 `Output`을 통해 구체적인 이동 명령을 스트림으로 내려보낸다.
    - **표준 타입:** `AnyPublisher<(UIViewController, Bool), Never>` 형식을 사용하여 전환할 대상과 애니메이션 여부를 함께 전달한다.
    - **ViewController**는 해당 스트림을 구독하여 실제 화면 전환 액션(`present`, `push` 등)만을 대리 실행한다.

### 2.2 ViewModel Input/Output (Protocol S-2)
- 모든 비즈니스 로직은 **ViewModel** 내에 `Input`/`Output` 구조체와 `transform()` 메서드로 정의되어야 한다.
- **명세화 지침:** `Input`과 `Output` 구조체는 시스템의 **최종 명세서**이다. 각 필드에는 상세한 주석을 작성하여, 해당 구조체만 보아도 전체 기능 구조를 파악할 수 있어야 한다.
- **함수 분리 규칙 (ViewController):** `bindViewModel` 메서드가 길어지는 것을 방지하기 위해, `Input` 구조체를 생성하는 로직은 반드시 **`createInput() -> ViewModel.Input`** 메서드로 분리하여 작성한다. **이 메서드는 바인딩 파이프라인의 핵심이므로 메인 클래스 본문에 위치한다.**

### 2.3 구현 예시 (Implementation Example)

```swift
// [Standard Strict MVVM with Extension Pattern]

// 1. ViewModel: 정체성 정의 및 스트림 연결 (Main Class)
class SampleViewModel {
    /// [Specification] ViewModel의 입력 정의 (UI 이벤트 명세)
    struct Input {
        /// ViewController의 준비 완료 신호 (초기 데이터 로딩 트리거)
        let ready: AnyPublisher<Void, Never>
        /// 로그인 버튼 탭 이벤트
        let login: AnyPublisher<Void, Never>
    }

    /// [Specification] ViewModel의 출력 정의 (상태 및 명령 명세)
    struct Output {
        /// 화면에 표시할 메인 타이틀 텍스트
        let title: AnyPublisher<String, Never>
        /// 화면 전환(Present) 명령 스트림: (전환될 ViewController, 애니메이션 여부)
        let presentViewController: AnyPublisher<(UIViewController, Bool), Never>
        /// 화면 전환(Push) 명령 스트림: (전환될 ViewController, 애니메이션 여부)
        let pushViewController: AnyPublisher<(UIViewController, Bool), Never>
    }

    // [Rule] 전역 변수 및 상태 선언은 메인 클래스 본문에 유지
    private let title = CurrentValueSubject<String, Never>("준비 중...")
    private let presentSubject = PassthroughSubject<(UIViewController, Bool), Never>()
    private let pushSubject = PassthroughSubject<(UIViewController, Bool), Never>()
    private var cancellables = Set<AnyCancellable>()

    func transform(input: Input) -> Output {
        // [Rule] 메모리 누수 방지를 위해 반드시 [weak self]를 사용하며, 익명 클로저 내에서 Handler 함수를 호출한다.
        // [Rule] transform 내 파이프라인 연결부는 무조건 함수로 연결하여 선언적 가독성을 확보한다.
        input.ready
            .sink { [weak self] in 
                self?.readyHandler() 
            }
            .store(in: &cancellables)

        input.login
            .sink { [weak self] in 
                self?.loginHandler() 
            }
            .store(in: &cancellables)
        
        return Output(
            title: title.eraseToAnyPublisher(),
            presentViewController: presentSubject.eraseToAnyPublisher(),
            pushViewController: pushSubject.eraseToAnyPublisher()
        )
    }
}

// [Rule] 주요 비즈니스 로직은 Extension으로 분리하여 본체 비대화 방지
extension SampleViewModel {
    // [Rule] Naming: [InputName]Handler 형식을 사용
    private func readyHandler() {
        // [Rule] sink 클로저 내 로직이 3줄 이상이 될 경우 별도 함수로 더욱 세분화
        self.loadInitialData()
    }

    private func loginHandler() {
        let nextViewController = NextViewController()
        self.presentSubject.send((nextViewController, true))
    }

    private func loadInitialData() {
        self.title.send("데이터 로드 완료!")
    }
}

// 2. ViewController: UI 선언 및 핵심 바인딩 파이프라인 (Main Class)
final class SampleViewController: UIViewController {
    private let viewModel = SampleViewModel()
    private var cancellables = Set<AnyCancellable>()
    
    // [Convention] ViewController의 준비 상태를 명시적으로 알리기 위한 서브젝트
    private let ready = PassthroughSubject<Void, Never>()

    override func viewDidLoad() {
        super.viewDidLoad()
        bindViewModel()
        
        // [Rule] 바인딩 완료 후, ViewModel에게 준비가 되었음을 명시적으로 알림 (지휘 계통 시작)
        ready.send(())
    }

    // [Core Pipeline] ViewModel과 View를 연결하는 핵심 메서드 (본문 위치)
    private func bindViewModel() {
        let input = createInput()
        let output = viewModel.transform(input: input)

        // [Data Binding] 모든 UI 업데이트는 반드시 메인 스레드에서 수신 (Thread Safety)
        output.title
            .receive(on: DispatchQueue.main)
            .assign(to: \.text, on: titleLabel)
            .store(in: &cancellables)

        // [Navigation Binding] 전달받은 ViewController와 애니메이션 값을 사용하여 실제 전환 액션 수행
        output.presentViewController
            .receive(on: DispatchQueue.main)
            .sink { [weak self] (viewController, animated) in
                self?.present(viewController, animated: animated)
            }
            .store(in: &cancellables)

        output.pushViewController
            .receive(on: DispatchQueue.main)
            .sink { [weak self] (viewController, animated) in
                self?.navigationController?.pushViewController(viewController, animated: animated)
            }
            .store(in: &cancellables)
    }

    // [Core Pipeline] UI 이벤트를 Input 스트림으로 구성 (핵심 로직이므로 본문 위치)
    private func createInput() -> SampleViewModel.Input {
        return SampleViewModel.Input(
            ready: ready.eraseToAnyPublisher(),
            login: loginButton.tapPublisher
        )
    }
}

// [Rule] 기타 보조 로직(UI 설정, 프로토콜 구현 등)은 Extension으로 분리
extension SampleViewController {
    private func setupUI() {
        // UI 초기 설정 로직 구현
    }
}
```

---

## 3. 코딩 컨벤션 (Coding Standards)

### 3.1 옵셔널 처리 (Safety First - Protocol S-4)
- 강제 언래핑(`!`) 사용을 엄격히 금지한다.
- 반드시 `guard let` 또는 `if let`을 통한 안전한 바인딩을 수행한다.
- 기본값(Default Value) 제공이 가능한 경우 옵셔널 체이닝과 함께 활용한다.

### 3.2 지휘 계통 준수 (Event Chain - Protocol S-7)
- 하위 View는 **ViewModel**과 직접 통신하지 않으며, 반드시 **ViewController**가 이벤트를 중계한다.
- 모든 비즈니스 판단 및 상태 제어는 오직 **ViewModel**만이 수행한다.

### 3.3 Extension 기반 역할 분리 (Protocol S-3)
- **Main Class 역할:** 전역 변수(State) 선언, 초기화(`init`), 핵심 바인딩 파이프라인(`bindViewModel`, **`createInput`**) 등 객체의 뼈대와 핵심 통로 역할을 수행한다.
- **Extension 역할:** 주요 비즈니스 로직의 상세 구현(**ViewModel**), UI 초기 설정(**ViewController**), 프로토콜(Delegate 등) 구현부 등을 분리하여 클래스 본체의 비대화를 방지하고 가독성을 확보한다.

### 3.4 스레드 및 메모리 안전성 (Thread & Memory Safety - Protocol S-5)
- **Thread Safety:** **ViewController**는 UI 업데이트 및 화면 전환과 관련된 모든 **Output** 수신 시, 반드시 **`.receive(on: DispatchQueue.main)`**을 명시하여 메인 스레드 실행을 보장한다.
- **Memory Safety:** 모든 **`sink`** 바인딩 시 반드시 **`[weak self]`**를 사용하여 강한 참조 순환(Retain Cycle)을 방지한다. **함수 참조 방식(`receiveValue: self.handler`)은 강한 참조를 유발하므로 사용을 엄격히 금지한다.**

### 3.5 비즈니스 로직 처리 및 명세화 (Protocol S-6)
- **명칭 규약:** `Input` 처리를 위한 메서드는 반드시 **`[InputName]Handler`**로 명명한다. (e.g., `login` -> `loginHandler`)
- **Combine 클로저 제약:** `sink` 내부의 로직은 **최대 3줄**까지만 허용하며, 이를 초과할 경우 반드시 별도의 함수로 분리하여 호출한다.
- **I/O 명세화:** `Input/Output` 구조체는 시스템의 최종 명세서 역할을 수행해야 하므로, 모든 필드에 상세한 주석을 작성한다.

---

## 4. 참고 문서 (Reference)
- [GDR NetworkService Guide]: 신규 네트워크 엔진 활용법 참조.
- [TaskStatusProtocol Guide]: 앱 상태(Foreground/Background) 연동 규격 참조.

---

## 5. 변경 이력 (Changelog)
- **2026.04.02**: 초안 작성 (Sentinel Auto-pilot 기반)
- **2026.04.03**: AppNavigator 제거, Extension 분리 및 PassthroughSubject 기반 ready 트리거 규약 추가
- **2026.04.03**: createInput 메서드 본문 이동 및 변수명 정제
- **2026.04.03**: ViewModel Output에 present/pushViewController 표준 타입 추가 및 ViewController 바인딩 로직 명시
- **2026.04.03**: 가독성 향상을 위해 모든 약어(VC, VM)를 풀네임(ViewController, ViewModel)으로 교체
- **2026.04.03**: 모든 UI 관련 Output에 메인 스레드 수신 규약 및 [weak self] 메모리 안전성 규약 통합
- **2026.04.03**: Handler 명명 규칙, Combine 3줄 제약 및 I/O 명세화 주입 규약 추가 (Protocol S-6)
