#
#  screenlogin.py - Screen Login Module Blueprint (GolfzonAuth)
#

class ScreenloginSpec:
    NAME = "ScreenLogin"
    DESC = "GDR/GS 스크린 로그인을 위한 통신 및 상태 관리 (MQTT, SocketIO)"
    PATH = "Sources/GolfzonAuth/screenlogin"
    
    # --- [Core Architectural Flow] ---
    CORE_FLOW = {
        "1_Routing": "ScreenLoginRouter를 통해 앱 종류(GDR/GS)에 따른 로그인 시스템 결정",
        "2_Connection": "AWS Iot Core(MQTT) 또는 SocketIO를 통해 스크린 장비와 실시간 세션 수립",
        "3_Authentication": "QR 코드 또는 번호 입력을 통한 장비 로그인 시도",
        "4_Event_Handling": "로그인 성공, 실패, 대기 등 장비로부터 수신되는 실시간 이벤트를 앱 UI로 전달",
        "5_Penalty_Check": "로그인 시도 실패 누적 등에 따른 Penalty 시스템 가동"
    }
    
    # --- [Key Components] ---
    COMPONENTS = {
        "Router": {
            "class": "ScreenLoginRouter",
            "desc": "GDR/GS 로그인 시스템 분기 및 진입점"
        },
        "GDR_Manager": {
            "class": "GDRScreenLoginManager",
            "desc": "AWS MQTT 기반의 GDR 전용 로그인 로직"
        },
        "GS_Manager": {
            "class": "GSScreenLoginManager",
            "desc": "SocketIO 기반의 GS 전용 로그인 로직"
        },
        "Modules": {
            "AWSMQTTService": "AWS IoT Core 연결 및 메시지 송수신",
            "SocketIOService": "Socket.io 클라이언트 구현"
        }
    }

    @classmethod
    def get_spec(cls):
        return {
            "name": cls.NAME,
            "desc": cls.DESC,
            "path": cls.PATH,
            "flow": cls.CORE_FLOW,
            "components": cls.COMPONENTS
        }
