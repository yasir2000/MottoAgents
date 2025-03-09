from typing import List, Dict, Any
from pydantic import BaseModel
from .action import Action, ActionOutput
from mottoagents.system.schema import Message

class MotivationState(BaseModel):
    """Represents the current motivation state of a user/agent"""
    energy_level: float = 1.0  # 0.0 to 1.0
    focus_level: float = 1.0   # 0.0 to 1.0
    mood: str = "neutral"      # positive, neutral, negative
    goals_progress: Dict[str, float] = {}
    recent_achievements: List[str] = []

class AssessMotivationAction(Action):
    """Assesses current motivation level and state"""
    
    async def run(self, messages: List[Message]) -> ActionOutput:
        # Analyze recent messages to assess motivation
        motivation_state = self._analyze_motivation(messages)
        return ActionOutput(
            content=self._format_motivation_assessment(motivation_state),
            instruct_content={"motivation_state": motivation_state.dict()}
        )
    
    def _analyze_motivation(self, messages: List[Message]) -> MotivationState:
        if not messages:
            return MotivationState()
            
        # Analyze message content for motivation indicators
        energy_indicators = 0
        focus_indicators = 0
        mood_score = 0
        
        for msg in messages[-10:]:  # Look at last 10 messages
            content = msg.content.lower()
            
            # Energy analysis
            if any(word in content for word in ["excited", "energetic", "motivated"]):
                energy_indicators += 1
            elif any(word in content for word in ["tired", "exhausted", "drained"]):
                energy_indicators -= 1
                
            # Focus analysis    
            if any(word in content for word in ["focused", "concentrated", "determined"]):
                focus_indicators += 1
            elif any(word in content for word in ["distracted", "confused", "overwhelmed"]):
                focus_indicators -= 1
                
            # Mood analysis
            if any(word in content for word in ["happy", "excited", "great", "good"]):
                mood_score += 1
            elif any(word in content for word in ["sad", "frustrated", "angry", "bad"]):
                mood_score -= 1
        
        # Calculate normalized scores
        energy_level = min(max((energy_indicators + 5) / 10, 0.0), 1.0)
        focus_level = min(max((focus_indicators + 5) / 10, 0.0), 1.0)
        mood = "positive" if mood_score > 0 else "negative" if mood_score < 0 else "neutral"
        
        return MotivationState(
            energy_level=energy_level,
            focus_level=focus_level,
            mood=mood
        )
    
    def _format_motivation_assessment(self, state: MotivationState) -> str:
        energy_desc = "high" if state.energy_level > 0.7 else "moderate" if state.energy_level > 0.3 else "low"
        focus_desc = "strong" if state.focus_level > 0.7 else "moderate" if state.focus_level > 0.3 else "weak"
        
        return f"Current motivation assessment:\n" \
               f"- Energy level is {energy_desc} ({state.energy_level:.1%})\n" \
               f"- Focus level is {focus_desc} ({state.focus_level:.1%})\n" \
               f"- Overall mood appears to be {state.mood}"

class GenerateMotivationAction(Action):
    """Generates motivational responses based on current state"""
    
    async def run(self, messages: List[Message]) -> ActionOutput:
        # Get the most recent motivation state if available
        motivation_state = None
        for msg in reversed(messages):
            if msg.instruct_content and "motivation_state" in msg.instruct_content:
                motivation_state = MotivationState(**msg.instruct_content["motivation_state"])
                break
        
        if not motivation_state:
            motivation_state = MotivationState()
        
        response = self._generate_motivation_response(motivation_state)
        return ActionOutput(
            content=response,
            instruct_content={"type": "motivation", "response": response}
        )
    
    def _generate_motivation_response(self, state: MotivationState) -> str:
        if state.energy_level < 0.3:
            return self._generate_energy_boost_response()
        elif state.focus_level < 0.3:
            return self._generate_focus_enhancement_response()
        elif state.mood == "negative":
            return self._generate_mood_improvement_response()
        else:
            return self._generate_maintenance_response()
    
    def _generate_energy_boost_response(self) -> str:
        return ("I notice your energy might be a bit low. Let's break this down into smaller, " 
                "manageable steps. What's the smallest action you could take right now that would " 
                "move you forward? Remember, even small progress is still progress.")
    
    def _generate_focus_enhancement_response(self) -> str:
        return ("It seems like you might be feeling a bit scattered. Let's try to center ourselves. " 
                "What's the single most important thing you want to accomplish? Let's focus just on " 
                "that for now, and I'll help you stay on track.")
    
    def _generate_mood_improvement_response(self) -> str:
        return ("I understand things might feel challenging right now. But remember, you've overcome " 
                "obstacles before. Let's focus on what you can control and take it one step at a time. " 
                "What's one positive thing we could work on right now?")
    
    def _generate_maintenance_response(self) -> str:
        return ("You're doing great! Your energy and focus are strong. Let's maintain this momentum. " 
                "What's your next goal? I'm here to help you achieve it.") 