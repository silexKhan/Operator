import { SystemStatus, CircuitDetails } from "@/types/mcp";

export class McpClient {
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
    return data.registered_circuits || data.circuits || [];
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

  async getDashboard(): Promise<unknown> {
    const res = await fetch(this.baseUrl);
    if (!res.ok) throw new Error("Failed to fetch dashboard");
    return res.json();
  }
}

export const mcpClient = new McpClient();
