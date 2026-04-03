import { NextResponse } from 'next/server';
import { McpClient } from '@/lib/mcpClient';

/**
 * [사용자] 서버의 물리적 디렉토리 구조를 탐색하는 API입니다.
 * McpClient를 통해 안정적인 스트림 데이터 수집을 보장합니다.
 */
export async function GET(request: Request): Promise<Response> {
  const { searchParams } = new URL(request.url);
  const targetPath = searchParams.get('path') || '.';

  const client = new McpClient();

  try {
    const results = await client.callTools({
      browser: {
        name: "mcp_operator_browse_directory",
        args: { path: targetPath }
      }
    });

    return NextResponse.json(results.browser || { current: targetPath, folders: [], files: [] });

  } catch (error) {
    console.error('Browser Bridge Error:', error);
    return NextResponse.json({ 
      error: error instanceof Error ? error.message : 'Path traversal failed' 
    }, { status: 500 });
  }
}
