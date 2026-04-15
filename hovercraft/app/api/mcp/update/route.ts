import { NextRequest, NextResponse } from "next/server";
import fs from "fs";
import path from "path";

export async function POST(req: NextRequest) {
  const { target, name, data } = await req.json();
  const ROOT = path.join(process.cwd(), "..");

  try {
    // 1. 시스템 상태 (state.json)
    if (target === "state") {
      const statePath = path.join(process.cwd(), "data", "state.json");
      const currentState = JSON.parse(fs.readFileSync(statePath, "utf-8"));
      fs.writeFileSync(statePath, JSON.stringify({ ...currentState, ...data }, null, 2));
    }

    // 2. 회선 개요 (overview.json) - UI target "overview" 처리
    if ((target === "overview" || target === "circuit_overview") && name) {
      const p = path.join(ROOT, "mcp_operator", "registry", "circuits", "registry", name, "overview.json");
      if (fs.existsSync(p)) {
        const currentData = JSON.parse(fs.readFileSync(p, "utf-8"));
        // UI에서 넘어온 data 구조에 따라 병합 (data 자체가 객체일 수도 있고, description만 있을 수도 있음)
        const updatedData = { ...currentData, ...(data.description ? data : data) };
        fs.writeFileSync(p, JSON.stringify(updatedData, null, 2));
      }
    }

    // 3. 회선 유닛 링크 관리 (overview.json 내 units 필드)
    if (target === "circuit_units" && name) {
      const p = path.join(ROOT, "mcp_operator", "registry", "circuits", "registry", name, "overview.json");
      if (fs.existsSync(p)) {
        const currentData = JSON.parse(fs.readFileSync(p, "utf-8"));
        currentData.units = data.units || [];
        fs.writeFileSync(p, JSON.stringify(currentData, null, 2));
      }
    }

    // 4. 회선 규약 (protocols.json) - UI target "protocol" 처리
    if ((target === "protocol" || target === "circuit_protocols") && name) {
      const p = path.join(ROOT, "mcp_operator", "registry", "circuits", "registry", name, "protocols.json");
      if (fs.existsSync(p)) {
        // UI에서는 { rules: [] } 또는 { RULES: [] } 형태로 보냄
        const rules = data.rules || data.RULES || [];
        fs.writeFileSync(p, JSON.stringify({ RULES: rules }, null, 2));
      }
    }

    // 5. 유닛 내부 규약 (unit protocols)
    if (target === "unit_protocols" && name) {
      const p = path.join(ROOT, "mcp_operator", "registry", "units", name, "protocols.json");
      if (fs.existsSync(p)) {
        const currentUnitData = JSON.parse(fs.readFileSync(p, "utf-8"));
        fs.writeFileSync(p, JSON.stringify({ ...currentUnitData, ...data }, null, 2));
      }
    }

    // 6. 글로벌 규약 (engine protocols)
    if (target === "global_protocols") {
      const p = path.join(ROOT, "mcp_operator", "engine", "protocols.json");
      if (fs.existsSync(p)) {
        // data가 문자열이면 그대로 쓰고, 객체면 stringify
        const content = typeof data === 'string' ? data : JSON.stringify(data, null, 2);
        fs.writeFileSync(p, content);
      }
    }

    return NextResponse.json({ success: true });
  } catch (error) {
    console.error("Update Error:", error);
    return NextResponse.json({ error: "Failed to update physical storage" }, { status: 500 });
  }
}
