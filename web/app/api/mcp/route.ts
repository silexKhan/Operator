import { NextResponse } from 'next/server';
import { McpClient } from '@/lib/mcpClient';

/**
 * [사용자] 사이드바 및 대시보드에서 필요한 전체 지휘소 정보를 통합 추출하는 API입니다.
 * McpClient를 통해 회선 목록, 유닛 목록, 의존성 그래프를 한 번에 수집합니다.
 */
export async function GET(): Promise<Response> {
  const client = new McpClient();

  try {
    // [사용자] 전체 프로젝트 구조를 분석하는 도구를 호출합니다.
    const results = await client.callTools({
      structure: { 
        name: "mcp_operator_get_full_json_structure", 
        args: {} 
      }
    });

    const data = results.structure || {};

    return NextResponse.json({
      registered_circuits: data.registered_circuits || [],
      active_units: data.active_units || [],
      dependency_graph: data.dependency_graph || [],
      // [사용자] 사이드바 렌더링을 위해 각 회선별 유닛 정보를 미리 매핑하여 보냅니다.
      circuit_details: data.circuits || {}
    });

  } catch (error) {
    console.error('Main Dashboard API Error:', error);
    return NextResponse.json({ 
      error: error instanceof Error ? error.message : 'Discovery failed',
      registered_circuits: [],
      active_units: [],
      dependency_graph: []
    }, { status: 500 });
  }
}
