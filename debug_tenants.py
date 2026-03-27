
import os
import sys
import importlib
import inspect
import traceback

# 프로젝트 루트를 경로에 추가
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from tenants.base import BaseTenant

def test_discovery():
    base_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "tenants")
    search_roots = ["projects"]
    
    for root in search_roots:
        root_path = os.path.join(base_dir, root)
        print(f"🔎 Searching in: {root_path}")
        
        for dirpath, _, filenames in os.walk(root_path):
            if "actions.py" in filenames:
                rel_path = os.path.relpath(dirpath, base_dir)
                module_name = f"tenants.{rel_path.replace(os.sep, '.')}.actions"
                
                print(f"尝试 loading: {module_name}")
                try:
                    module = importlib.import_module(module_name)
                    for name, obj in inspect.getmembers(module):
                        if inspect.isclass(obj) and issubclass(obj, BaseTenant) and obj is not BaseTenant:
                            print(f"✅ Found Tenant Class: {name} in {module_name}")
                except Exception as e:
                    print(f"❌ Failed to load {module_name}: {str(e)}")
                    traceback.print_exc()

if __name__ == "__main__":
    test_discovery()
