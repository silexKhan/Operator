import psutil
import time
import os
import json
from datetime import datetime

def monitor_system(duration=60, interval=5):
    print(f"Monitoring started at {datetime.now()} for {duration} seconds...")
    results = []
    
    start_time = time.time()
    while time.time() - start_time < duration:
        sample = {
            "timestamp": datetime.now().isoformat(),
            "cpu_total": psutil.cpu_percent(),
            "mem_total": psutil.virtual_memory().percent,
            "processes": []
        }
        
        for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent', 'cmdline']):
            try:
                cmd = " ".join(proc.info['cmdline'] or [])
                if any(x in cmd for x in ['node', 'python', 'next-dev', 'mcp_operator']):
                    sample["processes"].append({
                        "pid": proc.info['pid'],
                        "name": proc.info['name'],
                        "cpu": proc.info['cpu_percent'],
                        "mem": proc.info['memory_percent'],
                        "cmd": cmd[:100]
                    })
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
        
        results.append(sample)
        time.sleep(interval)
        
    with open("resource_monitor.json", "w") as f:
        json.dump(results, f, indent=2)
    print("Monitoring complete. Data saved to resource_monitor.json")

if __name__ == "__main__":
    monitor_system()
