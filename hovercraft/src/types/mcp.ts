export type I18nText = string | { [key: string]: string | undefined };
export type ProtocolRule = string | { [key: string]: string };

export interface Unit {
  name: string;
  path?: string;
  mission?: I18nText;
  rules?: ProtocolRule[];
}

export interface Action {
  name: string;
  description: string;
}

export interface Mission {
  objective: I18nText;
  criteria: ProtocolRule[];
}

export interface CircuitOverview {
  name: string;
  description?: I18nText;
  dependencies?: string[];
  units?: string[];
  mission?: Mission;
  [key: string]: unknown;
}

export interface ProtocolFile {
  OVERVIEW?: unknown;
  RULES?: ProtocolRule[];
  rules?: ProtocolRule[];
  protocols?: ProtocolRule[];
}

export interface SystemState {
  active_circuit: string;
  current_path?: string;
  lang?: "ko" | "en";
}

export interface CircuitDetails {
  name: string;
  overview?: CircuitOverview | null;
  description?: I18nText;
  protocols: ProtocolRule[] | { RULES: ProtocolRule[] };
  global_protocols?: {
    title: string;
    rules: string[];
  };
  units: Unit[] | string[];
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
