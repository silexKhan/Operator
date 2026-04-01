import { NextResponse } from 'next/server';
import fs from 'fs';
import path from 'path';

/**
 * [사용자] 지휘소에 새로운 전문 기술 유닛(Unit) 부대를 물리적으로 창설합니다. 
 * 디렉토리와 기본 프로토콜/감사기 템플릿을 자동 생성합니다.
 */
export async function POST(request: Request): Promise<Response> {
  try {
    const { name } = await request.json();
    if (!name) return NextResponse.json({ error: 'Unit name is required' }, { status: 400 });

    const unitsRoot = process.env.MCP_ROOT ? path.join(process.env.MCP_ROOT, 'units') : path.join(process.cwd(), '..', 'units');
    const newUnitPath = path.join(unitsRoot, name.toLowerCase());

    if (fs.existsSync(newUnitPath)) {
      return NextResponse.json({ error: 'Unit already exists' }, { status: 400 });
    }

    // 1. 디렉토리 창설 
    fs.mkdirSync(newUnitPath, { recursive: true });

    // 2. 기본 프로토콜 JSON 생성 (protocols.json)
    const protocolsData = {
      OVERVIEW: `${name.toUpperCase()} 전문 기술 유닛을 위한 독자적인 프로토콜입니다. `,
      RULES: [
        `Protocol ${name.charAt(0).toUpperCase()}-1 (Identity): ${name.toUpperCase()} 유닛의 전문성을 유지한다.`,
        `Protocol ${name.charAt(0).toUpperCase()}-2 (Compliance): 해당 기술 스택의 표준 규격을 준수한다.`
      ]
    };
    fs.writeFileSync(path.join(newUnitPath, 'protocols.json'), JSON.stringify(protocolsData, null, 2), 'utf-8');

    // 3. 기본 감사기 템플릿 (auditor.py) 
    const auditorTemplate = `#
#  auditor.py - ${name.toUpperCase()} Unit Code Auditor
#

import os
from core.interfaces import BaseAuditor

class ${name.charAt(0).toUpperCase() + name.slice(1)}Auditor(BaseAuditor):
    def audit(self, file_path: str, content: str) -> list[str]:
        results = []
        self.log(f"${name.toUpperCase()} 유닛 프로토콜 감사 시작 - 파일: {os.path.basename(file_path)}", 1)

        # [사용자] 여기에 ${name.toUpperCase()} 유닛 전용 정밀 진단 로직을 추가하십시오. 

        if not results:
            results.append(f" PASS: ${name.toUpperCase()} 유닛의 모든 프로토콜을 준수함.")

        return results
`;

    // 파일 물리적 기록 
    fs.writeFileSync(path.join(newUnitPath, 'auditor.py'), auditorTemplate);
    // 패키지 인식을 위한 __init__.py 추가
    fs.writeFileSync(path.join(newUnitPath, '__init__.py'), '');

    return NextResponse.json({ success: true, message: `Unit '${name}' created successfully` });
  } catch (error) {
    console.error('Failed to create unit:', error);
    return NextResponse.json({ error: 'Internal Server Error' }, { status: 500 });
  }
}
