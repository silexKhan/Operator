import { NextResponse } from 'next/server';
import { spawn } from 'child_process';
import path from 'path';

/**
 * [대장님 🎯] 웹에서 수정한 규약(Protocols), 개요(Overview), 유닛(Units) 정보를 실제 소스 코드에 반영하는 Write Bridge입니다. 🛡️⚡️
 * UNITS_UPDATE 액션 및 데이터 전달 로직이 완비되었습니다. 🚀
 */
export async function POST(request: Request) {
  const { circuit_name, rules, description, project_path, units, action } = await request.json();

  return new Promise((resolve) => {
    const projectRoot = path.join(process.cwd(), '..');
    const isWindows = process.platform === 'win32';
    const pythonPath = isWindows 
      ? path.join(projectRoot, '.venv', 'Scripts', 'python.exe')
      : path.join(projectRoot, '.venv', 'bin', 'python');
    
    const scriptPath = path.join(projectRoot, 'main.py');
    const mcpProcess = spawn(pythonPath, [scriptPath]);
    
    mcpProcess.stdin.write(JSON.stringify({
      jsonrpc: "2.0", id: 1, method: "initialize",
      params: { protocolVersion: "2024-11-05", capabilities: {}, clientInfo: { name: "Web-Reflector-Dynamic", version: "1.5.0" } }
    }) + '\n');

    // 상황에 따른 도구 호출 분기 🛡️
    let callMessage = '';
    
    if (action === 'OVERVIEW_UPDATE' || action === 'UNITS_UPDATE') {
      // [대장님 🎯] 유닛(units) 정보를 포함하여 백엔드 도구를 호출합니다. 🕵️‍♂️🚀
      callMessage = JSON.stringify({
        jsonrpc: "2.0", id: 2, method: "tools/call",
        params: {
          name: "mcp_operator_update_circuit_overview",
          arguments: { 
            circuit_name, 
            description, 
            project_path, 
            units // 유닛 데이터 명시적 전달 🛡️
          }
        }
      }) + '\n';
    } else {
      callMessage = JSON.stringify({
        jsonrpc: "2.0", id: 2, method: "tools/call",
        params: {
          name: "mcp_operator_update_circuit_protocols",
          arguments: { circuit_name, rules }
        }
      }) + '\n';
    }

    const reloadMessage = JSON.stringify({
      jsonrpc: "2.0", id: 3, method: "tools/call",
      params: { name: "mcp_operator_reload_operator", arguments: {} }
    }) + '\n';

    setTimeout(() => {
      mcpProcess.stdin.write(callMessage);
      setTimeout(() => {
        mcpProcess.stdin.write(reloadMessage);
      }, 500);
    }, 500);

    mcpProcess.stdout.on('data', (data) => {
      try {
        const jsonResponse = JSON.parse(data.toString());
        if (jsonResponse.id === 3) {
          mcpProcess.kill();
          resolve(NextResponse.json({ success: true, message: "Units and Overview reflected!" }));
        }
      } catch (e) {}
    });

    mcpProcess.stderr.on('data', (data) => { console.log(`[MCP-SYSTEM] ${data}`); });
    setTimeout(() => { mcpProcess.kill(); resolve(NextResponse.json({ error: "Timeout" }, { status: 504 })); }, 10000);
  });
}
