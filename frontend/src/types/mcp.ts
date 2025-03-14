export enum MCPControlLevel {
    STRICT = "strict",
    MODERATE = "moderate",
    PERMISSIVE = "permissive"
}

export interface MCPPolicy {
    name: string;
    controlLevel: MCPControlLevel;
    allowedModels: string[];
    restrictedActions: string[];
    safetyChecks: Record<string, boolean>;
}
