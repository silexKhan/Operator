import { NextResponse } from 'next/server';
import { spawn } from 'child_process';
import path from 'path';

/**
 * [대장님 🎯] 오퍼레이터의 전체 회선 구조(Blueprint)를 JSON으로 긁어오는 핵심 브릿지입니다. 🛡️⚡️
 */
export async function GET() {
  return new Promise((resolve) => {
    const projectRoot = path.join(process.cwd(), '..');
    const isWindows = process.platform === 'win32';
    const pythonPath = isWindows 
      ? path.join(projectRoot, '.venv', 'Scripts', 'python.exe')
      : path.join(projectRoot, '.venv', 'bin', 'python');
    
    const scriptPath = path.join(projectRoot, 'main.py');
    const mcpProcess = spawn(pythonPath, [scriptPath]);
    
    // 1. 초기화 (지휘권 확립)
    mcpProcess.stdin.write(JSON.stringify({
      jsonrpc: "2.0", id: 1, method: "initialize",
      params: { protocolVersion: "2024-11-05", capabilities: {}, clientInfo: { name: "Web-Registry-V3", version: "3.0.0" } }
    }) + '\n');

    // 2. 전체 구조(JSON) 요청 - [대장님 🎯] 호출명을 백엔드와 일치시킵니다. 📡
    const callMessage = JSON.stringify({
      jsonrpc: "2.0", id: 2, method: "tools/call",
      params: { name: "mcp_operator_get_full_json_structure", arguments: {} }
    }) + '\n';

    setTimeout(() => {
      mcpProcess.stdin.write(callMessage);
    }, 500);

    let fullData = "";

    mcpProcess.stdout.on('data', (data) => {
      const output = data.toString();
      try {
        // [대장님 🎯] 여러 줄의 응답 중 2번 ID(결과값)만 정밀 타격합니다. 🎯
        const lines = output.split('\n');
        for (const line of lines) {
          if (!line.trim()) continue;
          const jsonResponse = JSON.parse(line);
          
          if (jsonResponse.id === 2) {
            // 백엔드가 준 JSON 문자열을 다시 객체로 변환하여 전달 🚀
            const rawContent = jsonResponse.result.content[0].text;
            const parsedData = JSON.parse(rawContent);
            mcpProcess.kill();
            resolve(NextResponse.json(parsedData));
            return;
          }
        }
      } catch (e) {
        // 분할된 JSON 데이터 조각 모음 🧩
        fullData += output;
      }
    });

    mcpProcess.stderr.on('data', (data) => { console.log(`[MCP-SYSTEM] ${data}`); });
    
    // 타임아웃 방어막 🛡️
    setTimeout(() => { 
      mcpProcess.kill(); 
      resolve(NextResponse.json({ error: "지휘소 응답 지연 (Timeout)" }, { status: 504 })); 
    }, 8000);
  });
}
