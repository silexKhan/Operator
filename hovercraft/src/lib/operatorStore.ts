import fs from "fs";
import path from "path";
import {
  AuditLog,
  CircuitDetails,
  CircuitOverview,
  I18nText,
  Mission,
  ProtocolFile,
  ProtocolRule,
  SystemState,
  Unit,
} from "@/types/mcp";
import {
  assertSafeName,
  getCircuitPath,
  getCircuitsRegistryPath,
  getGlobalProtocolsPath,
  getLogsPath,
  getMissionPath,
  getStatePath,
  getUnitPath,
  getUnitsRegistryPath,
} from "@/lib/operatorPaths";

type JsonObject = Record<string, unknown>;

function isObject(value: unknown): value is JsonObject {
  return typeof value === "object" && value !== null && !Array.isArray(value);
}

function stringValue(value: unknown, fallback = ""): string {
  return typeof value === "string" ? value : fallback;
}

function readJsonObject(filePath: string): JsonObject {
  return readJsonFile<JsonObject>(filePath, {});
}

function normalizeRules(data: unknown): ProtocolRule[] {
  if (Array.isArray(data)) {
    return data.filter((item): item is ProtocolRule => typeof item === "string" || isObject(item));
  }
  return [];
}

function normalizeUnits(units: unknown): Unit[] {
  if (!Array.isArray(units)) return [];
  return units
    .map((unit): Unit | null => {
      if (typeof unit === "string") return { name: unit };
      if (isObject(unit) && typeof unit.name === "string") return { name: unit.name };
      return null;
    })
    .filter((unit): unit is Unit => unit !== null);
}

function normalizeMission(value: unknown): Mission | undefined {
  if (!isObject(value)) return undefined;
  return {
    objective: typeof value.objective === "string" || isObject(value.objective) ? value.objective as Mission["objective"] : "",
    criteria: Array.isArray(value.criteria) ? value.criteria as Mission["criteria"] : [],
  };
}

function normalizeOverview(value: unknown, fallbackName: string): CircuitOverview {
  const data = isObject(value) ? value : {};
  return {
    ...data,
    name: stringValue(data.name, fallbackName),
    description: data.description as I18nText | undefined,
    dependencies: Array.isArray(data.dependencies) ? data.dependencies.filter((item): item is string => typeof item === "string") : [],
    units: Array.isArray(data.units) ? data.units.filter((item): item is string => typeof item === "string") : [],
    mission: normalizeMission(data.mission),
  };
}

export function readJsonFile<T>(filePath: string, fallback: T): T {
  if (!fs.existsSync(filePath)) return fallback;
  try {
    return JSON.parse(fs.readFileSync(filePath, "utf-8")) as T;
  } catch {
    return fallback;
  }
}

export function writeJsonFile<T>(filePath: string, data: T): void {
  fs.mkdirSync(path.dirname(filePath), { recursive: true });
  fs.writeFileSync(filePath, JSON.stringify(data, null, 2), "utf-8");
}

export function listCircuitNames(): string[] {
  const registryPath = getCircuitsRegistryPath();
  if (!fs.existsSync(registryPath)) return [];
  return fs.readdirSync(registryPath)
    .filter((name) => {
      const fullPath = path.join(registryPath, name);
      return fs.statSync(fullPath).isDirectory() && !name.startsWith(".") && name !== "__pycache__";
    })
    .sort();
}

export function listUnitNames(): string[] {
  const registryPath = getUnitsRegistryPath();
  if (!fs.existsSync(registryPath)) return [];
  return fs.readdirSync(registryPath)
    .filter((name) => {
      const fullPath = path.join(registryPath, name);
      return fs.statSync(fullPath).isDirectory() && !name.startsWith(".") && name !== "__pycache__";
    })
    .sort();
}

export function readSystemState(): SystemState {
  const state = readJsonObject(getStatePath());
  const activeCircuit = stringValue(state.active_circuit, stringValue(state.active_circuit_override, "mcp")).toLowerCase();
  const lang = state.lang === "en" ? "en" : "ko";
  return {
    active_circuit: activeCircuit,
    current_path: stringValue(state.current_path),
    lang,
  };
}

export function writeSystemState(next: Partial<SystemState>): SystemState {
  const current = readSystemState();
  const merged: SystemState = {
    active_circuit: (next.active_circuit || current.active_circuit || "mcp").toLowerCase(),
    current_path: next.current_path ?? current.current_path ?? "",
    lang: next.lang === "en" || next.lang === "ko" ? next.lang : current.lang,
  };
  writeJsonFile(getStatePath(), merged);
  return merged;
}

export function readProtocolFile(filePath: string): ProtocolFile {
  return readJsonFile<ProtocolFile>(filePath, { RULES: [] });
}

export function readCircuitDetails(name: string): CircuitDetails {
  const safeName = assertSafeName(name.toLowerCase());
  const circuitPath = getCircuitPath(safeName);
  const overview = normalizeOverview(readJsonFile<unknown>(path.join(circuitPath, "overview.json"), {}), safeName);
  const protocolFile = readProtocolFile(path.join(circuitPath, "protocols.json"));
  const protocols = normalizeRules(protocolFile.RULES || protocolFile.protocols || protocolFile.rules);
  const mission = overview.mission || normalizeMission(readJsonFile<unknown>(getMissionPath(), {}));
  const units = normalizeUnits(overview.units);

  return {
    name: overview.name || safeName,
    description: overview.description,
    overview,
    protocols,
    units,
    actions: [],
    mission,
    audit_logs: [],
  };
}

export function readUnitProtocols(name: string): { overview: unknown; protocols: ProtocolRule[] } {
  const unitPath = getUnitPath(name);
  const data = readProtocolFile(path.join(unitPath, "protocols.json"));
  return {
    overview: data.OVERVIEW || {},
    protocols: normalizeRules(data.RULES || data.protocols || data.rules),
  };
}

export function writeUnitProtocols(name: string, rules: ProtocolRule[]): void {
  const unitPath = getUnitPath(name);
  const protocolsPath = path.join(unitPath, "protocols.json");
  const current = readProtocolFile(protocolsPath);
  writeJsonFile(protocolsPath, { ...current, RULES: rules });
}

export function readGlobalProtocols(): { data: unknown; content: string } | null {
  const protocolsPath = getGlobalProtocolsPath();
  if (!fs.existsSync(protocolsPath)) return null;
  const content = fs.readFileSync(protocolsPath, "utf-8");
  return { data: readJsonFile<unknown>(protocolsPath, {}), content };
}

export function writeGlobalProtocols(data: unknown): void {
  const content = typeof data === "string" ? data : JSON.stringify(data, null, 2);
  fs.writeFileSync(getGlobalProtocolsPath(), content, "utf-8");
}

export function readRecentLogs(limit = 100): AuditLog[] {
  const logPath = getLogsPath();
  if (!fs.existsSync(logPath)) return [];
  return fs.readFileSync(logPath, "utf-8")
    .split("\n")
    .filter((line) => line.trim())
    .slice(-limit)
    .map((line) => {
      if (line.includes(" - ")) {
        const parts = line.split(" - ");
        return { timestamp: parts[0], message: parts.slice(1).join(" - "), level: "INFO", category: "ENGINE" };
      }
      return { timestamp: new Date().toISOString(), message: line, level: "INFO", category: "ENGINE" };
    });
}
