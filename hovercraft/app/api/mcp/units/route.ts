import { NextResponse } from "next/server";
import { listUnitNames } from "@/lib/operatorStore";

export async function GET(): Promise<Response> {
  try {
    const units = listUnitNames().map((name) => ({
      name,
      path: `units/${name}`,
    }));

    return NextResponse.json({ units });
  } catch (error) {
    console.error("Failed to scan units:", error);
    return NextResponse.json({ error: "Internal Server Error", units: [] }, { status: 500 });
  }
}
