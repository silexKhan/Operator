import { NextResponse } from 'next/server';
import fs from 'fs';
import path from 'path';

/**
 * [사용자] 특정 전문 유닛(Unit)의 독자적인 프로토콜을 읽고 수정합니다. 
 * 백엔드의 새로운 설계(protocols.json 기반)를 완벽히 준수하도록 개편되었습니다.
 */
export async function GET(request: Request): Promise<Response> {
  const { searchParams } = new URL(request.url);
  const unitName = searchParams.get('unit');
  
  if (!unitName) return NextResponse.json({ error: 'Unit name is required' }, { status: 400 });

  try {
    const protocolsJsonPath = process.env.MCP_ROOT ? path.join(process.env.MCP_ROOT, 'units', unitName.toLowerCase(), 'protocols.json') : path.join(process.cwd(), '..', 'units', unitName.toLowerCase(), 'protocols.json');
    
    // 1. JSON 파일이 존재하면 JSON에서 읽습니다. (신규 아키텍처)
    if (fs.existsSync(protocolsJsonPath)) {
      const content = fs.readFileSync(protocolsJsonPath, 'utf-8');
      const data = JSON.parse(content);
      return NextResponse.json({ rules: data.RULES || [] });
    }

    // 2. 하위 호환성 (Fallback): 구형 protocols.py 파일 파싱
    const protocolsPyPath = process.env.MCP_ROOT ? path.join(process.env.MCP_ROOT, 'units', unitName.toLowerCase(), 'protocols.py') : path.join(process.cwd(), '..', 'units', unitName.toLowerCase(), 'protocols.py');
    if (fs.existsSync(protocolsPyPath)) {
      const content = fs.readFileSync(protocolsPyPath, 'utf-8');
      const match = content.match(/UNIT_RULES = \[([\s\S]*?)\]/);
      if (match) {
        const rulesStr = match[1];
        const rules = Array.from(rulesStr.matchAll(/^\s*"(.*?)"\s*(?:,|$)/gm)).map(m => m[1]);
        if (rules.length === 0) {
          const fallbackRules = Array.from(rulesStr.matchAll(/^\s*'(.*?)'\s*(?:,|$)/gm)).map(m => m[1]);
          return NextResponse.json({ rules: fallbackRules });
        }
        return NextResponse.json({ rules });
      }
    }

    return NextResponse.json({ rules: [] });
  } catch (error) {
    console.error('Failed to read unit protocols:', error);
    return NextResponse.json({ error: 'Failed to read unit protocols', rules: [] }, { status: 500 });
  }
}

export async function POST(request: Request): Promise<Response> {
  try {
    const { name, rules } = await request.json();
    if (!name || !rules) return NextResponse.json({ error: 'Invalid data' }, { status: 400 });

    const protocolsJsonPath = process.env.MCP_ROOT ? path.join(process.env.MCP_ROOT, 'units', name.toLowerCase(), 'protocols.json') : path.join(process.cwd(), '..', 'units', name.toLowerCase(), 'protocols.json');
    
    let data: { OVERVIEW?: string; RULES: string[] } = { RULES: [] };
    
    // 기존 JSON 파일이 있다면 병합 (OVERVIEW 등 보존)
    if (fs.existsSync(protocolsJsonPath)) {
      const content = fs.readFileSync(protocolsJsonPath, 'utf-8');
      data = JSON.parse(content);
    }
    
    data.RULES = rules;

    // JSON 규격으로 파일 작성 (AST를 훼손하던 기존 fs.writeFileSync 방식 탈피)
    fs.writeFileSync(protocolsJsonPath, JSON.stringify(data, null, 2), 'utf-8');
    
    return NextResponse.json({ success: true });
  } catch (error) {
    console.error('Failed to update unit protocols:', error);
    return NextResponse.json({ error: 'Failed to update unit protocols' }, { status: 500 });
  }
}
