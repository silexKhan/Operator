
import asyncio
import sys
import os
import json
from pathlib import Path

# MCP Operator 프로젝트 루트를 path에 추가
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from mcp_operator.engine.server import OperatorServer
import mcp.types as types

async def verify_tool(server, name, args):
    print(f"Testing tool: {name} with args: {args}...", end=" ", flush=True)
    try:
        result = await server._dispatch_tool_handler(name, args)
        if result and isinstance(result, list) and len(result) > 0:
            content = result[0].text if hasattr(result[0], 'text') else str(result[0])
            if " Error:" in content or content.startswith("Error:"):
                print(f"❌ FAIL (Error response: {content[:120]}...)")
                return False
            print("✅ PASS")
            # JSON 형태의 응답인 경우 첫 50자 출력
            print(f"   [Result Preview]: {content[:100]}...")
            return True
        else:
            print("❌ FAIL (Empty or invalid response)")
            return False
    except Exception as e:
        print(f"❌ FAIL (Exception: {str(e)})")
        return False

async def main():
    state_path = Path(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "data", "state.json")))
    original_state = state_path.read_text(encoding="utf-8") if state_path.exists() else None
    server = OperatorServer()
    print("=== MCP Operator Function Verification ===\n")
    
    results = []
    
    # 1. 상태 확인
    results.append(await verify_tool(server, "operator_get_status", {}))
    
    # 2. 회선 전환
    results.append(await verify_tool(server, "operator_set_circuit", {"name": "mcp"}))
    
    # 3. 데이터 조회 (operator_get)
    results.append(await verify_tool(server, "operator_get", {"target": "overview"}))
    results.append(await verify_tool(server, "operator_get", {"target": "protocol", "name": "python"}))
    results.append(await verify_tool(server, "operator_get", {"target": "state"}))
    
    # 4. 데이터 업데이트 (operator_update) - 안전한 state 업데이트 테스트
    results.append(await verify_tool(server, "operator_update", {"target": "state", "data": {"last_verified": "today"}}))
    
    # 5. 액션 실행 (operator_execute)
    results.append(await verify_tool(server, "operator_execute", {"action": "audit", "params": {"file_path": "MISSION_PIPELINE"}}))
    
    # 6. 미션 실행
    results.append(await verify_tool(server, "operator_execute_mission", {}))
    
    # 7. 엔진 리로드
    results.append(await verify_tool(server, "operator_reload", {}))

    print("\n" + "="*40)
    success_count = sum(1 for r in results if r)
    print(f"Final Result: {success_count}/{len(results)} Passed")
    print("="*40)
    
    if original_state is not None:
        state_path.write_text(original_state, encoding="utf-8")
    
    if success_count < len(results):
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())
