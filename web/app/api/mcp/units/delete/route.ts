import { NextResponse } from 'next/server';
import fs from 'fs';
import path from 'path';

/**
 * [사용자] 지휘소에 등록된 전문 기술 유닛(Unit) 부대를 영구 해체합니다. 
 * 물리적 디렉토리를 삭제하므로 복구가 불가능합니다. (MCP 유닛은 보호됨)
 */
export async function POST(request: Request): Promise<Response> {
  try {
    const { name } = await request.json();
    if (!name) return NextResponse.json({ error: 'Unit name is required' }, { status: 400 });

    const unitName = name.toLowerCase();
    
    // [중요] MCP, Python, Swift 등 핵심 유닛 보호 
    if (['mcp', 'python', 'swift', 'markdown'].includes(unitName)) {
      return NextResponse.json({ error: '보호된 핵심 유닛은 해체할 수 없습니다.' }, { status: 403 });
    }

    const unitsRoot = process.env.MCP_ROOT ? path.join(process.env.MCP_ROOT, 'units') : path.join(process.cwd(), '..', 'units');
    const unitPath = path.join(unitsRoot, unitName);

    if (!fs.existsSync(unitPath)) {
      return NextResponse.json({ error: 'Unit not found' }, { status: 404 });
    }

    // 물리적 디렉토리 및 파일 일괄 삭제 
    fs.rmSync(unitPath, { recursive: true, force: true });

    return NextResponse.json({ success: true, message: `Unit '${name}' decommissioned successfully` });
  } catch (error) {
    console.error('Failed to delete unit:', error);
    return NextResponse.json({ error: 'Internal Server Error' }, { status: 500 });
  }
}
