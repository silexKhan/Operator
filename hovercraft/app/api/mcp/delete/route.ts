import { NextRequest, NextResponse } from "next/server";
import fs from "fs";
import path from "path";

export async function POST(req: NextRequest) {
  const { name } = await req.json();
  const circuitPath = path.join(process.cwd(), "..", "mcp_operator", "registry", "circuits", "registry", name);
  
  try {
    if (fs.existsSync(circuitPath)) {
      fs.rmSync(circuitPath, { recursive: true, force: true });
      
      // state.json 업데이트하여 SSE 트리거
      const statePath = path.join(process.cwd(), "data", "state.json");
      if (fs.existsSync(statePath)) {
        const state = JSON.parse(fs.readFileSync(statePath, "utf-8"));
        if (state.circuits) {
          state.circuits = state.circuits.filter((c: string) => c !== name);
          fs.writeFileSync(statePath, JSON.stringify(state, null, 2));
        }
      }
      
      return NextResponse.json({ success: true });
    }
    return NextResponse.json({ error: "Circuit not found" }, { status: 404 });
  } catch {
    return NextResponse.json({ error: "Failed to delete circuit" }, { status: 500 });
  }
}
