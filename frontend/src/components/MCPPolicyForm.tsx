import React, { useState } from 'react';
import { MCPPolicy, MCPControlLevel } from '../types/mcp';
import { MCPService } from '../services/mcpService';

export const MCPPolicyForm: React.FC = () => {
    const [policy, setPolicy] = useState<MCPPolicy>({
        name: '',
        controlLevel: MCPControlLevel.MODERATE,
        allowedModels: [],
        restrictedActions: [],
        safetyChecks: {}
    });

    const mcpService = new MCPService();

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        await mcpService.registerPolicy(policy);
    };

    return (
        <form onSubmit={handleSubmit}>
            <div>
                <label>Policy Name:</label>
                <input
                    type="text"
                    value={policy.name}
                    onChange={e => setPolicy({...policy, name: e.target.value})}
                />
            </div>
            <div>
                <label>Control Level:</label>
                <select
                    value={policy.controlLevel}
                    onChange={e => setPolicy({...policy, controlLevel: e.target.value as MCPControlLevel})}
                >
                    {Object.values(MCPControlLevel).map(level => (
                        <option key={level} value={level}>{level}</option>
                    ))}
                </select>
            </div>
            <button type="submit">Save Policy</button>
        </form>
    );
}
