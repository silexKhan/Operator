#
#  logger.py - Operator (교환) FlowLogger
#

import time
import sys
from datetime import datetime

class OperatorLogger:
    def __init__(self, category: str):
        self.category = category
        self.start_time = time.time()
        now = datetime.now().strftime("%H:%M:%S.%f")[:-3]
        print(f"🚀 [{now}] [OPERATOR] [{self.category}] ▶️ 시작", file=sys.stderr)

    def log(self, message: str, indent: int = 0):
        prefix = "   " * (indent + 1) + "├─ "
        now = datetime.now().strftime("%H:%M:%S.%f")[:-3]
        print(f"🚀 [{now}] [OPERATOR] [{self.category}] {prefix}{message}", file=sys.stderr)

    def end(self, message: str = "완료"):
        duration = time.time() - self.start_time
        now = datetime.now().strftime("%H:%M:%S.%f")[:-3]
        print(f"🚀 [{now}] [OPERATOR] [{self.category}] ✅ {message} ({duration:.2f}s)", file=sys.stderr)
