import { NextResponse } from "next/server";
import fs from "fs";
import path from "path";
import { resolveWithinMcpRoot } from "@/lib/operatorPaths";

export async function GET(request: Request): Promise<Response> {
  const { searchParams } = new URL(request.url);
  const targetPath = searchParams.get("path") || ".";

  try {
    const current = resolveWithinMcpRoot(targetPath);
    if (!fs.existsSync(current) || !fs.statSync(current).isDirectory()) {
      return NextResponse.json({ error: "Path not found" }, { status: 404 });
    }

    const entries = fs.readdirSync(current).filter((entry) => !entry.startsWith("."));
    const folders = entries.filter((entry) => fs.statSync(path.join(current, entry)).isDirectory());
    const files = entries.filter((entry) => fs.statSync(path.join(current, entry)).isFile());

    return NextResponse.json({ current, folders, files });
  } catch (error) {
    console.error("Browser API Error:", error);
    return NextResponse.json({
      error: error instanceof Error ? error.message : "Path traversal failed",
    }, { status: 500 });
  }
}
