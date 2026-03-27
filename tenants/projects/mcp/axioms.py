#
#  axioms.py - Python MCP Development Axioms
#

class Axioms:
    PROJECT_NAME = "Silex MCP Hub"
    PROJECT_ROOT = "/Users/silex/workspace/private/MCP"
    
    RULES = [
        "Axiom P1: Strict Type Hinting (No Any)",
        "Axiom P2: Pydantic Data Validation (Strict Schema)",
        "Axiom P3: Async/Await & Error Masking",
        "Axiom P4: Modular Tool Isolation (Single Responsibility)"
    ]

    @classmethod
    def get_summary(cls) -> dict:
        return {
            "name": cls.PROJECT_NAME,
            "rules": cls.RULES
        }
