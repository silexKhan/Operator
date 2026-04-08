import { NextResponse } from 'next/server';
import { McpClient } from '@/lib/mcpClient';

/**
 * [사용자] 특정 Circuit의 정보를 통합 추출하는 API입니다.
 * McpClient 공통 모듈을 사용하여 비동기 정합성과 ID 관리를 자동화했습니다.
 */
export async function GET(request: Request): Promise<Response> {
  const { searchParams } = new URL(request.url);
  const circuitName = searchParams.get('circuit') || 'mcp';

  const client = new McpClient();

  try {
    // [사용자] 필요한 도구들을 한 번에 정의하여 호출합니다.
    const results = await client.callTools({
      circuitProtocols: { 
        name: "mcp_operator_mcp_operator_get", 
        args: { target: "protocol", name: circuitName } 
      },
      globalProtocols: { 
        name: "mcp_operator_mcp_operator_get", 
        args: { target: "protocol" } 
      }
    });

    // 결과 정제 및 반환
    return NextResponse.json({
      rules: results.circuitProtocols?.protocols || [],
      globalRules: results.globalProtocols || []
    });

  } catch (error) {
    console.error('MCP Bridge Error:', error);
    return NextResponse.json({ 
      error: error instanceof Error ? error.message : 'Unknown error',
      rules: [], 
      globalRules: [] 
    }, { status: 500 });
  }
}
