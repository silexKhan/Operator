import { NextResponse } from "next/server";
import { readRecentLogs } from "@/lib/operatorStore";

export async function GET() {
  try {
    return NextResponse.json({ logs: readRecentLogs(100) });
  } catch {
    return NextResponse.json({ error: "Failed to read logs" }, { status: 500 });
  }
}
