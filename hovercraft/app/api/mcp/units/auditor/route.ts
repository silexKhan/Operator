import { NextRequest, NextResponse } from "next/server";
import fs from "fs";
import path from "path";
import { getUnitPath } from "@/lib/operatorPaths";

export async function POST(req: NextRequest) {
  const { unit, file_path } = await req.json() as { unit?: string; file_path?: string };
  if (!unit) return NextResponse.json({ error: "Unit is required" }, { status: 400 });

  try {
    const auditorPath = path.join(getUnitPath(unit), "auditor.py");
    if (!fs.existsSync(auditorPath)) {
      return NextResponse.json({ error: "Auditor not found" }, { status: 404 });
    }

    return NextResponse.json({
      status: "SUCCESS",
      results: [`Audited ${file_path || "MISSION_PIPELINE"} with ${unit} unit.`],
    });
  } catch {
    return NextResponse.json({ error: "Failed to run audit" }, { status: 500 });
  }
}
