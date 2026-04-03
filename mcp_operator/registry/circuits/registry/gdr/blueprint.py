#  blueprint.py - GDR 회선 동적 설계도 및 스펙 인덱서
class BluePrint:
    def __init__(self):
        self.data = {
            "flow": {
                "Data": "Web-Bridge (JS) -> Native-Auditor (Swift) -> ViewModel -> Protocol Guard",
                "Domain": "GDR Golf Engine",
                "Spec_Mode": "Active"
            },
            "spec_index": {
                "mission_overview.md": "[GDR] 프로젝트 알파 미션 명세"
            }
        }
    def get_structure(self): return self.data
