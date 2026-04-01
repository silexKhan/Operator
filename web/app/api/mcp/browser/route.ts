import { NextResponse } from 'next/server';
import { spawn } from 'child_process';
import path from 'path';

export async function GET(request: Request): Promise<Response> {
  const { searchParams } = new URL(request.url);
  const targetPath = searchParams.get('path') || '.';

  return new Promise((resolve) => {
    const projectRoot = process.env.MCP_ROOT || path.join(process.cwd(), '..');
    const isWindows = process.platform === 'win32';
    const pythonPath = isWindows 
      ? path.join(projectRoot, '.venv', 'Scripts', 'python.exe')
      : path.join(projectRoot, '.venv', 'bin', 'python');
    
    const scriptPath = path.join(projectRoot, 'main.py');
    const mcpProcess = spawn(pythonPath, [scriptPath]);
    
    mcpProcess.stdin.write(JSON.stringify({
      jsonrpc: "2.0", id: 1, method: "initialize",
      params: { protocolVersion: "2024-11-05", capabilities: {}, clientInfo: { name: "Web-Browser-Universal", version: "1.6.0" } }
    }) + '\n');

    const callMessage = JSON.stringify({
      jsonrpc: "2.0", id: 2, method: "tools/call",
      params: { name: "mcp_operator_browse_directory", arguments: { path: targetPath } }
    }) + '\n';

    setTimeout(() => {
      mcpProcess.stdin.write(callMessage);
    }, 500);

    mcpProcess.stdout.on('data', (data) => {
      try {
        const jsonResponse = JSON.parse(data.toString());
        if (jsonResponse.id === 2 && jsonResponse.result) {
          const result = JSON.parse(jsonResponse.result.content[0].text);
          mcpProcess.kill();
          resolve(NextResponse.json(result));
        }
      } catch (e) {}
    });

    mcpProcess.stderr.on('data', (data) => { console.log(`[MCP-SYSTEM] ${data}`); });
    setTimeout(() => { mcpProcess.kill(); resolve(NextResponse.json({ error: "Timeout" }, { status: 504 })); }, 5000);
  });
}
