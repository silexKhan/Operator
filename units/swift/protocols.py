#
#  protocols.py - Standard Swift & MVVM Architecture Rules
#  (Level 2: Unit Protocols - Software Engineering / Swift)
#

class SwiftProtocols:
    """
    [대장님 🎯] Swift 유닛 전용 전문 기술 수칙입니다.
    상위 규약은 회선(Circuit)에서 상속받으므로, 여기서는 기술 본질에만 집중합니다. 🍎⚡️
    """

    @classmethod
    def get_rules(cls):
        UNIT_RULES = [
            "Protocol S-1 (Strict MVVM): Dumb View logic segregation 🏗️",
            "Protocol S-2 (SWR Data Flow): Cache -> Server flow priority 🔄",
            "Protocol S-3 (Safety-First): No fatalError, Idle state over Crash 🚑",
            "Protocol S-4 (No Forced Unwrapping): No '!' usage allowed 🛡️",
            "Protocol S-5 (Combine Naming): Same name for Private/Public, No 'Subject' Suffix ⛓️",
            "Protocol S-6 (Combine Primary): Active Use Required for bindings 🚀",
            "Protocol S-7 (No @IBAction): Use Combine Binding instead 🛡️",
            "Protocol S-8 (Clean Extension): Avoid private extension, use individual private 🧼",
            "Protocol S-9 (Data Mapping): 1:1 Server Mapping for lookup friendly 📥",
            "Protocol S-10 (Swift 6 Concurrency): Explicit Capture in TaskGroup Required 🏎️",
            "Protocol S-11 (Documentation): /// Doc Comments for all public methods 📝",
            "Protocol S-12 (Hierarchy): 📦 계층적 폴더 구조 준수 (protocol, model, enum, view, cell, endpoint, response)"
        ]
        return UNIT_RULES
