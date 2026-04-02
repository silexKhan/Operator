import { spawn, ChildProcessWithoutNullStreams } from 'child_process';
import path from 'path';

export interface McpResponse {
  [key: string]: any;
}

/**
 * [사용자] MCP 서버와의 통신을 전담하는 지능형 브릿지 클라이언트입니다.
 * JSON-RPC ID 관리 및 비동기 스트림 데이터 수집을 자동화합니다.
 */
export class McpClient {
  private process: ChildProcessWithoutNullStreams | null = null;
  private currentId = 1;
  private projectRoot: string;
  private pythonPath: string;
  private scriptPath: string;

  constructor() {
    // [사용자] 웹 서버 실행 위치와 관계없이 절대 경로를 계산합니다.
    this.projectRoot = process.env.MCP_ROOT || path.resolve(process.cwd(), '..');
    const isWindows = process.platform === 'win32';
    this.pythonPath = isWindows 
      ? path.join(this.projectRoot, '.venv', 'Scripts', 'python.exe')
      : path.join(this.projectRoot, '.venv', 'bin', 'python');
    this.scriptPath = path.join(this.projectRoot, 'main.py');
  }

  private async initialize(): Promise<void> {
    this.process = spawn(this.pythonPath, [this.scriptPath]);
    
    return new Promise((resolve, reject) => {
      if (!this.process) return reject('Process failed to start');

      const initMessage = JSON.stringify({
        jsonrpc: "2.0", id: this.currentId++, method: "initialize",
        params: { protocolVersion: "2024-11-05", capabilities: {}, clientInfo: { name: "Web-Mcp-Bridge", version: "1.0.0" } }
      }) + '\n';

      this.process.stdin.write(initMessage);

      const onData = (data: Buffer) => {
        const output = data.toString();
        if (output.includes('"id":1')) {
          this.process?.stdout.off('data', onData);
          resolve();
        }
      };

      this.process.stdout.on('data', onData);
      this.process.stderr.on('data', (data) => console.error(`[MCP-ERR] ${data}`));
      
      setTimeout(() => reject('Initialization Timeout'), 5000);
    });
  }

  public async callTools(tools: { [alias: string]: { name: string, args: any } }): Promise<McpResponse> {
    if (!this.process) await this.initialize();
    
    return new Promise((resolve, reject) => {
      const results: McpResponse = {};
      const pendingIds = new Map<number, string>();

      Object.entries(tools).forEach(([alias, tool]) => {
        const id = this.currentId++;
        pendingIds.set(id, alias);
        
        const message = JSON.stringify({
          jsonrpc: "2.0", id, method: "tools/call",
          params: { name: tool.name, arguments: tool.args }
        }) + '\n';
        
        this.process?.stdin.write(message);
      });

      const onData = (data: Buffer) => {
        const lines = data.toString().split('\n');
        for (const line of lines) {
          if (!line.trim()) continue;
          try {
            const json = JSON.parse(line);
            const alias = pendingIds.get(json.id);
            if (alias) {
              const textContent = json.result?.content?.[0]?.text;
              try {
                results[alias] = textContent ? JSON.parse(textContent) : json.result;
              } catch {
                results[alias] = textContent || json.result;
              }
              pendingIds.delete(json.id);
            }
          } catch (e) {}
        }

        if (pendingIds.size === 0) {
          this.close();
          resolve(results);
        }
      };

      this.process?.stdout.on('data', onData);
      
      setTimeout(() => {
        this.close();
        resolve(results);
      }, 8000);
    });
  }

  private close() {
    if (this.process) {
      this.process.kill();
      this.process = null;
    }
  }
}
