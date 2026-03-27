#
#  overview.py - MCP Project Summary
#

class Overview:
    PROJECT_DATA = {
        "project": "Silex MCP Hub",
        "path": "/Users/silex/workspace/private/MCP",
        "languages": ["Python 3.10+"],
        "domains": ["GDR", "Auth", "Nasmo", "Vision", "Common", "MCP"],
        "goal": "Recursive Axiom Enforcement Hub"
    }

    @classmethod
    def get_briefing(cls) -> dict:
        return cls.PROJECT_DATA
