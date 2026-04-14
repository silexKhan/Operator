import { NextRequest, NextResponse } from "next/server";
import fs from "fs";
import path from "path";

export async function POST(req: NextRequest) {
  const { unit, file_path } = await req.json();
  
  try {
    const auditorPath = path.join(process.cwd(), "..", "mcp_operator", "registry", "units", unit, "auditor.py");
    
    if (fs.existsSync(auditorPath)) {
      // Mock result for UI testing
      return NextResponse.json({ 
        status: "SUCCESS", 
        results: [`Audited ${file_path} with ${unit} unit.`] 
      });
    }
    
    return NextResponse.json({ error: "Auditor not found" }, { status: 404 });
  } catch {
    return NextResponse.json({ error: "Failed to run audit" }, { status: 500 });
  }
}
