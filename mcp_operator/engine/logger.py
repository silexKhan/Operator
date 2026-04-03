#
#  logger.py - Operator (교환) FlowLogger
#

import time
import sys
import asyncio
from datetime import datetime

class OperatorLogger:
    def __init__(self, category: str):
        self.category = category
        self.start_time = time.time()
        self._broadcast_handler = None
        now = datetime.now().strftime("%H:%M:%S.%f")[:-3]
        print(f" [{now}] [OPERATOR] [{self.category}] ▶ 시작", file=sys.stderr)

    def set_broadcast_handler(self, handler):
        """웹소켓 전송용 핸들러 등록"""
        self._broadcast_handler = handler

    def _broadcast(self, level: str, message: str):
        """[Internal] 웹소켓으로 로그 전송 (비동기 처리)"""
        if self._broadcast_handler:
            packet = {
                "type": "LOG",
                "timestamp": datetime.now().isoformat(),
                "category": self.category,
                "level": level,
                "message": message
            }
            # 비동기 함수를 동기 맥락에서 호출하기 위해 이벤트 루프 활용
            try:
                loop = asyncio.get_event_loop()
                if loop.is_running():
                    loop.create_task(self._broadcast_handler(packet))
            except: pass

    def log(self, message: str, indent: int = 0):
        prefix = "   " * (indent + 1) + "├─ "
        now = datetime.now().strftime("%H:%M:%S.%f")[:-3]
        print(f" [{now}] [OPERATOR] [{self.category}] {prefix}{message}", file=sys.stderr)
        self._broadcast("INFO", message)

    def end(self, message: str = "완료"):
        duration = time.time() - self.start_time
        now = datetime.now().strftime("%H:%M:%S.%f")[:-3]
        print(f" [{now}] [OPERATOR] [{self.category}]  {message} ({duration:.2f}s)", file=sys.stderr)
        self._broadcast("END", f"{message} ({duration:.2f}s)")
