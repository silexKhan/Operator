import { SystemStatus, CircuitDetails } from "@/types/mcp";

class McpClient {
  private baseUrl: string = "/api/mcp";

  async getStatus(): Promise<SystemStatus> {
    const res = await fetch(`${this.baseUrl}/state`);
    if (!res.ok) throw new Error("Failed to fetch status");
    return res.json();
  }

  async getCircuits(): Promise<string[]> {
    const res = await fetch(`${this.baseUrl}/state`);
    if (!res.ok) throw new Error("Failed to fetch circuits");
    const data = await res.json();
    return data.registered_circuits || [];
  }

  async getCircuitDetails(name: string): Promise<CircuitDetails> {
    const res = await fetch(`${this.baseUrl}/protocols?type=circuit_full&name=${name}`);
    if (!res.ok) throw new Error("Failed to fetch circuit details");
    return res.json();
  }

  async updateCircuit(name: string, data: Partial<CircuitDetails>): Promise<boolean> {
    const res = await fetch(`${this.baseUrl}/update`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        target: "circuit_overview",
        name,
        data
      })
    });
    return res.ok;
  }

  async callTool(circuit: string, tool: string, _arguments: Record<string, unknown>): Promise<unknown> {
    const res = await fetch(`${this.baseUrl}/execute`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        circuit,
        action: tool,
        params: _arguments
      })
    });
    if (!res.ok) throw new Error("Tool execution failed");
    return res.json();
  }
}

export const mcpClient = new McpClient();
