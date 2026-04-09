import { NextResponse } from 'next/server';
import fs from 'fs';
import path from 'path';

export async function GET() {
  try {
    const logPath = path.resolve(process.cwd(), '../logs/mcp_live.log');
    
    if (!fs.existsSync(logPath)) {
      return NextResponse.json([]);
    }

    const logData = fs.readFileSync(logPath, 'utf-8');
    const lines = logData.trim().split('\n').filter(line => line.length > 0);
    
    // 최근 30개의 로그만 반환
    const recentLogs = lines.slice(-30).map(line => {
      try {
        return JSON.parse(line);
      } catch {
        return { message: line, level: 'INFO', category: 'RAW' };
      }
    });

    return NextResponse.json(recentLogs);
  } catch (error) {
    return NextResponse.json({ error: 'Failed to read logs' }, { status: 500 });
  }
}
