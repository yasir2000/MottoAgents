from typing import Dict, List
from .bmm import BMMContext
from ..memory import BMMMemory

class MottoAgentsArchitecture:
    def __init__(self):
        self.bmm_context = BMMContext()
        self.memory_manager = BMMMemory()
        self.role_registry = {}
        self.action_registry = {}
        
    async def register_role(self, role_id: str, role_config: Dict):
        """Register role with BMM context"""
        if 'bmm_settings' in role_config:
            role_config['bmm_context'] = self.bmm_context
        self.role_registry[role_id] = role_config

    async def execute_action_chain(self, actions: List[Dict]) -> Dict:
        """Execute actions with BMM validation"""
        for action in actions:
            if not await self.validate_bmm_compliance(action):
                raise ValueError(f"Action {action['name']} violates BMM directives")
        return await self._execute_validated_chain(actions)

    async def validate_bmm_compliance(self, action: Dict) -> bool:
        """Validate action against BMM framework"""
        return (
            self.bmm_context.validate_action(action) and
            self.bmm_context.align_with_strategy(action)
        )
