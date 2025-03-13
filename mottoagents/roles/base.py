from ..core.bmm import BMMContext

class Role:
    def __init__(self, name: str, profile: str, **kwargs):
        self.name = name
        self.profile = profile
        self.state = None
        self.memory = None
        self.bmm = BMMContext()
        self._load_bmm_context(kwargs)

    def _load_bmm_context(self, kwargs: dict):
        """Load BMM context from kwargs"""
        if vision := kwargs.get("vision"):
            self.bmm.ends.vision = vision
        if goals := kwargs.get("goals"):
            self.bmm.ends.goals = goals
        # ...more BMM context loading...

    async def execute_action(self, action, context):
        """Execute action with BMM validation"""
        if not self.bmm.validate_action(context):
            raise ValueError("Action violates business policies")
        if not self.bmm.align_with_strategy(context):
            raise ValueError("Action not aligned with business strategy")
        return await super().execute_action(action, context)