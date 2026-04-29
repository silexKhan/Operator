import { NextRequest, NextResponse } from "next/server";
import {
  listCircuitNames,
  listUnitNames,
  readCircuitDetails,
  readGlobalProtocols,
  readUnitProtocols,
} from "@/lib/operatorStore";

export async function GET(req: NextRequest) {
  const { searchParams } = new URL(req.url);
  const type = searchParams.get("type");
  const name = searchParams.get("name");

  try {
    if (type === "units_list") {
      return NextResponse.json({ units: listUnitNames() });
    }

    if (type === "circuits_list") {
      return NextResponse.json({ circuits: listCircuitNames() });
    }

    if (type === "unit" && name) {
      return NextResponse.json(readUnitProtocols(name));
    }

    if (type === "circuit_full" && name) {
      return NextResponse.json(readCircuitDetails(name));
    }

    if (type === "global") {
      const globalProtocols = readGlobalProtocols();
      if (!globalProtocols) {
        return NextResponse.json({ error: "Global protocols file not found" }, { status: 404 });
      }
      return NextResponse.json({
        success: true,
        data: globalProtocols.data,
        content: globalProtocols.content,
      });
    }

    return NextResponse.json({ error: "Invalid type or missing parameters" }, { status: 400 });
  } catch (error) {
    console.error("Protocol Fetch Error:", error);
    return NextResponse.json({ error: "Internal Server Error" }, { status: 500 });
  }
}
