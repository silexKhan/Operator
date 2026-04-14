import { NextRequest, NextResponse } from "next/server";
import fs from "fs";
import path from "path";

export async function POST(req: NextRequest) {
  const { target, name, data } = await req.json();
  const ROOT = path.join(process.cwd(), "..");

  try {
    if (target === "state") {
      const statePath = path.join(process.cwd(), "data", "state.json");
      const currentState = JSON.parse(fs.readFileSync(statePath, "utf-8"));
      fs.writeFileSync(statePath, JSON.stringify({ ...currentState, ...data }, null, 2));
    }

    if (target === "circuit_overview" && name) {
      const p = path.join(ROOT, "mcp_operator", "registry", "circuits", "registry", name, "overview.json");
      if (fs.existsSync(p)) fs.writeFileSync(p, JSON.stringify(data, null, 2));
    }

    if (target === "circuit_protocols" && name) {
      const p = path.join(ROOT, "mcp_operator", "registry", "circuits", "registry", name, "protocols.json");
      if (fs.existsSync(p)) fs.writeFileSync(p, JSON.stringify(data, null, 2));
    }

    if (target === "unit_protocols" && name) {
      const p = path.join(ROOT, "mcp_operator", "registry", "units", name, "protocols.json");
      if (fs.existsSync(p)) {
        const currentUnitData = JSON.parse(fs.readFileSync(p, "utf-8"));
        fs.writeFileSync(p, JSON.stringify({ ...currentUnitData, ...data }, null, 2));
      }
    }

    if (target === "global_protocols") {
      const p = path.join(ROOT, "mcp_operator", "engine", "protocols.json");
      if (fs.existsSync(p)) fs.writeFileSync(p, data);
    }

    if (target === "resource_monitor") {
      const p = path.join(ROOT, "data", "resource_monitor.json");
      fs.writeFileSync(p, JSON.stringify(data, null, 2));
    }

    return NextResponse.json({ success: true });
  } catch {
    return NextResponse.json({ error: "Failed to update" }, { status: 500 });
  }
}
