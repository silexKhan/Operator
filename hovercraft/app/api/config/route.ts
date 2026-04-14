import { NextRequest, NextResponse } from "next/server";
import fs from "fs";
import path from "path";

export async function GET() {
  const configPath = path.join(process.cwd(), "config.json");
  try {
    if (fs.existsSync(configPath)) {
      return NextResponse.json(JSON.parse(fs.readFileSync(configPath, "utf-8")));
    }
    return NextResponse.json({ shipName: "NEBUCHADNEZZAR", captainName: "Morpheus" });
  } catch {
    return NextResponse.json({ error: "Failed to load config" }, { status: 500 });
  }
}

export async function POST(req: NextRequest) {
  const configPath = path.join(process.cwd(), "config.json");
  try {
    const data = await req.json();
    fs.writeFileSync(configPath, JSON.stringify(data, null, 2));
    return NextResponse.json({ success: true });
  } catch {
    return NextResponse.json({ error: "Failed to save config" }, { status: 500 });
  }
}
