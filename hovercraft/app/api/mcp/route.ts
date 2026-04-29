import { NextResponse } from "next/server";
import { listCircuitNames, listUnitNames, readCircuitDetails } from "@/lib/operatorStore";

export async function GET(): Promise<Response> {
  try {
    const registeredCircuits = listCircuitNames();
    const activeUnits = listUnitNames();
    const circuitDetails = Object.fromEntries(
      registeredCircuits.map((name) => [name, readCircuitDetails(name)])
    );

    return NextResponse.json({
      registered_circuits: registeredCircuits,
      active_units: activeUnits,
      dependency_graph: {
        nodes: registeredCircuits.map((name) => ({ id: name, label: name.toUpperCase() })),
        links: [],
      },
      circuit_details: circuitDetails,
    });
  } catch (error) {
    console.error("Main Dashboard API Error:", error);
    return NextResponse.json({
      error: error instanceof Error ? error.message : "Discovery failed",
      registered_circuits: [],
      active_units: [],
      dependency_graph: { nodes: [], links: [] },
    }, { status: 500 });
  }
}
