#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Modified from : https://github.com/geekan/MetaGPT/blob/main/metagpt/config.py

This module provides configuration management for the MottoAgents system.
It handles loading configuration from YAML files and environment variables,
and provides access to various system settings like API keys and service endpoints.
"""
import os
import openai

import yaml

from .const import PROJECT_ROOT
from .logs import logger
from .utils.singleton import Singleton
from .tools import SearchEngineType, WebBrowserEngineType


class NotConfiguredException(Exception):
    """Exception raised for errors in the configuration.

    Attributes:
        message (str): Explanation of the configuration error
    """

    def __init__(self, message="The required configuration is not set"):
        self.message = message
        super().__init__(self.message)


class Config(metaclass=Singleton):
    """Configuration manager for the MottoAgents system.
    
    This class manages system configuration by loading settings from YAML files
    and environment variables. It follows the Singleton pattern to ensure
    consistent configuration across the system.

    Attributes:
        key_yaml_file (Path): Path to the key configuration file
        default_yaml_file (Path): Path to the default configuration file
        global_proxy (str): Global proxy configuration
        openai_api_key (str): OpenAI API key
        openai_api_base (str): OpenAI API base URL
        openai_api_type (str): OpenAI API type
        openai_api_version (str): OpenAI API version
        openai_api_rpm (int): OpenAI API rate limit (requests per minute)
        openai_api_model (str): Default OpenAI model to use
        max_tokens_rsp (int): Maximum tokens in responses
        deployment_id (str): Deployment ID for Azure OpenAI
        claude_api_key (str): Anthropic Claude API key
        serpapi_api_key (str): SerpAPI key
        serper_api_key (str): Serper API key
        google_api_key (str): Google API key
        google_cse_id (str): Google Custom Search Engine ID
        search_engine (SearchEngineType): Default search engine to use
        web_browser_engine (WebBrowserEngineType): Web browser engine type
        long_term_memory (bool): Whether to enable long-term memory
        max_budget (float): Maximum budget for API calls
    """

    _instance = None
    key_yaml_file = PROJECT_ROOT / "config/key.yaml"
    default_yaml_file = PROJECT_ROOT / "config/config.yaml"

    def __init__(self, yaml_file=default_yaml_file):
        """Initialize the configuration manager.
        
        Args:
            yaml_file (Path): Path to the configuration file to load
        """
        self._configs = {}
        self._init_with_config_files_and_env(self._configs, yaml_file)
        logger.info("Config loading done.")
        
        # Load configuration values
        self.global_proxy = self._get("GLOBAL_PROXY")
        self.openai_api_key = self._get("OPENAI_API_KEY")
        self.openai_api_base = self._get("OPENAI_API_BASE")
        self.openai_proxy = self._get("OPENAI_PROXY")
        self.openai_api_type = self._get("OPENAI_API_TYPE")
        self.openai_api_version = self._get("OPENAI_API_VERSION")
        self.openai_api_rpm = self._get("RPM", 3)
        self.openai_api_model = self._get("OPENAI_API_MODEL", "gpt-4")
        self.max_tokens_rsp = self._get("MAX_TOKENS", 2048)
        self.deployment_id = self._get("DEPLOYMENT_ID")

        # API keys for various services
        self.claude_api_key = self._get('Anthropic_API_KEY')
        self.serpapi_api_key = self._get("SERPAPI_API_KEY")
        self.serper_api_key = self._get("SERPER_API_KEY")
        self.google_api_key = self._get("GOOGLE_API_KEY")
        self.google_cse_id = self._get("GOOGLE_CSE_ID")
        
        # Service configurations
        self.search_engine = self._get("SEARCH_ENGINE", SearchEngineType.SERPAPI_GOOGLE)
        self.web_browser_engine = WebBrowserEngineType(self._get("WEB_BROWSER_ENGINE", "playwright"))
        self.playwright_browser_type = self._get("PLAYWRIGHT_BROWSER_TYPE", "chromium")
        self.selenium_browser_type = self._get("SELENIUM_BROWSER_TYPE", "chrome")
        
        # System settings
        self.long_term_memory = self._get('LONG_TERM_MEMORY', False)
        if self.long_term_memory:
            logger.warning("LONG_TERM_MEMORY is True")
        self.max_budget = self._get("MAX_BUDGET", 10.0)
        self.total_cost = 0.0

    def _init_with_config_files_and_env(self, configs: dict, yaml_file):
        """Load configuration from files and environment variables.
        
        Configuration is loaded in the following order of precedence:
        1. Environment variables
        2. Key YAML file
        3. Default YAML file
        
        Args:
            configs (dict): Dictionary to store configuration
            yaml_file (Path): Path to the configuration file
        """
        # Load environment variables first (highest priority)
        configs.update(os.environ)

        # Load from YAML files
        for _yaml_file in [yaml_file, self.key_yaml_file]:
            if not _yaml_file.exists():
                continue

            # Load local YAML file
            with open(_yaml_file, "r", encoding="utf-8") as file:
                yaml_data = yaml.safe_load(file)
                if not yaml_data:
                    continue
                os.environ.update({k: v for k, v in yaml_data.items() if isinstance(v, str)})
                configs.update(yaml_data)

    def _get(self, *args, **kwargs):
        """Get a configuration value from the internal dictionary.
        
        Args:
            *args: Arguments to pass to dict.get()
            **kwargs: Keyword arguments to pass to dict.get()
            
        Returns:
            The configuration value if found, otherwise None or the default value
        """
        return self._configs.get(*args, **kwargs)

    def get(self, key, *args, **kwargs):
        """Get a configuration value, raising an error if not found.
        
        Args:
            key (str): The configuration key to look up
            *args: Additional arguments for the lookup
            **kwargs: Additional keyword arguments for the lookup
            
        Returns:
            The configuration value
            
        Raises:
            ValueError: If the key is not found in the configuration
        """
        value = self._get(key, *args, **kwargs)
        if value is None:
            raise ValueError(f"Key '{key}' not found in environment variables or in the YAML file")
        return value


CONFIG = Config()
