from typing import List, Dict, Any, Optional
from .bdi_agent import BDIAgent, Belief, Desire, Intention, BDIContext
from mottoagents.actions.motivation_actions import (
    AssessMotivationAction,
    GenerateMotivationAction,
    MotivationState
)
from mottoagents.system.schema import Message
from mottoagents.actions import ActionOutput

class MotivationBelief(Belief):
    """Extended belief for motivation-specific information"""
    motivation_state: MotivationState
    user_goals: List[str] = []
    intervention_history: List[Dict[str, Any]] = []

class MotivationDesire(Desire):
    """Extended desire for motivation-specific goals"""
    target_state: Dict[str, float] = {}  # Desired levels for energy, focus, etc.
    intervention_type: str = "general"    # Type of motivation intervention needed
    urgency: float = 0.5                 # How urgent is this desire (0.0 to 1.0)

class MotivationIntention(Intention):
    """Extended intention for motivation-specific plans"""
    intervention_steps: List[str] = []    # Specific steps in the motivation plan
    feedback_required: bool = True        # Whether user feedback is needed
    adaptation_history: List[str] = []    # History of plan adaptations

class MotivationContext(BDIContext):
    """Extended context for motivation-specific state"""
    current_motivation_state: Optional[MotivationState] = None
    intervention_history: List[Dict[str, Any]] = []
    user_preferences: Dict[str, Any] = {}

class MotivationAgent(BDIAgent):
    """A BDI agent specialized in providing motivation and encouragement"""
    
    def __init__(self, name="MotivationAgent", profile="Motivation Coach", 
                 goal="Help users maintain high motivation and achieve their goals",
                 constraints="Be encouraging but realistic, respect user boundaries"):
        super().__init__(name=name, profile=profile, goal=goal, constraints=constraints)
        self._rc = MotivationContext()
        self._init_actions([
            AssessMotivationAction(),
            GenerateMotivationAction()
        ])
        
    async def update_beliefs(self, message: Message) -> None:
        """Update beliefs with motivation-specific information"""
        # First, update general beliefs
        await super().update_beliefs(message)
        
        # Then, handle motivation-specific belief updates
        if message.instruct_content and "motivation_state" in message.instruct_content:
            motivation_state = MotivationState(**message.instruct_content["motivation_state"])
            belief = MotivationBelief(
                name=f"motivation_state_{len(self._rc.beliefs)}",
                confidence=1.0,
                timestamp=message.timestamp if hasattr(message, 'timestamp') else 0.0,
                data={"type": "motivation_assessment"},
                motivation_state=motivation_state
            )
            self._rc.beliefs[belief.name] = belief
            self._rc.current_motivation_state = motivation_state

    async def generate_desires(self) -> None:
        """Generate motivation-specific desires based on current beliefs"""
        await super().generate_desires()
        
        if not self._rc.current_motivation_state:
            return
            
        state = self._rc.current_motivation_state
        
        # Generate desires based on motivation state
        if state.energy_level < 0.3:
            desire = MotivationDesire(
                name=f"boost_energy_{len(self._rc.desires)}",
                priority=0.9,
                conditions=["user_receptive", "has_energy_intervention"],
                success_criteria=["energy_level_improved"],
                target_state={"energy_level": 0.7},
                intervention_type="energy_boost",
                urgency=0.8
            )
            self._rc.desires[desire.name] = desire
            
        if state.focus_level < 0.3:
            desire = MotivationDesire(
                name=f"improve_focus_{len(self._rc.desires)}",
                priority=0.85,
                conditions=["user_receptive", "has_focus_intervention"],
                success_criteria=["focus_level_improved"],
                target_state={"focus_level": 0.7},
                intervention_type="focus_enhancement",
                urgency=0.7
            )
            self._rc.desires[desire.name] = desire
            
        if state.mood == "negative":
            desire = MotivationDesire(
                name=f"improve_mood_{len(self._rc.desires)}",
                priority=0.95,
                conditions=["user_receptive", "has_mood_intervention"],
                success_criteria=["mood_improved"],
                target_state={"mood": "positive"},
                intervention_type="mood_improvement",
                urgency=0.9
            )
            self._rc.desires[desire.name] = desire

    def _generate_action_plan(self, desire_name: str) -> List[str]:
        """Generate motivation-specific action plans"""
        desire = self._rc.desires[desire_name]
        if not isinstance(desire, MotivationDesire):
            return super()._generate_action_plan(desire_name)
            
        # Create a plan based on the intervention type
        if desire.intervention_type == "energy_boost":
            return [
                "assess_current_energy",
                "identify_energy_drains",
                "suggest_energy_management",
                "provide_encouragement",
                "check_progress"
            ]
        elif desire.intervention_type == "focus_enhancement":
            return [
                "assess_distractions",
                "set_clear_goals",
                "break_down_tasks",
                "establish_focus_routine",
                "monitor_progress"
            ]
        elif desire.intervention_type == "mood_improvement":
            return [
                "acknowledge_feelings",
                "identify_mood_triggers",
                "suggest_positive_actions",
                "provide_support",
                "check_emotional_state"
            ]
        return ["assess_situation", "provide_motivation", "check_response"]

    async def _act(self) -> Message:
        """Execute motivation-specific actions"""
        if self._rc.current_intention and isinstance(self._rc.current_intention, MotivationIntention):
            # Execute the current step in the motivation plan
            current_step = self._rc.current_intention.intervention_steps[0]
            response = await self._execute_motivation_step(current_step)
            
            # Update the intention's progress
            self._rc.current_intention.intervention_steps.pop(0)
            self._rc.current_intention.progress = 1.0 - (
                len(self._rc.current_intention.intervention_steps) / 
                len(self._generate_action_plan(self._rc.current_intention.desire))
            )
            
            return Message(
                content=response.content,
                instruct_content=response.instruct_content,
                role=self.profile,
                cause_by=type(self._rc.todo)
            )
            
        return await super()._act()
        
    async def _execute_motivation_step(self, step: str) -> ActionOutput:
        """Execute a specific step in the motivation plan"""
        # Use the appropriate motivation action based on the step
        if step.startswith("assess"):
            return await self._actions[0].run(self._rc.important_memory)  # AssessMotivationAction
        else:
            return await self._actions[1].run(self._rc.important_memory)  # GenerateMotivationAction

    async def handle(self, message: Message) -> Message:
        """Handle incoming messages with motivation-specific processing"""
        # First, assess the motivation state
        assessment = await self._actions[0].run([message])
        self.recv(Message(
            content=assessment.content,
            instruct_content=assessment.instruct_content,
            role=self.profile,
            cause_by=type(self._actions[0])
        ))
        
        # Then handle the message with the standard BDI cycle
        return await super().handle(message) 