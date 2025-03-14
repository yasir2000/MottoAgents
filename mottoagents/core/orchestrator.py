from typing import Dict, List
from .architecture import MottoAgentsArchitecture
from .bmm import BMMContext
from .mcp import ModelControlProtocol

class MottoAgentsOrchestrator:
    def __init__(self):
        self.architecture = MottoAgentsArchitecture()
        self.active_roles = {}
        self.policy_engine = None
        self.mcp_controller = None
        
    async def initialize_bmm_environment(self, config: Dict):
        """Initialize BMM environment with MCP"""
        self.policy_engine = self._setup_policy_engine(config)
        await self._initialize_business_architect()
        await self._setup_bmm_monitoring()
        self.mcp_controller = ModelControlProtocol(config)
        await self._setup_mcp_controls()

    async def execute_task(self, task: Dict) -> Dict:
        """Execute task with BMM and MCP validation"""
        # Validate against BMM
        if not await self.validate_task_compliance(task):
            return {"status": "failed", "reason": "BMM/MCP compliance failure"}
        
        model = task.get("model", self.default_model)
        if not await self.mcp_controller.validate_model_usage(model, task):
            return {"status": "failed", "reason": "MCP validation failure"}
            
        # Execute with BMM context
        return await self._execute_with_bmm(task)

    async def validate_task_compliance(self, task: Dict) -> bool:
        """Validate task against BMM framework"""
        return (
            await self.policy_engine.validate(task) and
            await self.architecture.validate_bmm_compliance(task)
        )
