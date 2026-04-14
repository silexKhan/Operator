import { NextRequest, NextResponse } from "next/server";
import fs from "fs";
import path from "path";

export async function POST(req: NextRequest) {
  const { name, data } = await req.json();
  // eslint-disable-next-line @typescript-eslint/no-unused-vars
  const { role, inherit_global, ...cleanData } = data;

  const circuitPath = path.join(process.cwd(), "..", "mcp_operator", "registry", "circuits", "registry", name);
  
  try {
    if (!fs.existsSync(circuitPath)) {
      fs.mkdirSync(circuitPath, { recursive: true });
    }
    
    fs.writeFileSync(path.join(circuitPath, "overview.json"), JSON.stringify(cleanData, null, 2));
    fs.writeFileSync(path.join(circuitPath, "protocols.json"), JSON.stringify({ RULES: [] }, null, 2));
    
    return NextResponse.json({ success: true });
  } catch (error) {
    console.error(error);
    return NextResponse.json({ error: "Failed to create circuit" }, { status: 500 });
  }
}
