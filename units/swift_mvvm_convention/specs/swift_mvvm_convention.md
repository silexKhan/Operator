# [SPEC] Swift MVVM Architecture Convention

## 1. 개요 (Overview)
본 문서는 GDR 프로젝트 및 Swift 기반 모든 개발 작업에서 준수해야 할 **Strict MVVM** 아키텍처 및 코딩 컨벤션을 정의한다. 오퍼레이터(AI)는 본 명세를 최우선 지침으로 삼아 코드를 생성 및 수정한다.

---

## 2. 아키텍처 원칙 (Architecture Principles)

### 2.1 Dumb View (Protocol S-1)
- **ViewController/View는 '바보(Dumb)'여야 한다.** 로직을 판단하거나 조건을 처리(`if`, `switch` 등)해서는 안 된다.
- 단순히 UI 이벤트를 수집하여 `Input`으로 넣고, `Output`으로 내려오는 데이터를 화면에 그리거나 명령을 실행만 한다.
- **화면 이동(Navigation) 제어:** 
    - 만약 **`AppNavigator`**와 같은 별도의 라우팅 객체를 사용 중이라면, ViewModel이 직접 Navigator를 호출하여 화면을 전환한다. 이 경우 ViewController로 라우팅 명령(`push`, `present` 등)을 내려보낼 필요가 없다.
    - 별도의 Navigator가 없는 경우에만 `Output`에 구체적인 이동 명령(`push`, `present`, `pop`, `dismiss`) 스트림을 두어 ViewController가 대리 실행하게 한다.

### 2.2 ViewModel Input/Output (Protocol S-2)
... (생략) ...
- **함수 분리 규칙 (VC):** `bindViewModel` 메서드가 길어지는 것을 방지하기 위해, `Input` 구조체를 생성하는 로직은 반드시 **`createInput() -> ViewModel.Input`** 메서드로 분리하여 작성한다.

### 2.3 구현 예시 (Implementation Example)

```swift
// [Advanced Dumb-View & Navigator Pattern]

// 1. ViewModel: Navigator를 직접 사용하여 화면 전환 제어 (VC는 모름)
class SampleViewModel {
    struct Input {
        let ready: AnyPublisher<Void, Never>
        let login: AnyPublisher<Void, Never>
    }

    struct Output {
        let title: AnyPublisher<String, Never>
    }

    private let title = CurrentValueSubject<String, Never>("준비 중...")
    private let navigator: AppNavigator // 별도 네비게이터 주입
    private var cancellables = Set<AnyCancellable>()

    init(navigator: AppNavigator) {
        self.navigator = navigator
    }

    func transform(input: Input) -> Output {
        input.login
            .sink { [weak self] in
                // [Navigation] VC에게 시키지 않고 직접 네비게이터 호출
                self?.navigator.showMainScreen() 
            }
            .store(in: &cancellables)

        return Output(title: title.eraseToAnyPublisher())
    }
}

// 2. ViewController: Input 생성을 분리하여 코드 가독성 확보
final class SampleViewController: UIViewController {
    private let viewModel = SampleViewModel(navigator: AppNavigator.shared)
    private var cancellables = Set<AnyCancellable>()

    override func viewDidLoad() {
        super.viewDidLoad()
        bindViewModel()
    }

    private func bindViewModel() {
        // [Pattern] Input 생성 로직을 별도 함수로 호출
        let input = createInput()
        let output = viewModel.transform(input: input)

        output.title
            .assign(to: \.text, on: titleLabel)
            .store(in: &cancellables)
    }

    // [Convention] UI 이벤트 수집 로직을 명확히 분리
    private func createInput() -> SampleViewModel.Input {
        return SampleViewModel.Input(
            ready: Just(()).eraseToAnyPublisher(),
            login: loginButton.tapPublisher,
            userIdInput: idTextField.textPublisher
        )
    }
}
```
// 2. ViewController: UI 이벤트 바인딩 및 렌더링 담당
final class SampleViewController: UIViewController {
    private let viewModel = SampleViewModel()
    private var cancellables = Set<AnyCancellable>()
    
    // UI Components (UILabel, UITextField, UIButton 등)
    
    private func bindViewModel() {
        // [Input] UI 이벤트를 퍼블리셔로 변환하여 수집
        let input = SampleViewModel.Input(
            didTapButton: actionButton.publisher(for: .touchUpInside).map { _ in }.eraseToAnyPublisher(),
            textInputChange: textField.publisher(for: .editingChanged)
                .map { ($0 as? UITextField)?.text ?? "" }
                .eraseToAnyPublisher()
        )
        
        // [Transform] ViewModel에 전달하여 Output 획득
        let output = viewModel.transform(input: input)
        
        // [Output] 수신된 데이터를 UI 요소에 배정 (Data Binding)
        output.titleLabelText
            .assign(to: \.text, on: titleLabel)
            .store(in: &cancellables)
            
        output.isButtonEnabled
            .assign(to: \.isEnabled, on: actionButton)
            .store(in: &cancellables)
    }
}
```

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
