import { NextRequest, NextResponse } from "next/server";
import fs from "fs";
import path from "path";

export async function POST(req: NextRequest) {
  const { name, data = {} } = await req.json();
  
  // 필수 스키마 정의
  const defaultSchema = {
    name: name,
    description: {
      ko: `${name} 회선입니다.`,
      en: `${name} circuit.`
    },
    dependencies: [],
    units: ["markdown", "sentinel"],
    mission: {
      objective: { ko: "대기 중", en: "Standby" },
      criteria: []
    }
  };

  const finalData = { ...defaultSchema, ...data };
  const circuitPath = path.join(process.cwd(), "..", "mcp_operator", "registry", "circuits", "registry", name);
  
  try {
    if (!fs.existsSync(circuitPath)) {
      fs.mkdirSync(circuitPath, { recursive: true });
    }
    
    fs.writeFileSync(path.join(circuitPath, "overview.json"), JSON.stringify(finalData, null, 2));
    fs.writeFileSync(path.join(circuitPath, "protocols.json"), JSON.stringify({ RULES: [] }, null, 2));
    
    // state.json 업데이트하여 SSE 트리거
    const statePath = path.join(process.cwd(), "data", "state.json");
    if (fs.existsSync(statePath)) {
      const state = JSON.parse(fs.readFileSync(statePath, "utf-8"));
      if (!state.circuits) state.circuits = [];
      if (!state.circuits.includes(name)) {
        state.circuits.push(name);
        fs.writeFileSync(statePath, JSON.stringify(state, null, 2));
      }
    }
    
    return NextResponse.json({ success: true });
  } catch (error) {
    console.error(error);
    return NextResponse.json({ error: "Failed to create circuit" }, { status: 500 });
  }
}
