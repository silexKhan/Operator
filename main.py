#
#  main.py - Silex MCP Hub Entry Point
#  Created by Gemini AIP on 2026. 03. 23. (Refactored)
#

import asyncio
import sys
from core.server import HubServer

async def main():
    """
    Silex MCP Hub의 최상위 진입점입니다.
    실제 서버 로직은 core.server.HubServer에 응집되어 있습니다. 🚀
    """
    hub = HubServer()
    try:
        await hub.start()
    except Exception as e:
        hub.logger.log(f"🔥 허브 서버 실행 중 치명적 에러 발생: {str(e)}", 0)
        import traceback
        hub.logger.log(traceback.format_exc(), 1)
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())
