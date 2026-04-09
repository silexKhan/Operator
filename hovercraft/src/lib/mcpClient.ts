/**
 * [사용자] MCP 엔진(File-based IPC)과 통신을 전담하는 지능형 브릿지 클라이언트입니다.
 * 웹소켓을 제거하고 HTTP API를 통해 엔진의 상태 파일을 다이렉트로 읽어옵니다.
 */
export class McpClient {
  private static instance: McpClient;
  private stateUrl = '/api/mcp/state';
  private lastState: any = null;

  constructor() {}

  public static getInstance(): McpClient {
    if (!McpClient.instance) {
      McpClient.instance = new McpClient();
    }
    return McpClient.instance;
  }

  /**
   * [IPC] 엔진의 최신 상태를 가져옵니다.
   */
  public async fetchState(): Promise<any> {
    try {
      const response = await fetch(this.stateUrl, { cache: 'no-store' });
      if (!response.ok) throw new Error('Failed to fetch MCP state');
      
      const state = await response.json();
      this.lastState = state;
      return state;
    } catch (error) {
      console.error(`[MCP-UI] ❌ 엔진 상태 동기화 실패: ${error instanceof Error ? error.message : 'Unknown'}`);
      return null;
    }
  }

  /**
   * [Legacy compatibility] 엔진 서버에 명령을 전달합니다.
   * 현재 구조에서는 엔진이 파일을 쓰고 UI가 읽는 방식이므로, 
   * 쓰기 작업(Tool Call)은 직접적인 엔진 프로세스 제어가 필요할 수 있습니다.
   */
  public async callTools(tools: { [alias: string]: { name: string, args: any } }): Promise<any> {
    console.warn("[MCP-UI] ⚠️ 다이렉트 도구 호출은 현재 엔진의 MCP 서버 인터페이스를 통해야 합니다.");
    // TODO: 엔진의 HTTP/Stdio 엔드포인트와 연동 필요 시 구현
    return {};
  }

  public getStatus(): boolean {
    return this.lastState !== null && this.lastState.status !== 'OFFLINE';
  }

  public getLastState(): any {
    return this.lastState;
  }
}
