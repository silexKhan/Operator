#
#  crypto.py - Crypto Module Blueprint (GolfzonCommon)
#

class CryptoSpec:
    NAME = "Utils/Crypto"
    DESC = "데이터 보안을 위한 암호화 및 복호화 유틸리티 (AES, HMAC, XOR)"
    PATH = "Sources/GolfzonCommon/utils/crypto"
    
    # --- [Core Architectural Flow] ---
    CORE_FLOW = {
        "1_Abstraction": "CryptoManager를 통해 다양한 암호화 알고리즘에 대한 통합 인터페이스 제공",
        "2_AES_Standard": "대칭키 암호화(AES-256)를 통한 민감 데이터 로컬 저장 및 통신 보안",
        "3_Integrity": "HMAC을 이용한 메시지 변조 방지 및 무결성 검증",
        "4_Lightweight": "XOR 알고리즘을 통한 저사양/고속 데이터 마스킹 지원"
    }
    
    # --- [Key Components] ---
    COMPONENTS = {
        "Manager": {
            "class": "CryptoManager",
            "desc": "알고리즘별 구현체(AESCrypto, HMACCrypto 등)를 오케스트레이션"
        },
        "Support": {
            "AESCrypto": "CommonCrypto 기반의 AES 구현",
            "HMACCrypto": "키 기반 해시 인증 코드 생성",
            "XORCrypto": "단순 비트 연산 기반 마스킹"
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
