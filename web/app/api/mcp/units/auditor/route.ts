import { NextResponse } from 'next/server';
import fs from 'fs';
import path from 'path';

/**
 * [대장님 🎯] 특정 전문 유닛(Unit)의 감사기(Auditor.py) 소스 코드를 읽고 수정합니다. 🛡️⚡️
 */
export async function GET(request: Request) {
  const { searchParams } = new URL(request.url);
  const unitName = searchParams.get('unit');
  
  if (!unitName) return NextResponse.json({ error: 'Unit name is required' }, { status: 400 });

  try {
    const auditorPath = path.join(process.cwd(), '..', 'units', unitName.toLowerCase(), 'auditor.py');
    
    if (!fs.existsSync(auditorPath)) {
      return NextResponse.json({ code: '' });
    }

    const code = fs.readFileSync(auditorPath, 'utf-8');
    return NextResponse.json({ code });
  } catch (error) {
    return NextResponse.json({ error: 'Failed to read unit auditor' }, { status: 500 });
  }
}

export async function POST(request: Request) {
  try {
    const { name, code } = await request.json();
    if (!name || code === undefined) return NextResponse.json({ error: 'Invalid data' }, { status: 400 });

    const auditorPath = path.join(process.cwd(), '..', 'units', name.toLowerCase(), 'auditor.py');
    
    if (!fs.existsSync(auditorPath)) {
      return NextResponse.json({ error: 'Unit auditor file not found' }, { status: 404 });
    }

    fs.writeFileSync(auditorPath, code);
    return NextResponse.json({ success: true });
  } catch (error) {
    return NextResponse.json({ error: 'Failed to update unit auditor' }, { status: 500 });
  }
}
