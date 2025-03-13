from typing import Dict, List
from .architecture import MottoAgentsArchitecture
from .bmm import BMMContext

class MottoAgentsOrchestrator:
    def __init__(self):
        self.architecture = MottoAgentsArchitecture()
        self.active_roles = {}
        self.policy_engine = None
        
    async def initialize_bmm_environment(self, config: Dict):
        """Initialize BMM environment"""
        self.policy_engine = self._setup_policy_engine(config)
        await self._initialize_business_architect()
        await self._setup_bmm_monitoring()

    async def execute_task(self, task: Dict) -> Dict:
        """Execute task with BMM awareness"""
        # Validate against BMM
        if not await self.validate_task_compliance(task):
            return {"status": "failed", "reason": "BMM compliance failure"}
            
        # Execute with BMM context
        return await self._execute_with_bmm(task)

    async def validate_task_compliance(self, task: Dict) -> bool:
        """Validate task against BMM framework"""
        return (
            await self.policy_engine.validate(task) and
            await self.architecture.validate_bmm_compliance(task)
        )
