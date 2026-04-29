import { NextResponse } from "next/server";
import { listCircuitNames, readCircuitDetails, readSystemState } from "@/lib/operatorStore";

export async function GET() {
  try {
    const state = readSystemState();
    const circuits = listCircuitNames();
    const activeCircuit = circuits.includes(state.active_circuit) ? state.active_circuit : circuits[0] || "mcp";
    const activeCircuitDetails = circuits.includes(activeCircuit) ? readCircuitDetails(activeCircuit) : null;

    return NextResponse.json({
      ...state,
      active_circuit: activeCircuit,
      circuits,
      registered_circuits: circuits,
      active_circuit_details: activeCircuitDetails,
    });
  } catch (error) {
    console.error("[STATE_FETCH] Critical Error:", error);
    return NextResponse.json({ error: "Failed to read state" }, { status: 500 });
  }
}
