from typing import Dict, List, Optional
from .base import Memory

class BMMMemory(Memory):
    def __init__(self):
        super().__init__()
        self.objective_index = {}
        self.strategy_index = {}

    def add_with_context(self, message: Dict, bmm_context: Dict):
        """Add memory with BMM context"""
        message["bmm_context"] = bmm_context
        if objective := bmm_context.get("objective"):
            self.objective_index.setdefault(objective, []).append(message)
        super().add(message)

    def get_by_objective(self, objective_id: str) -> List[Dict]:
        """Get memories related to specific objective"""
        return self.objective_index.get(objective_id, [])

    def get_strategic_context(self, strategy_id: str) -> Optional[Dict]:
        """Get strategic context for decision making"""
        return self.strategy_index.get(strategy_id)

    def _index_bmm_context(self, message: Dict, bmm_context: Dict):
        """Index message by BMM context elements"""
        for context_type, value in bmm_context.items():
            if isinstance(value, dict):
                for key, data in value.items():
                    self._add_to_index(f"{context_type}_{key}", message)

    def _add_to_index(self, index_key: str, message: Dict):
        """Add message to specific index"""
        if not hasattr(self, f"{index_key}_index"):
            setattr(self, f"{index_key}_index", {})
        index = getattr(self, f"{index_key}_index")
        index.setdefault(str(message["id"]), []).append(message)
