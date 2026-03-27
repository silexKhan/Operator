#
#  auth.py - Auth Domain Specification
#

class AuthSpec:
    NAME = "Auth (Authentication)"
    DESC = "사용자 인증 및 세션 관리"
    PATH = "Sources/Auth"
    
    CORE_LOGIC = "AuthViewModel.transform(input: AuthInput) -> AuthOutput"
    INTERFACES = {
        "Input": ["loginTap(id:pw:)", "autoLoginCheck"],
        "Output": ["loginResult", "userInfo", "isProcessing"]
    }
    
    @classmethod
    def get_spec(cls):
        return {
            "name": cls.NAME,
            "desc": cls.DESC,
            "path": cls.PATH,
            "logic": cls.CORE_LOGIC,
            "interfaces": cls.INTERFACES
        }
