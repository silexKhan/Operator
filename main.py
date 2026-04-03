#
#  main.py - Operator (교환) Entry Point
#  Created by Gemini AIP on 2026. 03. 23. (Refactored)
#

import asyncio
import sys
import os

# [사용자] 프로젝트 루트를 sys.path에 추가하여 테넌트 모듈 로드 환경을 격리 및 최적화합니다. 
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from core.server import OperatorServer

async def main():
    """
    Operator (교환)의 최상위 진입점입니다.
    실제 서버 로직은 core.server.OperatorServer에 응집되어 있습니다. 
    """
    operator = OperatorServer()
    try:
        await operator.start_server_handler()
    except Exception as e:
        operator.logger.log(f" 교환 서버 실행 중 치명적 에러 발생: {str(e)}", 0)
        import traceback
        operator.logger.log(traceback.format_exc(), 1)
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())
