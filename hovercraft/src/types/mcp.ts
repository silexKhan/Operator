export interface Unit {
  name: string;
  mission: string | { ko: string; en: string };
  rules: (string | { ko: string; en: string })[];
}

export interface Action {
  name: string;
  description: string;
}

export interface Mission {
  objective: string | { [key: string]: string };
  criteria: (string | { [key: string]: string })[];
}

export interface CircuitDetails {
  name: string;
  description?: string | { [key: string]: string };
  protocols: string[] | { RULES: string[] };
  global_protocols?: {
    title: string;
    rules: string[];
  };
  units: Unit[];
  actions: Action[];
  mission?: Mission;
  audit_logs?: AuditLog[];
}

export interface SystemStatus {
  active_circuit: string;
  circuits: string[];
  details?: CircuitDetails;
}

export interface AuditLog {
  timestamp: string;
  level: string;
  message: string;
  category: string;
  status?: 'PASS' | 'VIOLATION' | 'WARNING';
  rule_id?: string;
}

export interface LogEntry {
  timestamp: string;
  level: string;
  message: string;
  category: string;
}

export interface Thresholds {
  cpu: number;
  mem: number;
}
