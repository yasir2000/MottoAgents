from typing import Dict, List, Optional, Set, Type
from pydantic import BaseModel, Field
from .role import Role, RoleContext
from mottoagents.actions import Action
from mottoagents.system.schema import Message

class Belief(BaseModel):
    """Represents a belief about the environment"""
    name: str
    confidence: float = 1.0  # Confidence level in this belief
    timestamp: float  # When this belief was last updated
    data: dict  # Actual belief data

class Desire(BaseModel):
    """Represents a goal the agent wants to achieve"""
    name: str
    priority: float  # Priority level of this desire
    conditions: List[str]  # Conditions that must be met
    success_criteria: List[str]  # Criteria to determine if desire is achieved

class Intention(BaseModel):
    """Represents a committed plan to achieve a desire"""
    desire: str  # Reference to the desire this intention aims to fulfill
    actions: List[str]  # Sequence of actions to take
    status: str = "pending"  # pending, active, completed, failed
    progress: float = 0.0  # Progress towards completion

class BDIContext(RoleContext):
    """Extended context for BDI agents"""
    beliefs: Dict[str, Belief] = Field(default_factory=dict)
    desires: Dict[str, Desire] = Field(default_factory=dict)
    intentions: Dict[str, Intention] = Field(default_factory=dict)
    current_intention: Optional[str] = None

class BDIAgent(Role):
    """A BDI-based agent that can handle intents"""
    
    def __init__(self, name="", profile="BDI Agent", goal="", constraints="", desc=""):
        super().__init__(name=name, profile=profile, goal=goal, constraints=constraints, desc=desc)
        self._rc = BDIContext()  # Override with BDI-specific context

    async def update_beliefs(self, message: Message) -> None:
        """Update agent's beliefs based on new information"""
        # Extract relevant information from message
        if not message.content:
            return
            
        # Update beliefs based on message content
        belief = Belief(
            name=f"belief_{len(self._rc.beliefs)}",
            confidence=1.0,
            timestamp=message.timestamp if hasattr(message, 'timestamp') else 0.0,
            data={"source": message.role, "content": message.content}
        )
        self._rc.beliefs[belief.name] = belief

    async def generate_desires(self) -> None:
        """Generate new desires based on current beliefs and goals"""
        # Analyze beliefs to generate appropriate desires
        for belief in self._rc.beliefs.values():
            # Example: If belief contains a question, generate desire to answer it
            if "?" in belief.data.get("content", ""):
                desire = Desire(
                    name=f"answer_{len(self._rc.desires)}",
                    priority=0.8,
                    conditions=[f"has_relevant_knowledge_{belief.name}"],
                    success_criteria=["answer_provided"]
                )
                self._rc.desires[desire.name] = desire

    async def select_intention(self) -> None:
        """Select the most appropriate intention based on current desires"""
        if not self._rc.desires:
            return

        # Select highest priority desire that doesn't have an active intention
        active_desires = {i.desire for i in self._rc.intentions.values() if i.status == "active"}
        available_desires = set(self._rc.desires.keys()) - active_desires

        if not available_desires:
            return

        selected_desire = max(
            available_desires,
            key=lambda d: self._rc.desires[d].priority
        )

        # Create new intention for selected desire
        intention = Intention(
            desire=selected_desire,
            actions=self._generate_action_plan(selected_desire)
        )
        self._rc.intentions[f"intention_{len(self._rc.intentions)}"] = intention
        self._rc.current_intention = intention

    def _generate_action_plan(self, desire_name: str) -> List[str]:
        """Generate a plan of actions to achieve the given desire"""
        desire = self._rc.desires[desire_name]
        # Simple example: create a basic plan based on desire conditions
        return [f"check_{cond}" for cond in desire.conditions] + ["execute_main_action"]

    async def _think(self) -> None:
        """Override think to implement BDI reasoning cycle"""
        # Update beliefs based on recent messages
        for msg in self._rc.memory.get():
            await self.update_beliefs(msg)

        # Generate new desires based on updated beliefs
        await self.generate_desires()

        # Select new intention if needed
        if not self._rc.current_intention:
            await self.select_intention()

        # Default to parent class behavior for action selection
        await super()._think()

    async def handle(self, message: Message) -> Message:
        """Handle incoming messages with BDI reasoning"""
        # Update beliefs based on new message
        await self.update_beliefs(message)
        
        # Run normal message handling
        return await super().handle(message)

    async def run(self, message=None):
        """Run the BDI agent's reasoning cycle"""
        if message:
            await self.update_beliefs(Message(message) if isinstance(message, str) else message)
        
        # Run the main agent loop with BDI reasoning
        return await super().run(message) 