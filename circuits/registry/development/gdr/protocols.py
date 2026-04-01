#  protocols.py - GDR 프로젝트 핵심 규약 (Project Alpha)
class Protocols:
    PROJECT_NAME = "GDR (프로젝트 알파)"
    # [사용자] 골프존 GDR 개발 시 AI가 준수해야 할 4대 핵심 규약(Protocols)입니다.
    RULES = [
        "Protocol S-1 (Strict MVVM): ViewController는 비즈니스 로직을 가질 수 없으며, 반드시 ViewModel을 통해 데이터와 통신한다. (Dumb View 원칙)",
        "Protocol S-2 (Business Specification): 모든 비즈니스 로직은 ViewModel 내에 Input/Output 구조체와 transform() 메서드로 정의되어야 한다.",
        "Protocol S-3 (Safety-First): fatalError() 등 앱 중단 코드는 사용 금지하며, 예외 상황 발생 시 적절한 유휴 상태를 유지한다.",
        "Protocol S-4 (No Forced Unwrapping): 강제 언래핑('!') 사용을 금지하며, 반드시 guard let 또는 if let을 통해 안전하게 추출한다."
    ]
    @classmethod
    def get_rules(cls): return cls.RULES
