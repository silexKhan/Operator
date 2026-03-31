import { NextResponse } from 'next/server';
import { spawn } from 'child_process';
import path from 'path';

/**
 * [대장님 🎯] 웹에서 새로운 Circuit을 동적으로 생성하는 API입니다. 🛡️⚡️
 */
export async function POST(request: Request) {
  const { name, role, inherit_global } = await request.json();

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
      params: { protocolVersion: "2024-11-05", capabilities: {}, clientInfo: { name: "Web-Creator-V2", version: "1.7.0" } }
    }) + '\n');

    const callMessage = JSON.stringify({
      jsonrpc: "2.0", id: 2, method: "tools/call",
      params: { 
        name: "mcp_operator_create_new_circuit", 
        arguments: { name, role: role || "development", inherit_global: inherit_global !== false } 
      }
    }) + '\n';

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
          resolve(NextResponse.json({ success: true, message: "New Circuit established with inheritance settings!" }));
        }
      } catch (e) {}
    });

    mcpProcess.stderr.on('data', (data) => { console.log(`[MCP-SYSTEM] ${data}`); });
    setTimeout(() => { mcpProcess.kill(); resolve(NextResponse.json({ error: "Timeout" }, { status: 504 })); }, 10000);
  });
}
