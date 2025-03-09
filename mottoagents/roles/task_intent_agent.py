from typing import List, Dict, Any
from .bdi_agent import BDIAgent, Belief, Desire, Intention
from mottoagents.system.schema import Message
from mottoagents.actions import Action, ActionOutput

class TaskIntent:
    """Represents a task-related intent"""
    def __init__(self, name: str, parameters: Dict[str, Any] = None):
        self.name = name
        self.parameters = parameters or {}

class Taskyasir2000(BDIAgent):
    """A BDI agent specialized in handling task-related intents"""
    
    def __init__(self, name="TaskAgent", profile="Task Intent Handler", goal="Handle and execute task intents", 
                 constraints="Follow task execution protocols"):
        super().__init__(name=name, profile=profile, goal=goal, constraints=constraints)
        self.supported_intents = {
            "start_task": self._handle_start_task,
            "check_status": self._handle_check_status,
            "pause_task": self._handle_pause_task,
            "resume_task": self._handle_resume_task,
            "cancel_task": self._handle_cancel_task
        }

    async def _extract_intent(self, message: Message) -> TaskIntent:
        """Extract intent from message content"""
        content = message.content.lower()
        
        # Simple intent matching based on keywords
        if "start" in content or "begin" in content or "initiate" in content:
            return TaskIntent("start_task", {"task_description": content})
        elif "status" in content or "progress" in content:
            return TaskIntent("check_status")
        elif "pause" in content or "hold" in content:
            return TaskIntent("pause_task")
        elif "resume" in content or "continue" in content:
            return TaskIntent("resume_task")
        elif "cancel" in content or "stop" in content:
            return TaskIntent("cancel_task")
        
        return None

    async def update_beliefs(self, message: Message) -> None:
        """Update beliefs with task-specific information"""
        await super().update_beliefs(message)
        
        # Extract and store intent-related beliefs
        intent = await self._extract_intent(message)
        if intent:
            belief = Belief(
                name=f"intent_{len(self._rc.beliefs)}",
                confidence=1.0,
                timestamp=message.timestamp if hasattr(message, 'timestamp') else 0.0,
                data={"intent": intent.name, "parameters": intent.parameters}
            )
            self._rc.beliefs[belief.name] = belief

    async def generate_desires(self) -> None:
        """Generate desires based on detected intents"""
        await super().generate_desires()
        
        # Generate desires from intent beliefs
        for belief in self._rc.beliefs.values():
            if "intent" in belief.data:
                intent_name = belief.data["intent"]
                desire = Desire(
                    name=f"handle_{intent_name}_{len(self._rc.desires)}",
                    priority=0.9,  # High priority for intent handling
                    conditions=[f"can_handle_{intent_name}"],
                    success_criteria=[f"{intent_name}_handled"]
                )
                self._rc.desires[desire.name] = desire

    def _generate_action_plan(self, desire_name: str) -> List[str]:
        """Generate specific action plan for task intents"""
        desire = self._rc.desires[desire_name]
        if "handle_" in desire_name:
            intent_name = desire_name.split("handle_")[1].split("_")[0]
            return [
                f"validate_{intent_name}",
                f"prepare_{intent_name}",
                f"execute_{intent_name}",
                f"verify_{intent_name}"
            ]
        return super()._generate_action_plan(desire_name)

    async def _handle_start_task(self, parameters: Dict[str, Any]) -> ActionOutput:
        """Handle start task intent"""
        return ActionOutput(
            content=f"Starting task: {parameters.get('task_description', 'Unknown task')}",
            instruct_content={"status": "started", "task_id": f"task_{len(self._rc.beliefs)}"}
        )

    async def _handle_check_status(self, parameters: Dict[str, Any]) -> ActionOutput:
        """Handle check status intent"""
        # Get status from current intentions
        active_intentions = [i for i in self._rc.intentions.values() if i.status == "active"]
        return ActionOutput(
            content=f"Current active tasks: {len(active_intentions)}",
            instruct_content={"active_tasks": [i.desire for i in active_intentions]}
        )

    async def _handle_pause_task(self, parameters: Dict[str, Any]) -> ActionOutput:
        """Handle pause task intent"""
        if self._rc.current_intention:
            self._rc.current_intention.status = "paused"
            return ActionOutput(content="Task paused", instruct_content={"status": "paused"})
        return ActionOutput(content="No active task to pause", instruct_content={"status": "error"})

    async def _handle_resume_task(self, parameters: Dict[str, Any]) -> ActionOutput:
        """Handle resume task intent"""
        paused_intentions = [i for i in self._rc.intentions.values() if i.status == "paused"]
        if paused_intentions:
            intention = paused_intentions[0]
            intention.status = "active"
            self._rc.current_intention = intention
            return ActionOutput(content="Task resumed", instruct_content={"status": "active"})
        return ActionOutput(content="No paused task to resume", instruct_content={"status": "error"})

    async def _handle_cancel_task(self, parameters: Dict[str, Any]) -> ActionOutput:
        """Handle cancel task intent"""
        if self._rc.current_intention:
            self._rc.current_intention.status = "cancelled"
            self._rc.current_intention = None
            return ActionOutput(content="Task cancelled", instruct_content={"status": "cancelled"})
        return ActionOutput(content="No active task to cancel", instruct_content={"status": "error"})

    async def _act(self) -> Message:
        """Override act to handle intents"""
        if self._rc.current_intention and self._rc.current_intention.status == "active":
            # Find the most recent intent belief
            intent_beliefs = [b for b in self._rc.beliefs.values() if "intent" in b.data]
            if intent_beliefs:
                latest_intent = intent_beliefs[-1]
                intent_name = latest_intent.data["intent"]
                if intent_name in self.supported_intents:
                    handler = self.supported_intents[intent_name]
                    response = await handler(latest_intent.data.get("parameters", {}))
                    return Message(
                        content=response.content,
                        instruct_content=response.instruct_content,
                        role=self.profile,
                        cause_by=type(self._rc.todo)
                    )
        
        return await super()._act() 