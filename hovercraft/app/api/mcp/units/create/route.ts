import { NextResponse } from "next/server";
import fs from "fs";
import path from "path";
import { getUnitPath } from "@/lib/operatorPaths";
import { writeJsonFile } from "@/lib/operatorStore";

export async function POST(request: Request): Promise<Response> {
  try {
    const { name } = await request.json() as { name?: string };
    if (!name) return NextResponse.json({ error: "Unit name is required" }, { status: 400 });

    const unitName = name.toLowerCase();
    const newUnitPath = getUnitPath(unitName);

    if (fs.existsSync(newUnitPath)) {
      return NextResponse.json({ error: "Unit already exists" }, { status: 400 });
    }

    fs.mkdirSync(newUnitPath, { recursive: true });

    writeJsonFile(path.join(newUnitPath, "protocols.json"), {
      OVERVIEW: `${unitName.toUpperCase()} 전문 기술 유닛을 위한 독자적인 프로토콜입니다.`,
      RULES: [
        `Protocol ${unitName.charAt(0).toUpperCase()}-1 (Identity): ${unitName.toUpperCase()} 유닛의 전문성을 유지한다.`,
        `Protocol ${unitName.charAt(0).toUpperCase()}-2 (Compliance): 해당 기술 스택의 표준 규격을 준수한다.`,
      ],
    });

    const className = `${unitName.charAt(0).toUpperCase()}${unitName.slice(1)}Auditor`;
    const auditorTemplate = `#
#  auditor.py - ${unitName.toUpperCase()} Unit Code Auditor
#

import os
from mcp_operator.engine.interfaces import BaseAuditor

class ${className}(BaseAuditor):
    def __init__(self, logger=None, circuit_manager=None):
        super().__init__(logger)
        self.circuit_manager = circuit_manager

    def audit(self, file_path: str, content: str) -> list[str]:
        results = []
        if self.logger:
            self.logger.log(f"${unitName.toUpperCase()} 유닛 프로토콜 감사 시작 - 파일: {os.path.basename(file_path)}", 1)
        return results
`;

    fs.writeFileSync(path.join(newUnitPath, "auditor.py"), auditorTemplate, "utf-8");
    fs.writeFileSync(path.join(newUnitPath, "__init__.py"), "", "utf-8");

    return NextResponse.json({ success: true, message: `Unit '${unitName}' created successfully` });
  } catch (error) {
    console.error("Failed to create unit:", error);
    return NextResponse.json({ error: "Internal Server Error" }, { status: 500 });
  }
}
