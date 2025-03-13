from typing import Dict, Type
from .bmm import BMMContext
from ..roles import Role, BusinessArchitect

class MottoAgentsFactory:
    def __init__(self, bmm_context: BMMContext):
        self.bmm_context = bmm_context
        self.role_templates = {}
        self.action_templates = {}

    async def create_role(self, role_type: str, config: Dict) -> Role:
        """Create role with BMM context"""
        role_class = self.role_templates.get(role_type)
        if not role_class:
            raise ValueError(f"Unknown role type: {role_type}")
            
        config['bmm_context'] = self.bmm_context
        return role_class(**config)

    async def create_business_architect(self, config: Dict) -> BusinessArchitect:
        """Create BusinessArchitect with full BMM capabilities"""
        return BusinessArchitect(
            bmm_context=self.bmm_context,
            **config
        )
