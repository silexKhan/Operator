import { NextResponse } from "next/server";
import { ProtocolRule } from "@/types/mcp";
import { readUnitProtocols, writeUnitProtocols } from "@/lib/operatorStore";

function normalizeRules(value: unknown): ProtocolRule[] {
  if (!Array.isArray(value)) return [];
  return value.filter((rule): rule is ProtocolRule => (
    typeof rule === "string" || (typeof rule === "object" && rule !== null && !Array.isArray(rule))
  ));
}

export async function GET(request: Request): Promise<Response> {
  const { searchParams } = new URL(request.url);
  const unitName = searchParams.get("unit");

  if (!unitName) return NextResponse.json({ error: "Unit name is required" }, { status: 400 });

  try {
    return NextResponse.json({ rules: readUnitProtocols(unitName).protocols });
  } catch (error) {
    console.error("Failed to read unit protocols:", error);
    return NextResponse.json({ error: "Failed to read unit protocols", rules: [] }, { status: 500 });
  }
}

export async function POST(request: Request): Promise<Response> {
  try {
    const { name, rules } = await request.json() as { name?: string; rules?: unknown };
    if (!name) return NextResponse.json({ error: "Invalid data" }, { status: 400 });

    writeUnitProtocols(name, normalizeRules(rules));
    return NextResponse.json({ success: true });
  } catch (error) {
    console.error("Failed to update unit protocols:", error);
    return NextResponse.json({ error: "Failed to update unit protocols" }, { status: 500 });
  }
}
