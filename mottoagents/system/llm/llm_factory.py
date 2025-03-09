"""
LLM factory for creating appropriate LLM instances based on configuration.
"""

from typing import Optional
from mottoagents.system.config import Config
from .base_llm import BaseLLM
from .openai_llm import OpenAILLM
from .claude_llm import ClaudeLLM
from .ollama_llm import OllamaLLM

class LLMFactory:
    """Factory class for creating LLM instances."""

    @staticmethod
    def create_llm(config: Config) -> BaseLLM:
        """Create an LLM instance based on configuration.
        
        Args:
            config (Config): System configuration
            
        Returns:
            BaseLLM: Appropriate LLM instance
            
        Raises:
            ValueError: If model type is not supported
        """
        model_type = config.model_type.lower()
        
        if model_type == "openai":
            return OpenAILLM(config)
        elif model_type == "claude":
            return ClaudeLLM(config)
        elif model_type == "ollama":
            return OllamaLLM(config)
        else:
            raise ValueError(f"Unsupported model type: {model_type}")

    @staticmethod
    def get_default_llm(config: Config) -> BaseLLM:
        """Get default LLM instance based on configuration.
        
        This method implements a fallback strategy:
        1. Try Ollama if available (for cost-free local inference)
        2. Fall back to OpenAI if Ollama is not available
        3. Use Claude as final fallback
        
        Args:
            config (Config): System configuration
            
        Returns:
            BaseLLM: Default LLM instance
        """
        try:
            if config.model_type == "ollama":
                return OllamaLLM(config)
        except Exception:
            pass

        if config.openai_api_key:
            return OpenAILLM(config)
        elif config.claude_api_key:
            return ClaudeLLM(config)
        else:
            # Default to Ollama with basic model
            config.model_type = "ollama"
            config.ollama_model = "llama2"
            return OllamaLLM(config) 