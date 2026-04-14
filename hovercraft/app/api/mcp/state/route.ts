import { NextResponse } from "next/server";
import fs from "fs";
import path from "path";

export async function GET() {
  const statePath = path.join(process.cwd(), "data", "state.json");
  try {
    let state = { active_circuit: "mcp", circuits: ["research", "mcp", "gdr"], lang: "ko" };
    if (fs.existsSync(statePath)) {
      state = JSON.parse(fs.readFileSync(statePath, "utf-8"));
      console.log(`[STATE_FETCH] Loaded state from ${statePath}: active_circuit=${state.active_circuit}`);
    } else {
      console.warn(`[STATE_FETCH] state.json not found at ${statePath}, using fallback.`);
    }

    // 활성 회선의 상세 정보(details) 추가 로드
    const circuitPath = path.join(process.cwd(), "..", "mcp_operator", "registry", "circuits", "registry", state.active_circuit);
    const protocolsPath = path.join(circuitPath, "protocols.json");
    const overviewPath = path.join(circuitPath, "overview.json");

    const active_circuit_details: any = { protocols: [], overview: {} };
    if (fs.existsSync(protocolsPath)) {
      const data = JSON.parse(fs.readFileSync(protocolsPath, "utf-8"));
      active_circuit_details.protocols = data.RULES || data.protocols || [];
      console.log(`[STATE_FETCH] Loaded protocols for ${state.active_circuit}: ${active_circuit_details.protocols.length} rules found.`);
    } else {
      console.warn(`[STATE_FETCH] protocols.json not found for ${state.active_circuit} at ${protocolsPath}`);
    }

    if (fs.existsSync(overviewPath)) {
      active_circuit_details.overview = JSON.parse(fs.readFileSync(overviewPath, "utf-8"));
      // UI 호환성을 위해 units 정보를 객체 배열로 변환하여 최상위에 노출
      if (active_circuit_details.overview.units) {
        active_circuit_details.units = active_circuit_details.overview.units.map((u: string) => ({ name: u }));
      }
      active_circuit_details.name = active_circuit_details.overview.name;
      console.log(`[STATE_FETCH] Loaded overview for ${state.active_circuit}: ${active_circuit_details.overview.name}`);
    }

    return NextResponse.json({ ...state, active_circuit_details });
  } catch (error) {
    console.error("[STATE_FETCH] Critical Error:", error);
    return NextResponse.json({ error: "Failed to read state" }, { status: 500 });
  }
}
