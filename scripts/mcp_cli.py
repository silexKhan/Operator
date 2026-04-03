#
#  mcp_cli.py - Operator (교환) Command Line Interface 
#

import argparse
import sys
import os
import json
import asyncio

# 프로젝트 루트를 sys.path 에 추가 
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from circuits.manager import CircuitManager
from core.logger import OperatorLogger

def main():
    # [사용자] 가용한 회선 목록을 실시간으로 추출하여 도움말에 동적으로 주입합니다. 
    manager = CircuitManager()
    available_list = ", ".join(manager.circuits.keys())
    hint = f"(현재 가용: {available_list})" if available_list else "(가용 회선 없음)"

    parser = argparse.ArgumentParser(description=" Operator (교환) CLI - Circuit & Protocol Management")
    subparsers = parser.add_subparsers(dest="command", help="사용 가능한 명령")

    # 1. 상태 조회
    subparsers.add_parser("status", help="교환 및 회선(Circuit) 활성 상태 확인")

    # 2. 회선 목록
    subparsers.add_parser("list", help="등록된 모든 회선(Circuit) 목록 출력")

    # 3. 회선 연결 (Set Active)
    set_parser = subparsers.add_parser("connect", help="특정 회선(Circuit) 강제 연결")
    set_parser.add_argument("name", type=str, help=f"연결할 회선 이름 {hint}")

    # 4. 규약 검증 (Audit)
    audit_parser = subparsers.add_parser("audit", help="현재 회선 규약(Protocols)으로 파일 검증")
    audit_parser.add_argument("path", type=str, help="검증할 파일 경로")

    args = parser.parse_args()


    if args.command == "status":
        active = manager.get_active_circuit()
        active_name = active.get_name() if active else "None"
        print(f"\n Operator Status: Online")
        print(f" Current Path: {manager.current_path}")
        print(f" Active Circuit: \033[92m{active_name}\033[0m")
        print(f" Registered Lines: {list(manager.circuits.keys())}\n")

    elif args.command == "list":
        print(f"\n [Registered Circuits]")
        for key in manager.circuits.keys():
            print(f"  - {key}")
        print("")

    elif args.command == "connect":
        if manager.set_active_circuit(args.name):
            print(f" \033[92m{args.name}\033[0m 회선이 연결되었습니다!")
        else:
            print(f" '{args.name}' 회선을 찾을 수 없습니다.")

    elif args.command == "audit":
        active = manager.get_active_circuit()
        if not active:
            print(" 연결된 회선이 없습니다. 먼저 'connect' 명령으로 회선을 지정하세요.")
            return

        async def run_audit():
            print(f" [{active.get_name()}] 규약 검수 시작: {args.path}")
            tools = active.get_tools()
            audit_tool = next((t for t in tools if "audit" in t.name), None)
            
            if audit_tool:
                result = await active.call_tool(audit_tool.name, {"file_path": args.path})
                print(f"\n{result[0].text}")
            else:
                print(f" {active.get_name()} 회선은 audit 도구를 지원하지 않습니다.")

        asyncio.run(run_audit())

    else:
        parser.print_help()

if __name__ == "__main__":
    main()
