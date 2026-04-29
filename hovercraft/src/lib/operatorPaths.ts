import path from "path";

const SAFE_NAME_PATTERN = /^[A-Za-z0-9_-]+$/;

export function getMcpRoot(): string {
  if (process.env.MCP_ROOT) {
    return path.resolve(process.env.MCP_ROOT);
  }

  const cwd = process.cwd();
  return path.basename(cwd) === "hovercraft" ? path.resolve(cwd, "..") : cwd;
}

export function assertSafeName(name: string): string {
  const normalized = name.trim();
  if (!SAFE_NAME_PATTERN.test(normalized)) {
    throw new Error(`Unsafe registry name: ${name}`);
  }
  return normalized;
}

export function getStatePath(): string {
  return path.join(getMcpRoot(), "data", "state.json");
}

export function getMissionPath(): string {
  return path.join(getMcpRoot(), "mission.json");
}

export function getLogsPath(): string {
  return path.join(getMcpRoot(), "logs", "server.log");
}

export function getGlobalProtocolsPath(): string {
  return path.join(getMcpRoot(), "mcp_operator", "engine", "protocols.json");
}

export function getCircuitsRegistryPath(): string {
  return path.join(getMcpRoot(), "mcp_operator", "registry", "circuits", "registry");
}

export function getCircuitPath(name: string): string {
  return path.join(getCircuitsRegistryPath(), assertSafeName(name.toLowerCase()));
}

export function getUnitsRegistryPath(): string {
  return path.join(getMcpRoot(), "mcp_operator", "registry", "units");
}

export function getUnitPath(name: string): string {
  return path.join(getUnitsRegistryPath(), assertSafeName(name.toLowerCase()));
}

export function resolveWithinMcpRoot(targetPath: string): string {
  const root = getMcpRoot();
  const resolved = path.resolve(root, targetPath);
  if (resolved !== root && !resolved.startsWith(`${root}${path.sep}`)) {
    throw new Error(`Path escapes MCP root: ${targetPath}`);
  }
  return resolved;
}
