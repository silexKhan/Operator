import { NextResponse } from 'next/server';
import fs from 'fs';
import path from 'path';

/**
 * [사용자] 현재 지휘소(MCP)에 등록된 모든 전문 기술 유닛(Units) 리스트를 동적으로 스캔하여 반환합니다. 
 * 물리적 경로 정보를 포함하여 보안 및 이식성을 확보합니다.
 */
export async function GET(): Promise<Response> {
  try {
    const unitsPath = process.env.MCP_ROOT ? path.join(process.env.MCP_ROOT, 'units') : path.join(process.cwd(), '..', 'units');
    
    if (!fs.existsSync(unitsPath)) {
      return NextResponse.json({ units: [] });
    }
// 디렉토리 리스트를 스캔하여 유닛 이름을 추출합니다 (캐시 및 숨김 파일 제외) 
const items = fs.readdirSync(unitsPath);
const units = items.filter(item => {
  const fullPath = path.join(unitsPath, item);
  // __pycache__ 및 점(.)으로 시작하는 폴더 제외
  return fs.statSync(fullPath).isDirectory() && 
         !item.startsWith('.') && 
         item !== '__pycache__';
}).map(name => ({
  name,
  path: `units/${name}`
}));


    return NextResponse.json({ units });
  } catch (error) {
    console.error('Failed to scan units:', error);
    return NextResponse.json({ error: 'Internal Server Error', units: [] }, { status: 500 });
  }
}
