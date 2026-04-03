import os
import json
from datetime import datetime
from shared.utils import get_project_root

class HistoryLogger:
    """
    [사용자] 시스템의 핵심 이력(감사 차단, 미션 성공 등)을 SQLite 등 무거운 DB 없이 
    JSON Lines(.jsonl) 포맷으로 가볍게 영구 보존하는 매니저입니다.
    """
    def __init__(self):
        self.history_dir = os.path.join(get_project_root(), "history")
        self.audit_file = os.path.join(self.history_dir, "audit_logs.jsonl")
        self.mission_file = os.path.join(self.history_dir, "missions.jsonl")
        self._ensure_dir()

    def _ensure_dir(self):
        if not os.path.exists(self.history_dir):
            os.makedirs(self.history_dir, exist_ok=True)

    def log_audit(self, circuit: str, file_path: str, severity: str, message: str):
        """[사용자] 하네스에 의해 규약 위반으로 차단된 내역을 기록합니다."""
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "circuit": circuit,
            "file_path": file_path,
            "severity": severity,
            "message": message
        }
        self._append_to_file(self.audit_file, log_entry)

    def log_mission(self, objective: str, status: str, evidence: str):
        """[사용자] 센티널에 의한 미션 수행 결과를 기록합니다."""
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "objective": objective,
            "status": status,
            "evidence": evidence
        }
        self._append_to_file(self.mission_file, log_entry)

    def get_recent_audits(self, limit: int = 10) -> list[dict]:
        """[사용자] 최근 기록된 감사 이력을 파싱하여 반환합니다."""
        return self._read_recent_lines(self.audit_file, limit)

    def _append_to_file(self, path: str, data: dict):
        try:
            with open(path, "a", encoding="utf-8") as f:
                f.write(json.dumps(data, ensure_ascii=False) + "\n")
        except Exception:
            pass

    def _read_recent_lines(self, path: str, limit: int) -> list[dict]:
        if not os.path.exists(path):
            return []
        try:
            with open(path, "r", encoding="utf-8") as f:
                lines = f.readlines()
            return [json.loads(line.strip()) for line in lines[-limit:]]
        except Exception:
            return []

# 싱글톤 인스턴스 (Import용)
history_logger = HistoryLogger()
