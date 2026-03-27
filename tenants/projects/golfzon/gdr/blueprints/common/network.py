#
#  network.py - Common Network Module Blueprint (GDR)
#

class NetworkSpec:
    NAME = "Common/Network"
    DESC = "앱 전체의 통신 및 SWR(Stale-While-Revalidate) 캐싱 엔진"
    PATH = "GDR/common/network"
    
    # --- [Core Architectural Flow] ---
    # UI/VM -> NetworkService.fetch -> [Cache Check] -> [Alamofire Request] -> [Cache Save] -> UI/VM
    CORE_FLOW = {
        "Request_Entry": "NetworkService.shared.fetch(endpoint:policy:) -> AsyncThrowingStream<FetchResult<T>, Error>",
        "SWR_Strategy": "1. If Policy is SWR, return Cache immediately (origin: .cache) -> 2. Fetch from Server (origin: .server)",
        "Abstraction": "Endpoint Protocol (URL, Method, AuthStrategy, CachingPolicy) -> AlamofireEngine"
    }
    
    # --- [Key Components] ---
    COMPONENTS = {
        "Service": {
            "class": "NetworkService",
            "desc": "SWR 오케스트레이터. 캐시와 서버 데이터를 스트림으로 결합하여 반환"
        },
        "Core": {
            "Endpoint": "API 요청 명세 프로토콜 (인증 위치, 캐싱 정책 포함)",
            "AuthStrategy": "GDR 전용 인증 전략 (HeaderProvider 연동)",
            "CachingPolicy": "캐시 유지 시간 및 갱신 전략 정의"
        },
        "Engine": {
            "class": "AlamofireEngine",
            "desc": "실제 HTTP 통신을 담당하는 Concrete Engine"
        },
        "Cache": {
            "class": "CacheManager",
            "desc": "T: Codable 데이터를 디스크/메모리에 저장하고 키 기반으로 관리"
        }
    }

    # --- [Data Structures] ---
    STRUCTURES = {
        "FetchResult<T>": "entity(T) + origin(.cache | .server) 조합",
        "DataOrigin": ".cache (Stale) | .server (Fresh)"
    }

    @classmethod
    def get_spec(cls):
        return {
            "name": cls.NAME,
            "desc": cls.DESC,
            "path": cls.PATH,
            "flow": cls.CORE_FLOW,
            "components": cls.COMPONENTS,
            "structures": cls.STRUCTURES
        }
