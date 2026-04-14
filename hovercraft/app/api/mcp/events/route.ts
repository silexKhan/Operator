import { NextRequest } from "next/server";
import fs from "fs";
import path from "path";

const ROOT = path.join(process.cwd());
const DATA_DIR = path.join(ROOT, "data");
const STATE_FILE = path.join(DATA_DIR, "state.json");
const LOG_FILE = path.join(ROOT, "..", "logs", "mcp_server.log");

export async function GET(req: NextRequest) {
  const encoder = new TextEncoder();

  const stream = new ReadableStream({
    async start(controller) {
      // 1. Initial State Push
      const sendState = () => {
        try {
          const statePath = path.join(process.cwd(), "data", "state.json");
          if (fs.existsSync(statePath)) {
            const stateStr = fs.readFileSync(statePath, "utf-8");
            const state = JSON.parse(stateStr);

            // 활성 회선의 상세 정보(details) 추가 로드
            const circuitPath = path.join(process.cwd(), "..", "mcp_operator", "registry", "circuits", "registry", state.active_circuit);
            const protocolsPath = path.join(circuitPath, "protocols.json");
            const overviewPath = path.join(circuitPath, "overview.json");

            const active_circuit_details: any = { protocols: [], overview: {} };
            if (fs.existsSync(protocolsPath)) {
              const data = JSON.parse(fs.readFileSync(protocolsPath, "utf-8"));
              active_circuit_details.protocols = data.RULES || data.protocols || [];
            }
            if (fs.existsSync(overviewPath)) {
              active_circuit_details.overview = JSON.parse(fs.readFileSync(overviewPath, "utf-8"));
            }

            const payload = { ...state, active_circuit_details };
            controller.enqueue(encoder.encode(`event: state\ndata: ${JSON.stringify(payload)}\n\n`));
            console.log(`[SSE_SEND] Dispatched full state update to client: ${state.active_circuit}`);
          }
        } catch (error) {
          console.warn("[SSE_SEND] State Sync Skip (File Busy/Partial):", error instanceof Error ? error.message : "Unknown");
        }
      };

      sendState();

      // 2. Watch for Changes (State)
      const stateWatcher = fs.watch(DATA_DIR, (eventType, filename) => {
        if (filename === "state.json") {
          console.log(`[SSE_WATCH] Detected change in ${filename}, triggering push.`);
          sendState();
        }
      });

      // 3. Log Streaming
      let lastLogSize = 0;
      if (fs.existsSync(LOG_FILE)) {
        lastLogSize = fs.statSync(LOG_FILE).size;
      }

      const sendLogs = () => {
        try {
          if (!fs.existsSync(LOG_FILE)) return;
          const currentSize = fs.statSync(LOG_FILE).size;
          if (currentSize > lastLogSize) {
            const buffer = Buffer.alloc(currentSize - lastLogSize);
            const fd = fs.openSync(LOG_FILE, "r");
            fs.readSync(fd, buffer, 0, currentSize - lastLogSize, lastLogSize);
            fs.closeSync(fd);
            
            const lines = buffer.toString("utf-8").split("\n").filter(l => l.trim());
            lines.forEach(line => {
              try {
                // eslint-disable-next-line @typescript-eslint/no-explicit-any
                const logObj: any = { message: line, timestamp: new Date().toISOString(), level: "INFO" };
                if (line.includes(" - ")) {
                  const parts = line.split(" - ");
                  logObj.timestamp = parts[0];
                  logObj.message = parts.slice(1).join(" - ");
                }
                controller.enqueue(encoder.encode(`event: log\ndata: ${JSON.stringify(logObj)}\n\n`));
              } catch {
                // ignore
              }
            });
            lastLogSize = currentSize;
          }
        } catch {
          // ignore
        }
      };

      const logInterval = setInterval(sendLogs, 1000);

      // 4. Cleanup
      req.signal.addEventListener("abort", () => {
        stateWatcher.close();
        clearInterval(logInterval);
        try { controller.close(); } catch { /* ignore */ }
      });
    },
  });

  return new Response(stream, {
    headers: {
      "Content-Type": "text/event-stream",
      "Cache-Control": "no-cache",
      "Connection": "keep-alive",
    },
  });
}
