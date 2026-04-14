import { NextResponse } from "next/server";
import fs from "fs";
import path from "path";

export async function GET() {
  const LOG_PATH = path.join(process.cwd(), "..", "logs", "mcp_server.log");
  
  try {
    if (fs.existsSync(LOG_PATH)) {
      const content = fs.readFileSync(LOG_PATH, "utf-8");
      const lines = content.split("\n").filter(l => l.trim()).slice(-100);
      
      const parsedLogs = lines.map(line => {
        if (line.includes(" - ")) {
          const parts = line.split(" - ");
          return { timestamp: parts[0], message: parts.slice(1).join(" - "), level: "INFO" };
        }
        return { timestamp: new Date().toISOString(), message: line, level: "INFO" };
      });
      
      return NextResponse.json({ logs: parsedLogs });
    }
    return NextResponse.json({ logs: [] });
  } catch {
    return NextResponse.json({ error: "Failed to read logs" }, { status: 500 });
  }
}
