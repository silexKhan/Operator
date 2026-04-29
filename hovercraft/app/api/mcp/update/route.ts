import { NextRequest, NextResponse } from "next/server";
import path from "path";
import { getCircuitPath, getUnitPath } from "@/lib/operatorPaths";
import {
  readCircuitDetails,
  readJsonFile,
  writeGlobalProtocols,
  writeJsonFile,
  writeSystemState,
  writeUnitProtocols,
} from "@/lib/operatorStore";
import { CircuitOverview, ProtocolRule, SystemState } from "@/types/mcp";

interface UpdateRequest {
  target: string;
  name?: string;
  data?: unknown;
}

function isRecord(value: unknown): value is Record<string, unknown> {
  return typeof value === "object" && value !== null && !Array.isArray(value);
}

function readRules(data: unknown): ProtocolRule[] {
  if (!isRecord(data)) return [];
  const rawRules = data.rules || data.RULES || [];
  return Array.isArray(rawRules)
    ? rawRules.filter((rule): rule is ProtocolRule => typeof rule === "string" || isRecord(rule))
    : [];
}

export async function POST(req: NextRequest) {
  const { target, name, data } = await req.json() as UpdateRequest;

  try {
    if (target === "state") {
      const stateData = isRecord(data) ? data as Partial<SystemState> : {};
      return NextResponse.json({ success: true, state: writeSystemState(stateData) });
    }

    if ((target === "overview" || target === "circuit_overview") && name) {
      const overviewPath = path.join(getCircuitPath(name), "overview.json");
      const current = readJsonFile<CircuitOverview>(overviewPath, readCircuitDetails(name).overview || { name });
      const next = isRecord(data) ? { ...current, ...data } : current;
      writeJsonFile(overviewPath, next);
      return NextResponse.json({ success: true });
    }

    if (target === "circuit_units" && name) {
      const overviewPath = path.join(getCircuitPath(name), "overview.json");
      const current = readJsonFile<CircuitOverview>(overviewPath, readCircuitDetails(name).overview || { name });
      const units = isRecord(data) && Array.isArray(data.units)
        ? data.units.filter((unit): unit is string => typeof unit === "string")
        : [];
      writeJsonFile(overviewPath, { ...current, units });
      return NextResponse.json({ success: true });
    }

    if ((target === "protocol" || target === "circuit_protocols") && name) {
      const protocolsPath = path.join(getCircuitPath(name), "protocols.json");
      writeJsonFile(protocolsPath, { RULES: readRules(data) });
      return NextResponse.json({ success: true });
    }

    if (target === "unit_protocols" && name) {
      if (isRecord(data) && Array.isArray(data.RULES || data.rules)) {
        writeUnitProtocols(name, readRules(data));
      } else {
        const protocolsPath = path.join(getUnitPath(name), "protocols.json");
        const current = readJsonFile<Record<string, unknown>>(protocolsPath, {});
        writeJsonFile(protocolsPath, isRecord(data) ? { ...current, ...data } : current);
      }
      return NextResponse.json({ success: true });
    }

    if (target === "global_protocols") {
      writeGlobalProtocols(data);
      return NextResponse.json({ success: true });
    }

    return NextResponse.json({ error: `Unsupported update target: ${target}` }, { status: 400 });
  } catch (error) {
    console.error("Update Error:", error);
    return NextResponse.json({ error: "Failed to update physical storage" }, { status: 500 });
  }
}
