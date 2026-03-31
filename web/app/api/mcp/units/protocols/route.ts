import { NextResponse } from 'next/server';
import fs from 'fs';
import path from 'path';

/**
 * [대장님 🎯] 특정 전문 유닛(Unit)의 독자적인 프로토콜을 읽고 수정합니다. 🛡️⚡️
 * 정교화된 정규표현식을 통해 문장 내부의 따옴표를 구분자로 오인하지 않도록 개선했습니다.
 */
export async function GET(request: Request) {
  const { searchParams } = new URL(request.url);
  const unitName = searchParams.get('unit');
  
  if (!unitName) return NextResponse.json({ error: 'Unit name is required' }, { status: 400 });

  try {
    const protocolsPath = path.join(process.cwd(), '..', 'units', unitName.toLowerCase(), 'protocols.py');
    
    if (!fs.existsSync(protocolsPath)) {
      return NextResponse.json({ rules: [] });
    }

    const content = fs.readFileSync(protocolsPath, 'utf-8');
    
    // [대장님 🎯] UNIT_RULES 리스트 본체를 추출합니다.
    const match = content.match(/UNIT_RULES = \[(.*?)\]/s);
    if (match) {
      const rulesStr = match[1];
      
      // [대장님 🎯] 각 행에서 바깥쪽 따옴표(")로 감싸진 전체 문장만 정확히 추출합니다. 🕵️‍♂️
      // 내부의 작은따옴표(')나 쉼표(,)에 현혹되지 않습니다.
      const rules = Array.from(rulesStr.matchAll(/^\s*"(.*?)"\s*(?:,|$)/gm)).map(m => m[1]);
      
      // 만약 큰따옴표 매칭이 실패할 경우(작은따옴표 사용 시)를 대비한 보조 매칭
      if (rules.length === 0) {
        const fallbackRules = Array.from(rulesStr.matchAll(/^\s*'(.*?)'\s*(?:,|$)/gm)).map(m => m[1]);
        return NextResponse.json({ rules: fallbackRules });
      }

      return NextResponse.json({ rules });
    }

    return NextResponse.json({ rules: [] });
  } catch (error) {
    console.error('Failed to read unit protocols:', error);
    return NextResponse.json({ error: 'Failed to read unit protocols', rules: [] }, { status: 500 });
  }
}

export async function POST(request: Request) {
  try {
    const { name, rules } = await request.json();
    if (!name || !rules) return NextResponse.json({ error: 'Invalid data' }, { status: 400 });

    const protocolsPath = path.join(process.cwd(), '..', 'units', name.toLowerCase(), 'protocols.py');
    
    if (!fs.existsSync(protocolsPath)) {
      return NextResponse.json({ error: 'Unit protocols file not found' }, { status: 404 });
    }

    let content = fs.readFileSync(protocolsPath, 'utf-8');
    
    // [대장님 🎯] 리스트 내용을 표준 규격으로 포맷팅하여 치환합니다.
    const newRulesStr = rules.map((r: string) => `            "${r}"`).join(',\n');
    const updatedContent = content.replace(
      /UNIT_RULES = \[(.*?)\]/s, 
      `UNIT_RULES = [\n${newRulesStr}\n        ]`
    );

    fs.writeFileSync(protocolsPath, updatedContent);
    return NextResponse.json({ success: true });
  } catch (error) {
    console.error('Failed to update unit protocols:', error);
    return NextResponse.json({ error: 'Failed to update unit protocols' }, { status: 500 });
  }
}
