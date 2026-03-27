#
#  login.py - Login Module Blueprint (GDR)
#

class LoginSpec:
    NAME = "View/Login"
    DESC = "사용자 인증을 담당하는 로그인 모듈 (레거시 MVC 방식 ⚠️)"
    PATH = "GDR/view/login"
    
    # --- [Core Architectural Flow (Legacy MVC)] ---
    # Login (Entry) -> [Simple Login (Scheme)] OR [Manual Login (ID/PW)] OR [QR Login]
    CORE_FLOW = {
        "1_Entry_Animation": "Login.swift에서 Dissolve 애니메이션을 통해 브랜드 이미지 노출 및 로그인 수단 선택 제공",
        "2_Simple_Login": "golfzon5:// 앱 스킴을 호출하여 골프존 앱을 통한 간편 로그인 수행 (성공 시 exchangeAccessToken 호출)",
        "3_Manual_Login": "ManualLogin.swift에서 ID/PW 기반 인증 수행. 보안 강화를 위해 Captcha(이미지 인증) 로직 내장",
        "4_QR_Login": "QRLogin.swift에서 골프존 서비스 로그인을 위한 QR 코드 생성 및 상태 관리",
        "5_Session_Completion": "인증 성공 시 AuthManager.info()를 통해 전체 세션을 완성하고 PRIME.shared에 토큰 동기화 후 메인 이동"
    }
    
    # --- [Key Components] ---
    COMPONENTS = {
        "Main_Entry": {
            "class": "Login",
            "desc": "로그인 진입점. 뷰모델 없이 VC에서 직접 애니메이션 및 간편/수동 로그인 분기 처리"
        },
        "Manual_Login": {
            "class": "ManualLogin",
            "desc": "ID/PW 입력 및 캡차 인증 수행. TableView 기반의 레거시 입력 폼"
        },
        "QR_Login": {
            "class": "QRLogin",
            "desc": "QR 코드 기반 로그인 서비스 제공"
        }
    }

    # --- [Legacy Characteristics] ---
    CHARACTERISTICS = [
        "⚠️ No ViewModel: 비즈니스 로직이 ViewController에 밀집된 레거시 MVC 구조",
        "⚠️ Direct Action Handlers: 버튼 액션에서 직접 네트워크 요청 및 화면 전환 수행",
        "⚠️ Manual UI State: 캡차 노출 여부 등을 VC의 변수로 수동 관리"
    ]

    # --- [Special Logic] ---
    LOGIC = {
        "Captcha_Handling": "로그인 실패 시 서버 응답에 따라 캡차 모드를 활성화하고, 이미지 갱신 및 검증 로직 수행",
        "App_Scheme_Bridge": "mbsessionID 또는 accessToken을 URL 쿼리로 전달받아 즉시 세션을 구성하는 브릿지 로직 탑재",
        "Vision_Sync": "로그인 완료 즉시 PRIME.shared에 accessToken 및 sesssionID를 주입하여 웹뷰 기반 기능(Vision)과 세션 공유"
    }

    @classmethod
    def get_spec(cls):
        return {
            "name": cls.NAME,
            "desc": cls.DESC,
            "path": cls.PATH,
            "flow": cls.CORE_FLOW,
            "components": cls.COMPONENTS,
            "logic": cls.LOGIC
        }
