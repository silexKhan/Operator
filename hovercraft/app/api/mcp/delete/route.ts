import { NextRequest, NextResponse } from "next/server";
import fs from "fs";
import path from "path";

export async function POST(req: NextRequest) {
  const { name } = await req.json();
  const circuitPath = path.join(process.cwd(), "..", "mcp_operator", "registry", "circuits", "registry", name);
  
  try {
    if (fs.existsSync(circuitPath)) {
      fs.rmSync(circuitPath, { recursive: true, force: true });
      return NextResponse.json({ success: true });
    }
    return NextResponse.json({ error: "Circuit not found" }, { status: 404 });
  } catch {
    return NextResponse.json({ error: "Failed to delete circuit" }, { status: 500 });
  }
}
