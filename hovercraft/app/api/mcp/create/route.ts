import { NextRequest, NextResponse } from "next/server";
import fs from "fs";
import path from "path";
import { getCircuitPath } from "@/lib/operatorPaths";
import { writeJsonFile } from "@/lib/operatorStore";

interface CreateCircuitRequest {
  name: string;
  data?: Record<string, unknown>;
}

export async function POST(req: NextRequest) {
  const { name, data = {} } = await req.json() as CreateCircuitRequest;

  try {
    const circuitPath = getCircuitPath(name);
    if (fs.existsSync(circuitPath)) {
      return NextResponse.json({ error: "Circuit already exists" }, { status: 400 });
    }

    const defaultSchema = {
      name: name.toLowerCase(),
      description: {
        ko: `${name} 회선입니다.`,
        en: `${name} circuit.`,
      },
      dependencies: [],
      units: ["markdown", "sentinel"],
      mission: {
        objective: { ko: "대기 중", en: "Standby" },
        criteria: [],
      },
    };

    fs.mkdirSync(circuitPath, { recursive: true });
    writeJsonFile(path.join(circuitPath, "overview.json"), { ...defaultSchema, ...data });
    writeJsonFile(path.join(circuitPath, "protocols.json"), { RULES: [] });

    return NextResponse.json({ success: true });
  } catch (error) {
    console.error("Failed to create circuit:", error);
    return NextResponse.json({ error: "Failed to create circuit" }, { status: 500 });
  }
}
