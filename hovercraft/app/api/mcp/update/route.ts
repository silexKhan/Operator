import { NextResponse } from 'next/server';
import fs from 'fs';
import path from 'path';
import { exec } from 'child_process';
import { promisify } from 'util';

const execAsync = promisify(exec);

/**
 * [POST] 시스템 설정을 원자적으로 업데이트하고 엔진을 리로드하는 통합 API
 */
export async function POST(request: Request) {
  try {
    const { target, name, data } = await request.json();
    const rootDir = path.resolve(process.cwd(), '../');
    let filePath = '';

    // 1. 타겟별 파일 경로 매핑
    switch (target) {
      case 'state':
        filePath = path.join(rootDir, 'data/state.json');
        break;
      case 'circuit_overview':
        filePath = path.join(rootDir, `mcp_operator/registry/circuits/registry/${name}/overview.json`);
        break;
      case 'circuit_protocols':
        filePath = path.join(rootDir, `mcp_operator/registry/circuits/registry/${name}/protocols.json`);
        break;
      case 'unit_protocols':
        filePath = path.join(rootDir, `mcp_operator/registry/units/${name}/protocols.json`);
        break;
      case 'mission':
        filePath = path.join(rootDir, 'data/mission.json');
        break;
      case 'resource_monitor':
        filePath = path.join(rootDir, 'data/resource_monitor.json');
        break;
      case 'global_protocols':
        filePath = path.join(rootDir, 'mcp_operator/engine/protocols.py');
        break;
      default:
        return NextResponse.json({ error: 'Invalid update target' }, { status: 400 });
    }

    // 2. 백업 생성 (data/history/)
    const historyDir = path.join(rootDir, 'data/history');
    if (!fs.existsSync(historyDir)) fs.mkdirSync(historyDir, { recursive: true });
    
    if (fs.existsSync(filePath)) {
      const timestamp = new Date().toISOString().replace(/[:.]/g, '-');
      const backupPath = path.join(historyDir, `${timestamp}_${path.basename(filePath)}`);
      fs.copyFileSync(filePath, backupPath);
    }

    // 3. 파일 쓰기 및 병합
    let finalData = data;
    if (fs.existsSync(filePath)) {
      try {
        const existing = JSON.parse(fs.readFileSync(filePath, 'utf-8'));
        if (typeof data === 'object' && !Array.isArray(data)) {
          finalData = { ...existing, ...data };
        }
      } catch (e) {
        console.warn(`[API] Failed to parse existing file at ${filePath}, overwriting.`);
      }
    }

    const content = typeof finalData === 'string' ? finalData : JSON.stringify(finalData, null, 2);
    fs.writeFileSync(filePath, content, 'utf-8');

    // 4. 엔진 리로드 (Signal 기반 또는 Command 기반)
    // [사용자] 현재 시스템은 state.json 변경을 감지하므로, state.json의 타임스탬프를 갱신하여 리로드를 유도합니다.
    const statePath = path.join(rootDir, 'data/state.json');
    if (fs.existsSync(statePath)) {
      const state = JSON.parse(fs.readFileSync(statePath, 'utf-8'));
      state.last_update = new Date().toISOString();
      fs.writeFileSync(statePath, JSON.stringify(state, null, 2), 'utf-8');
    }

    return NextResponse.json({ success: true, message: `Update successful for ${target}` });

  } catch (error) {
    console.error('Update Error:', error);
    return NextResponse.json({ error: 'Failed to update resource' }, { status: 500 });
  }
}
