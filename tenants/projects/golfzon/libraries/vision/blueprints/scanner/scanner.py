#
#  scanner.py - Scanner Module Blueprint (GolfzonVision)
#

class ScannerSpec:
    NAME = "Scanner"
    DESC = "QR 코드 및 바코드 인식을 위한 카메라 뷰 컨트롤러"
    PATH = "Sources/GolfzonVision"
    
    # --- [Core Architectural Flow] ---
    CORE_FLOW = {
        "1_Session_Start": "AVCaptureSession을 구성하여 카메라 프리뷰 시작",
        "2_Detection": "MetadataOutput을 통해 QR/Barcode 데이터 실시간 감지",
        "3_Vibration_Feedback": "인식 성공 시 햅틱/진동 피드백 제공 및 세션 중지",
        "4_Result_Callback": "인식된 데이터를 ScanCompletionModel에 담아 Delegate 또는 completion closure로 전달"
    }
    
    # --- [Key Components] ---
    COMPONENTS = {
        "QRCode": {
            "class": "QRCodeScanViewController",
            "desc": "QR 코드 스캔 특화 뷰 컨트롤러"
        },
        "Barcode": {
            "class": "BarcodeScanViewController",
            "desc": "바코드 스캔 특화 뷰 컨트롤러"
        },
        "Model": {
            "class": "ScanCompletionModel",
            "desc": "스캔 성공 시 반환되는 결과 데이터 구조체"
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
