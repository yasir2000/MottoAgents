import { MCPPolicy } from '../types/mcp';

export class MCPService {
    private baseUrl = '/api/mcp';

    async validateModelUsage(model: string, context: Record<string, any>): Promise<boolean> {
        const response = await fetch(`${this.baseUrl}/validate`, {
            method: 'POST',
            body: JSON.stringify({ model, context }),
            headers: { 'Content-Type': 'application/json' }
        });
        return response.json();
    }

    async registerPolicy(policy: MCPPolicy): Promise<void> {
        await fetch(`${this.baseUrl}/policy`, {
            method: 'POST',
            body: JSON.stringify(policy),
            headers: { 'Content-Type': 'application/json' }
        });
    }
}
