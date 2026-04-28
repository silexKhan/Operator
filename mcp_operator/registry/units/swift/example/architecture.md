# Modern Swift Architecture & Convention Guide (MVVM)

이 가이드는 UI와 로직의 완벽한 분리 및 테스트 가능성을 극대화하기 위한 **MVVM (Model-View-ViewModel)** 패턴을 지향합니다.

## 1. 아키텍처 계층 구조

| 계층 (Layer) | 역할 (Responsibility) | 특징 |
| :--- | :--- | :--- |
| **Model** | 단순 데이터 구조 및 비즈니스 엔티티 | Struct 사용, 로직 최소화 |
| **ViewModel** | UI 상태 관리 및 비즈니스 로직 | **Input/Output** 구조 필수, 비즈니스 로직의 핵심 |
| **View(Controller)** | UI 렌더링 및 이벤트 전달 | **Dummy View** 원칙 준수 (로직 0%), `createInput()` 사용 |
| **Service/Repository** | 데이터 I/O 및 외부 통신 | Protocol 인터페이스 필수, DI(의존성 주입) |

## 2. 핵심 컨벤션 (Swift Standards)

- **Input/Output Modeling:** ViewModel은 `Input`과 `Output` 구조체를 내부에 포함해야 합니다.
- **Interest Separation:** ViewController는 `createInput() -> Input` 메서드를 통해 **등록(Subscription)과 생성(Creation)의 관심사를 분리**합니다.
- **Conservative Combine:** Combine을 사용하되 과도한 연산자 체이닝을 지양합니다. `sink` 등 실제 데이터를 소비하는 시점에 필요한 최소한의 변환만 수행합니다.
- **Access Control:** `private`를 사용하여 내부 상태를 철저히 캡슐화합니다.

## 3. 코드 구조 예시 (Standard MVVM)

```swift
// [ViewModel]
class UserViewModel {
    struct Input {
        let fetchTrigger: AnyPublisher<Void, Never>
    }
    struct Output {
        let userName: AnyPublisher<String, Never>
    }
    
    func transform(input: Input) -> Output { ... }
}

// [ViewController - Dummy View Principle]
class UserViewController: UIViewController {
    private let viewModel: UserViewModel
    private var cancellables = Set<AnyCancellable>()

    override func viewDidLoad() {
        super.viewDidLoad()
        bind()
    }

    private func bind() {
        let input = createInput() // 관심사 분리
        let output = viewModel.transform(input: input)
        
        output.userName
            .sink { [weak self] name in self?.nameLabel.text = name }
            .store(in: &cancellables)
    }

    private func createInput() -> UserViewModel.Input {
        // 이벤트 소스들을 Input 구조체로 묶어서 반환
        return UserViewModel.Input(fetchTrigger: button.tapPublisher)
    }
}
```

## 4. 금기 사항 (Anti-Patterns)
- **Massive View Controller:** ViewController에 연산 로직이나 복잡한 조건문을 넣지 않습니다. (Dummy View 원칙 위반)
- **Complex Combine Chains:** 이해하기 어려운 긴 Combine 연산자 체인을 작성하지 않습니다.
- **Hard Dependencies:** 클래스 내부에서 직접 인스턴스를 생성하지 않고 주입받습니다.
