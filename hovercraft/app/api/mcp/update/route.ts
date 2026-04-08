import { NextResponse } from 'next/server';
import { McpClient } from '@/lib/mcpClient';

/**
 * [사용자] 웹에서 수정한 정보를 소스 코드에 반영하고 엔진을 동기화하는 통합 쓰기 API입니다.
 * McpClient를 통해 쓰기 작업과 리로드를 원자적으로 처리합니다.
 */
export async function POST(request: Request): Promise<Response> {
  const { circuit_name, rules, description, units, action } = await request.json();
  const client = new McpClient();

  try {
    const toolsToCall: any = {};

    // 1. 정보 업데이트 도구 정의
    if (action === 'OVERVIEW_UPDATE' || action === 'UNITS_UPDATE') {
      toolsToCall.update = {
        name: "mcp_operator_mcp_operator_update",
        args: { target: "overview", name: circuit_name, data: { description, units } }
      };
    } else {
      toolsToCall.update = {
        name: "mcp_operator_mcp_operator_update",
        args: { target: "protocol", name: circuit_name, data: { rules } }
      };
    }

    // 2. 엔진 리로드 도구 추가 (업데이트 직후 즉시 실행)
    toolsToCall.reload = {
      name: "mcp_operator_mcp_operator_execute",
      args: { action: "reload" }
    };

    // [사용자] 모든 작업을 일괄 요청하고 응답을 대기합니다.
    const results = await client.callTools(toolsToCall);

    return NextResponse.json({ 
      success: true, 
      message: "Sync complete",
      details: results 
    });

  } catch (error) {
    console.error('Update Bridge Error:', error);
    return NextResponse.json({ 
      error: error instanceof Error ? error.message : 'Update failed' 
    }, { status: 500 });
  }
}
