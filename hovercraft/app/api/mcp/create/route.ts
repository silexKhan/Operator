import { NextResponse } from 'next/server';
import { McpClient } from '@/lib/mcpClient';

/**
 * [사용자] 새로운 Circuit을 물리적으로 생성하고 엔진을 동기화하는 API입니다.
 * McpClient를 통해 생성과 리로드를 통합 관리합니다.
 */
export async function POST(request: Request): Promise<Response> {
  const { name, role, inherit_global } = await request.json();
  const client = new McpClient();

  try {
    const results = await client.callTools({
      create: {
        name: "mcp_operator_mcp_operator_create",
        args: { 
          target: "circuit",
          name
        }
      },
      reload: {
        name: "mcp_operator_mcp_operator_execute",
        args: { action: "reload" }
      }
    });

    return NextResponse.json({ 
      success: true, 
      message: "Circuit creation and sync complete",
      details: results 
    });

  } catch (error) {
    console.error('Create Bridge Error:', error);
    return NextResponse.json({ 
      error: error instanceof Error ? error.message : 'Creation failed' 
    }, { status: 500 });
  }
}
