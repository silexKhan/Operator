#
#  mcp_cli.py - Silex MCP Hub CLI Controller 🛠️🚀
#

import sys
import os
import argparse
from tenants.manager import TenantManager
from core.logger import HubLogger

def main():
    parser = argparse.ArgumentParser(description="🛡️ Silex MCP Hub CLI Controller")
    subparsers = parser.add_subparsers(dest="command", help="Commands")

    # status
    subparsers.add_parser("status", help="허브 및 테넌트 활성 상태 확인")

    # list
    subparsers.add_parser("list", help="등록된 모든 테넌트 목록 출력")

    # set [name]
    set_parser = subparsers.add_parser("set", help="테넌트 강제 활성화")
    set_parser.add_argument("name", type=str, help="활성화할 테넌트 이름 (예: gdr, auth)")

    # audit [file]
    audit_parser = subparsers.add_parser("audit", help="현재 테넌트 공리로 파일 검증")
    audit_parser.add_argument("file", type=str, help="검증할 파일 경로")

    args = parser.parse_args()

    # Hub 인스턴스 초기화 (Manager를 통해 상태 공유)
    manager = TenantManager()
    logger = HubLogger("MCP-CLI")

    if args.command == "status":
        active = manager.get_active_tenant()
        active_name = active.get_name() if active else "None"
        print(f"\n🚀 [Hub Status: Online]")
        print(f"📍 Current Path: {manager.current_path}")
        print(f"🏢 Active Tenant: \033[92m{active_name}\033[0m")
        print(f"📋 Registered: {list(manager.tenants.keys())}\n")

    elif args.command == "list":
        print(f"\n📋 [Registered Tenants]")
        for key in manager.tenants.keys():
            print(f"  - {key}")
        print("")

    elif args.command == "set":
        if manager.set_active_tenant(args.name):
            print(f"✅ \033[92m{args.name}\033[0m 테넌트가 활성화되었습니다!")
        else:
            print(f"❌ '{args.name}' 테넌트를 찾을 수 없습니다.")

    elif args.command == "audit":
        active = manager.get_active_tenant()
        if not active:
            print("⚠️ 활성화된 테넌트가 없습니다. 먼저 'set' 명령으로 테넌트를 지정하세요.")
            return

        # 테넌트의 call_tool을 호출하여 audit 수행 (MCP 프로토콜 모사)
        import asyncio
        import mcp.types as types
        
        async def run_audit():
            # 테넌트마다 audit_rules 도구 이름이 다를 수 있으므로 prefix 확인
            tool_name = "audit_rules"
            prefix = active.get_name().lower() + "_"
            
            # 테넌트 내부의 _audit 메서드 직접 호출 (CLI 편의상)
            if hasattr(active, "_audit"):
                result = active._audit(args.file)
                print(f"\n{result}\n")
            else:
                print(f"❌ {active.get_name()} 테넌트는 audit 도구를 지원하지 않습니다.")

        asyncio.run(run_audit())

    else:
        parser.print_help()

if __name__ == "__main__":
    main()
