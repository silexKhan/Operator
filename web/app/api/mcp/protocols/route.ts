import { NextResponse } from 'next/server';
import { spawn } from 'child_process';
import path from 'path';

/**
 * [대장님 🎯] 특정 Circuit의 정보를 순수 JSON 형태로 추출하는 현대적 브릿지입니다. 🛡️⚡️
 */
export async function GET(request: Request) {
  const { searchParams } = new URL(request.url);
  const circuitName = searchParams.get('circuit') || 'mcp';

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
      params: { protocolVersion: "2024-11-05", capabilities: {}, clientInfo: { name: "Web-Explorer-Pure", version: "3.0.0" } }
    }) + '\n');

    // 1. 규약(Protocols) 요청
    const callProtocols = JSON.stringify({
      jsonrpc: "2.0", id: 2, method: "tools/call",
      params: { name: "mcp_operator_get_circuit_protocols", arguments: { circuit_name: circuitName } }
    }) + '\n';

    // 2. 전사 공통 규약 요청
    const callGlobalProtocols = JSON.stringify({
      jsonrpc: "2.0", id: 3, method: "tools/call",
      params: { name: "mcp_operator_get_global_protocols", arguments: {} }
    }) + '\n';

    // 3. 개요(Overview) 요청 - [대장님 🎯] 이제 JSON 데이터를 기대합니다! 💎
    const overviewToolName = circuitName === 'mcp' ? "mcp_operator_get_overview" : `mcp_operator_${circuitName}_get_overview`;
    const callOverview = JSON.stringify({
      jsonrpc: "2.0", id: 4, method: "tools/call",
      params: { name: overviewToolName, arguments: {} }
    }) + '\n';

    setTimeout(() => {
      mcpProcess.stdin.write(callProtocols);
      setTimeout(() => {
        mcpProcess.stdin.write(callGlobalProtocols);
        setTimeout(() => { mcpProcess.stdin.write(callOverview); }, 200);
      }, 200);
    }, 500);

    let rules = [];
    let globalRules = [];
    let briefing: any = {};

    mcpProcess.stdout.on('data', (data) => {
      const output = data.toString();
      try {
        const lines = output.split('\n');
        for (const line of lines) {
          if (!line.trim()) continue;
          const jsonResponse = JSON.parse(line);
          
          if (jsonResponse.id === 2) rules = JSON.parse(jsonResponse.result.content[0].text);
          if (jsonResponse.id === 3) globalRules = JSON.parse(jsonResponse.result.content[0].text);
          if (jsonResponse.id === 4) {
            // [대장님 🎯] 텍스트 파싱 대신 순수 JSON 파싱을 수행합니다! 🥳🔥
            briefing = JSON.parse(jsonResponse.result.content[0].text);
            
            mcpProcess.kill();
            resolve(NextResponse.json({ rules, globalRules, briefing }));
          }
        }
      } catch (e) {}
    });

    mcpProcess.stderr.on('data', (data) => { console.log(`[MCP-SYSTEM] ${data}`); });
    setTimeout(() => { mcpProcess.kill(); resolve(NextResponse.json({ error: "Timeout" }, { status: 504 })); }, 10000);
  });
}
