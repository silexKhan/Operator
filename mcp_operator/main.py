#
#  main.py - Operator (교환) Entry Point
#  Created by Gemini AIP on 2026. 03. 23. (Refactored)
#

import asyncio
import sys
import os
import builtins

# [MCP Safety] 전역 print 함수를 가로채어 stderr로 보냅니다. 
# sys.stdout 자체를 덮어쓰지 않아 MCP 통신 채널(stdout)을 보존합니다.
def safe_print(*args, **kwargs):
    kwargs['file'] = sys.stderr
    builtins._original_print(*args, **kwargs)

if not hasattr(builtins, "_original_print"):
    builtins._original_print = builtins.print
    builtins.print = safe_print

# [사용자] 프로젝트 루트를 sys.path에 추가하여 테넌트 모듈 로드 환경을 격리 및 최적화합니다. 
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from mcp_operator.engine.server import OperatorServer

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
