#
#  master.py - Global System Architecture
#

class MasterFlow:
    """
    [대장님 🎯] 시스템 전체의 뼈대와 핵심 흐름
    """
    FLOW = {
        "Data": "Remote(API) -> SWR(Cache) -> ViewModel(Business Logic) -> View(Dumb)",
        "Navigation": "Splash -> Login -> MainDashboard -> (Practice / Nasmo / Challenge)"
    }
    
    GLOBAL_BINDINGS = {
        "UserSession": "LoginSuccess -> Store In UserSession(Singleton) -> Notify via NotificationCenter",
        "SensorData": "Socket Stream -> PracticeViewModel -> 60fps Real-time Rendering"
    }

    @classmethod
    def get_flow(cls):
        return {
            "flow": cls.FLOW,
            "bindings": cls.GLOBAL_BINDINGS
        }
