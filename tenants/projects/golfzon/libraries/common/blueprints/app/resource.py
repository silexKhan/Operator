#
#  resource.py - Resource Management Module Blueprint (GolfzonCommon)
#

class ResourceSpec:
    NAME = "App/Resource"
    DESC = "원격 리소스(이미지, 영상, 설정 파일 등) 다운로드 및 파일 시스템 관리"
    PATH = "Sources/GolfzonCommon/app/resource"
    
    # --- [Core Architectural Flow] ---
    CORE_FLOW = {
        "1_Async_Download": "DownloadManager.shared.download(from:to:)를 통한 대기(Await) 기반 파일 획득",
        "2_Stream_Support": "AsyncStream을 이용한 다운로드 상태(progress, completed, failed) 실시간 수신",
        "3_Atomic_Move": "임시 디렉토리에 다운로드 후, 완료 시점에만 목적지 경로로 안전하게 이동(Overwrite)",
        "4_Error_Handling": "네트워크 단절, 파일 시스템 권한 부족 등 예외 상황에 대한 명확한 에러 반환"
    }
    
    # --- [Key Components] ---
    COMPONENTS = {
        "Manager": {
            "class": "DownloadManager",
            "desc": "Stateless한 설계를 가진 @unchecked Sendable 싱글톤 다운로드 엔진"
        },
        "State": {
            "enum": "DownloadState",
            "desc": "진행률(progress), 완료(completed), 실패(failed) 상태 정의"
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
