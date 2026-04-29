import { NextRequest } from "next/server";
import fs from "fs";
import path from "path";
import { getLogsPath, getStatePath } from "@/lib/operatorPaths";
import { listCircuitNames, readCircuitDetails, readSystemState } from "@/lib/operatorStore";

interface LogPayload {
  message: string;
  timestamp: string;
  level: string;
  category: string;
}

function buildStatePayload() {
  const state = readSystemState();
  const circuits = listCircuitNames();
  const activeCircuit = circuits.includes(state.active_circuit) ? state.active_circuit : circuits[0] || "mcp";
  return {
    ...state,
    active_circuit: activeCircuit,
    circuits,
    registered_circuits: circuits,
    active_circuit_details: circuits.includes(activeCircuit) ? readCircuitDetails(activeCircuit) : null,
  };
}

function parseLogLine(line: string): LogPayload {
  if (line.includes(" - ")) {
    const parts = line.split(" - ");
    return {
      timestamp: parts[0],
      message: parts.slice(1).join(" - "),
      level: "INFO",
      category: "ENGINE",
    };
  }

  return {
    timestamp: new Date().toISOString(),
    message: line,
    level: line.includes("ERROR") ? "ERROR" : "INFO",
    category: "ENGINE",
  };
}

export async function GET(req: NextRequest) {
  const encoder = new TextEncoder();
  const statePath = getStatePath();
  const dataDir = path.dirname(statePath);
  const logFile = getLogsPath();

  const stream = new ReadableStream({
    async start(controller) {
      const sendState = () => {
        try {
          const payload = buildStatePayload();
          controller.enqueue(encoder.encode(`event: state\ndata: ${JSON.stringify(payload)}\n\n`));
        } catch (error) {
          console.warn("[SSE_SEND] State sync skipped:", error instanceof Error ? error.message : "Unknown");
        }
      };

      sendState();

      const stateWatcher = fs.existsSync(dataDir)
        ? fs.watch(dataDir, (_eventType, filename) => {
            if (filename === "state.json") sendState();
          })
        : null;

      let lastLogSize = fs.existsSync(logFile) ? fs.statSync(logFile).size : 0;

      const sendLogs = () => {
        try {
          if (!fs.existsSync(logFile)) return;
          const currentSize = fs.statSync(logFile).size;
          if (currentSize <= lastLogSize) return;

          const buffer = Buffer.alloc(currentSize - lastLogSize);
          const fd = fs.openSync(logFile, "r");
          fs.readSync(fd, buffer, 0, currentSize - lastLogSize, lastLogSize);
          fs.closeSync(fd);

          buffer.toString("utf-8")
            .split("\n")
            .filter((line) => line.trim())
            .forEach((line) => {
              controller.enqueue(encoder.encode(`event: log\ndata: ${JSON.stringify(parseLogLine(line))}\n\n`));
            });

          lastLogSize = currentSize;
        } catch {
          // SSE streams should stay alive through transient file read errors.
        }
      };

      const logInterval = setInterval(sendLogs, 1000);

      req.signal.addEventListener("abort", () => {
        stateWatcher?.close();
        clearInterval(logInterval);
        try { controller.close(); } catch { /* stream already closed */ }
      });
    },
  });

  return new Response(stream, {
    headers: {
      "Content-Type": "text/event-stream",
      "Cache-Control": "no-cache",
      Connection: "keep-alive",
    },
  });
}
