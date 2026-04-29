import { NextRequest, NextResponse } from "next/server";
import fs from "fs";
import { getCircuitPath } from "@/lib/operatorPaths";

export async function POST(req: NextRequest) {
  const { name } = await req.json() as { name?: string };
  if (!name) return NextResponse.json({ error: "Circuit name is required" }, { status: 400 });

  try {
    const circuitPath = getCircuitPath(name);
    if (!fs.existsSync(circuitPath)) {
      return NextResponse.json({ error: "Circuit not found" }, { status: 404 });
    }

    fs.rmSync(circuitPath, { recursive: true, force: true });
    return NextResponse.json({ success: true });
  } catch {
    return NextResponse.json({ error: "Failed to delete circuit" }, { status: 500 });
  }
}
