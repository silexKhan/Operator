
import asyncio
import websockets
import json
import time

async def test_mcp_status():
    uri = "ws://localhost:3001"
    async with websockets.connect(uri) as websocket:
        print(f"Connected to {uri}")
        
        # 1. INIT 메시지 수신 확인
        init_msg = await websocket.recv()
        print(f"Received INIT: {init_msg}")
        
        # 2. operator_get_status 명령 전송
        command = {
            "type": "COMMAND",
            "action": "operator_get_status",
            "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
        }
        print(f"Sending COMMAND: {json.dumps(command)}")
        await websocket.send(json.dumps(command))
        
        # 3. 응답 대기 (최대 5초)
        try:
            while True:
                response = await asyncio.wait_for(websocket.recv(), timeout=5.0)
                print(f"Received Response: {response}")
                data = json.loads(response)
                if data.get("type") == "STATUS_UPDATE":
                    print("SUCCESS: Received STATUS_UPDATE")
                    break
        except asyncio.TimeoutError:
            print("FAILED: Timeout waiting for STATUS_UPDATE")

if __name__ == "__main__":
    asyncio.run(test_mcp_status())
