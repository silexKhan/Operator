import { NextResponse } from 'next/server';
import fs from 'fs';
import path from 'path';

export async function GET() {
  try {
    // [IPC] 엔진이 작성하는 상태 파일 경로 (상위 디렉토리의 data/state.json)
    const statePath = path.resolve(process.cwd(), '../data/state.json');
    
    if (!fs.existsSync(statePath)) {
      return NextResponse.json({ 
        error: 'State file not found',
        status: 'OFFLINE' 
      }, { status: 404 });
    }

    const stateData = fs.readFileSync(statePath, 'utf-8');
    return NextResponse.json(JSON.parse(stateData));
  } catch (error) {
    return NextResponse.json({ 
      error: 'Failed to read state',
      status: 'ERROR' 
    }, { status: 500 });
  }
}
