import { NextRequest, NextResponse } from "next/server";
import fs from "fs";
import path from "path";

export async function GET(req: NextRequest) {
  const { searchParams } = new URL(req.url);
  const type = searchParams.get("type");
  const name = searchParams.get("name");

  try {
    if (type === "units_list") {
      const unitsPath = path.join(process.cwd(), "..", "mcp_operator", "registry", "units");
      const units = fs.readdirSync(unitsPath).filter(f => fs.statSync(path.join(unitsPath, f)).isDirectory() && f !== "__pycache__");
      return NextResponse.json({ units });
    }

    if (type === "circuits_list") {
      const circuitsPath = path.join(process.cwd(), "..", "mcp_operator", "registry", "circuits", "registry");
      const circuits = fs.readdirSync(circuitsPath).filter(f => fs.statSync(path.join(circuitsPath, f)).isDirectory() && f !== "__pycache__");
      return NextResponse.json({ circuits });
    }

    if (type === "unit" && name) {
      const unitPath = path.join(process.cwd(), "..", "mcp_operator", "registry", "units", name, "protocols.json");
      if (fs.existsSync(unitPath)) {
        const data = JSON.parse(fs.readFileSync(unitPath, "utf-8"));
        return NextResponse.json({ overview: data.OVERVIEW || {}, protocols: data.RULES || data.protocols || [] });
      }
      // protocols.json이 없는 경우 기본 응답 반환 (Fallback)
      return NextResponse.json({ overview: { name, description: "No protocols found." }, protocols: [] });
    }

    if (type === "circuit_full" && name) {
      const circuitPath = path.join(process.cwd(), "..", "mcp_operator", "registry", "circuits", "registry", name);
      const overviewPath = path.join(circuitPath, "overview.json");
      const protocolsPath = path.join(circuitPath, "protocols.json");
      const res: { overview: any; protocols: any; units?: any; mission?: any } = { overview: null, protocols: [] };
      
      if (fs.existsSync(overviewPath)) {
        res.overview = JSON.parse(fs.readFileSync(overviewPath, "utf-8"));
        // UI 호환성을 위해 units 정보를 객체 배열로 변환하여 최상위에 노출
        if (res.overview.units) {
          res.units = res.overview.units.map((u: string) => ({ name: u }));
        }
      }

      if (fs.existsSync(protocolsPath)) {
        const pData = JSON.parse(fs.readFileSync(protocolsPath, "utf-8"));
        res.protocols = pData.RULES || pData.protocols || pData.rules || [];
      }

      // Mission data (Data Sanctuary)
      const missionPath = path.join(process.cwd(), "..", "data", "mission.json");
      if (fs.existsSync(missionPath)) res.mission = JSON.parse(fs.readFileSync(missionPath, "utf-8"));

      return NextResponse.json(res);
    }

    if (type === "global") {
      const globalPath = path.join(process.cwd(), "..", "mcp_operator", "engine", "protocols.json");
      if (fs.existsSync(globalPath)) {
        return NextResponse.json({ content: fs.readFileSync(globalPath, "utf-8") });
      }
    }

    return NextResponse.json({ error: "Invalid type or missing parameters" }, { status: 400 });
  } catch (error) {
    console.error("Protocol Fetch Error:", error);
    return NextResponse.json({ error: "Internal Server Error" }, { status: 500 });
  }
}
