import { NextResponse } from 'next/server';
import { spawn } from 'child_process';
import path from 'path';

/**
 * [사용자] 오퍼레이터의 전체 회선 구조(Blueprint)를 JSON으로 긁어오는 핵심 브릿지입니다. 
 */
export async function GET(): Promise<Response> {
  return new Promise((resolve) => {
    const projectRoot = process.env.MCP_ROOT || path.join(process.cwd(), '..');
    const isWindows = process.platform === 'win32';
    const pythonPath = isWindows 
      ? path.join(projectRoot, '.venv', 'Scripts', 'python.exe')
      : path.join(projectRoot, '.venv', 'bin', 'python');
    
    const scriptPath = path.join(projectRoot, 'main.py');
    const mcpProcess = spawn(pythonPath, [scriptPath], {
      cwd: projectRoot,
      env: { ...process.env, PYTHONIOENCODING: 'utf-8' }
    });
    
    // 1. 초기화 (지휘권 확립)
    mcpProcess.stdin.write(JSON.stringify({
      jsonrpc: "2.0", id: 1, method: "initialize",
      params: { protocolVersion: "2024-11-05", capabilities: {}, clientInfo: { name: "Web-Registry-V3", version: "3.0.0" } }
    }) + '\n');

    // 2. 전체 구조(JSON) 요청 - [사용자] 통신 규약 준수 
    const initializedMessage = JSON.stringify({
      jsonrpc: "2.0", method: "notifications/initialized"
    }) + '\n';
    
    const callMessage = JSON.stringify({
      jsonrpc: "2.0", id: 2, method: "tools/call",
      params: { name: "mcp_operator_get_full_json_structure", arguments: {} }
    }) + '\n';

    setTimeout(() => {
      mcpProcess.stdin.write(initializedMessage);
      mcpProcess.stdin.write(callMessage);
    }, 500);


    let fullData = "";

    mcpProcess.stdout.on('data', (data) => {
      fullData += data.toString();
      
      const lines = fullData.split('\n');
      // 마지막 미완성 줄은 다음 chunk를 위해 보관 
      fullData = lines.pop() || "";
      
      for (const line of lines) {
        if (!line.trim()) continue;
        try {
          const jsonResponse = JSON.parse(line);
          
          if (jsonResponse.id === 2) {
            // 백엔드가 준 JSON 문자열을 다시 객체로 변환하여 전달 
            const rawContent = jsonResponse.result.content[0].text;
            const parsedData = JSON.parse(rawContent);
            mcpProcess.kill();
            resolve(NextResponse.json(parsedData));
            return;
          }
        } catch (e) {
          // JSON 파싱 실패 시 무시 (로그 등 다른 출력일 수 있음)
        }
      }
    });

    mcpProcess.stderr.on('data', (data) => { console.log(`[MCP-SYSTEM] ${data}`); });
    
    // 타임아웃 방어막 
    setTimeout(() => { 
      mcpProcess.kill(); 
      resolve(NextResponse.json({ error: "지휘소 응답 지연 (Timeout)" }, { status: 504 })); 
    }, 8000);
  });
}
