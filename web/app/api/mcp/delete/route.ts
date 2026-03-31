import { NextResponse } from 'next/server';
import { spawn } from 'child_process';
import path from 'path';

/**
 * [대장님 🎯] Circuit을 물리적으로 영구 삭제하는 API입니다. 🛡️💥
 */
export async function POST(request: Request) {
  const { name } = await request.json();

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
      params: { protocolVersion: "2024-11-05", capabilities: {}, clientInfo: { name: "Web-Deleter", version: "1.0.0" } }
    }) + '\n');

    // 1. 삭제 도구 호출
    const deleteMessage = JSON.stringify({
      jsonrpc: "2.0", id: 2, method: "tools/call",
      params: { name: "mcp_operator_delete_circuit", arguments: { name } }
    }) + '\n';

    // 2. 오퍼레이터 리로드 호출
    const reloadMessage = JSON.stringify({
      jsonrpc: "2.0", id: 3, method: "tools/call",
      params: { name: "mcp_operator_reload_operator", arguments: {} }
    }) + '\n';

    setTimeout(() => {
      mcpProcess.stdin.write(deleteMessage);
      setTimeout(() => {
        mcpProcess.stdin.write(reloadMessage);
      }, 500);
    }, 500);

    mcpProcess.stdout.on('data', (data) => {
      try {
        const jsonResponse = JSON.parse(data.toString());
        if (jsonResponse.id === 2) {
          console.log(`[DELETE-API] ${jsonResponse.result.content[0].text}`);
        }
        if (jsonResponse.id === 3) {
          mcpProcess.kill();
          resolve(NextResponse.json({ success: true }));
        }
      } catch (e) {}
    });

    mcpProcess.stderr.on('data', (data) => { console.log(`[MCP-SYSTEM] ${data}`); });
    setTimeout(() => { mcpProcess.kill(); resolve(NextResponse.json({ error: "Timeout" }, { status: 504 })); }, 10000);
  });
}
