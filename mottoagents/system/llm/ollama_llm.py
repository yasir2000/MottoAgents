"""
Ollama LLM integration for MottoAgents.
This module provides integration with Ollama's local LLM models.
"""

import aiohttp
import json
from typing import Any, Dict, Optional

from mottoagents.system.config import Config
from mottoagents.system.logs import logger
from .base_llm import BaseLLM

class OllamaLLM(BaseLLM):
    """Ollama LLM implementation for local model inference."""

    def __init__(self, config: Config):
        """Initialize Ollama LLM.
        
        Args:
            config (Config): System configuration
        """
        super().__init__()
        self.config = config
        self.host = config.ollama_host or "http://localhost:11434"
        self.model = config.ollama_model or "llama2"
        self.timeout = config.ollama_timeout or 30
        self.parameters = config.ollama_parameters or {}

    async def _make_request(self, endpoint: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Make HTTP request to Ollama API.
        
        Args:
            endpoint (str): API endpoint
            data (Dict[str, Any]): Request data
            
        Returns:
            Dict[str, Any]: Response data
            
        Raises:
            ConnectionError: If Ollama server is not running
            Exception: For other API errors
        """
        url = f"{self.host}/{endpoint}"
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(url, json=data, timeout=self.timeout) as response:
                    if response.status != 200:
                        error_text = await response.text()
                        raise Exception(f"Ollama API error: {error_text}")
                    return await response.json()
        except aiohttp.ClientConnectorError:
            raise ConnectionError("Ollama server not running")
        except Exception as e:
            logger.error(f"Ollama request failed: {str(e)}")
            raise

    async def aask(self, prompt: str, system_prompt: Optional[str] = None) -> str:
        """Send a prompt to the Ollama model and get a response.
        
        Args:
            prompt (str): The prompt to send
            system_prompt (Optional[str]): System prompt for context
            
        Returns:
            str: Model response
            
        Raises:
            Exception: If the request fails
        """
        data = {
            "model": self.model,
            "prompt": prompt,
            "stream": False,
            **self.parameters
        }
        
        if system_prompt:
            data["system"] = system_prompt

        try:
            response = await self._make_request("api/generate", data)
            return response.get("response", "")
        except Exception as e:
            logger.error(f"Failed to get response from Ollama: {str(e)}")
            raise

    async def aask_batch(self, prompts: list[str]) -> list[str]:
        """Send multiple prompts to the Ollama model.
        
        Args:
            prompts (list[str]): List of prompts to process
            
        Returns:
            list[str]: List of model responses
        """
        responses = []
        for prompt in prompts:
            try:
                response = await self.aask(prompt)
                responses.append(response)
            except Exception as e:
                logger.error(f"Batch processing failed for prompt: {str(e)}")
                responses.append("")
        return responses

    async def get_embedding(self, text: str) -> list[float]:
        """Get embeddings for text using Ollama model.
        
        Args:
            text (str): Text to embed
            
        Returns:
            list[float]: Embedding vector
            
        Raises:
            Exception: If embedding generation fails
        """
        data = {
            "model": self.model,
            "prompt": text
        }
        
        try:
            response = await self._make_request("api/embeddings", data)
            return response.get("embedding", [])
        except Exception as e:
            logger.error(f"Failed to get embeddings: {str(e)}")
            raise

    def update_model(self, model_name: str) -> None:
        """Update the current model.
        
        Args:
            model_name (str): Name of the model to use
        """
        self.model = model_name
        logger.info(f"Switched to Ollama model: {model_name}")

    @property
    def model_name(self) -> str:
        """Get current model name.
        
        Returns:
            str: Current model name
        """
        return self.model 