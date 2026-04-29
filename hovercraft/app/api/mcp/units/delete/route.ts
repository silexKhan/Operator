import { NextResponse } from "next/server";
import fs from "fs";
import { getUnitPath } from "@/lib/operatorPaths";

const PROTECTED_UNITS = new Set(["python", "swift", "markdown", "sentinel", "planning"]);

export async function POST(request: Request): Promise<Response> {
  try {
    const { name } = await request.json() as { name?: string };
    if (!name) return NextResponse.json({ error: "Unit name is required" }, { status: 400 });

    const unitName = name.toLowerCase();
    if (PROTECTED_UNITS.has(unitName)) {
      return NextResponse.json({ error: "보호된 핵심 유닛은 해체할 수 없습니다." }, { status: 403 });
    }

    const unitPath = getUnitPath(unitName);
    if (!fs.existsSync(unitPath)) {
      return NextResponse.json({ error: "Unit not found" }, { status: 404 });
    }

    fs.rmSync(unitPath, { recursive: true, force: true });
    return NextResponse.json({ success: true, message: `Unit '${unitName}' decommissioned successfully` });
  } catch (error) {
    console.error("Failed to delete unit:", error);
    return NextResponse.json({ error: "Internal Server Error" }, { status: 500 });
  }
}
