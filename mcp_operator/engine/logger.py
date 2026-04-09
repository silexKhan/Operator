#
#  logger.py - Operator (교환) FlowLogger
#

import time
import sys
import os
import asyncio
from datetime import datetime

class OperatorLogger:
    def __init__(self, category: str):
        self.category = category
        self.start_time = time.time()
        self._broadcast_handler = None
        
        # [통합 로그 경로 설정]
        self.log_dir = "/Users/silex/workspace/private/MCP/logs"
        self.log_file = os.path.join(self.log_dir, "server.log")
        
        # 로그 폴더 생성
        if not os.path.exists(self.log_dir):
            os.makedirs(self.log_dir, exist_ok=True)
            
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]
        start_msg = f" [{now}] [OPERATOR] [{self.category}] ▶ 서버 실행 (PID: {os.getpid()})"
        print(start_msg, file=sys.stderr)
        self._write_to_file(start_msg)

    def _write_to_file(self, message: str):
        """[Internal] 로그를 파일에 기록"""
        try:
            with open(self.log_file, "a", encoding="utf-8") as f:
                f.write(message + "\n")
        except Exception as e:
            print(f" [ERROR] 로그 기록 실패: {e}", file=sys.stderr)

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
            try:
                loop = asyncio.get_event_loop()
                if loop.is_running():
                    loop.create_task(self._broadcast_handler(packet))
            except: pass

    def log(self, message: str, indent: int = 0):
        prefix = "   " * (indent + 1) + "├─ "
        now = datetime.now().strftime("%H:%M:%S.%f")[:-3]
        full_msg = f" [{now}] [OPERATOR] [{self.category}] {prefix}{message}"
        print(full_msg, file=sys.stderr)
        self._write_to_file(full_msg)
        self._broadcast("INFO", message)

    def end(self, message: str = "완료"):
        duration = time.time() - self.start_time
        now = datetime.now().strftime("%H:%M:%S.%f")[:-3]
        end_msg = f" [{now}] [OPERATOR] [{self.category}]  {message} ({duration:.2f}s)"
        print(end_msg, file=sys.stderr)
        self._write_to_file(end_msg)
        self._broadcast("END", f"{message} ({duration:.2f}s)")
