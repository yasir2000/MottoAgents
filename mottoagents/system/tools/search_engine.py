#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Time    : 2023/5/23 18:27
@Author  : alexanderwu
@File    : search_engine.py
@From    : https://github.com/geekan/MetaGPT/blob/main/metagpt/tools/search_engine.py

This module provides search engine functionality for the MottoAgents system.
It supports multiple search engines including Google (direct and through APIs),
SerpAPI, and custom search implementations.
"""
from __future__ import annotations

import json

from mottoagents.system.config import Config
from mottoagents.system.logs import logger
from .search_engine_serpapi import SerpAPIWrapper
from .search_engine_serper import SerperWrapper

config = Config()
from mottoagents.system.tools import SearchEngineType


class SearchEngine:
    """Search engine interface supporting multiple backend implementations.
    
    This class provides a unified interface for performing web searches using
    different search engines. It supports:
    - Direct Google search
    - SerpAPI Google search
    - Serper Google search
    - Custom search implementations
    
    Note: For Google search, a global proxy (like Proxifier) may be required.
    
    Attributes:
        config (Config): System configuration
        run_func (callable): Custom search function for custom implementations
        engine (SearchEngineType): The search engine to use
        serpapi_api_key (str): API key for SerpAPI
    """

    def __init__(self, engine=None, run_func=None, serpapi_api_key=None):
        """Initialize the search engine.
        
        Args:
            engine (SearchEngineType, optional): Search engine to use
            run_func (callable, optional): Custom search function
            serpapi_api_key (str, optional): SerpAPI key
        """
        self.config = Config()
        self.run_func = run_func
        self.engine = engine or self.config.search_engine
        self.serpapi_api_key = serpapi_api_key

    @classmethod
    def run_google(cls, query, max_results=8):
        """Perform a direct Google search.
        
        Args:
            query (str): Search query
            max_results (int): Maximum number of results to return
            
        Returns:
            list: Search results
        """
        results = google_official_search(query, num_results=max_results)
        logger.info(results)
        return results

    async def run(self, query: str, max_results=8):
        """Execute a search using the configured search engine.
        
        Args:
            query (str): Search query
            max_results (int): Maximum number of results to return
            
        Returns:
            dict|list: Search results in engine-specific format
            
        Raises:
            NotImplementedError: If the selected engine is not supported
        """
        if self.engine == SearchEngineType.SERPAPI_GOOGLE:
            if self.serpapi_api_key is not None:
                api = SerpAPIWrapper(serpapi_api_key=self.serpapi_api_key)
            else:
                api = SerpAPIWrapper()
            rsp = await api.run(query)
        elif self.engine == SearchEngineType.DIRECT_GOOGLE:
            rsp = SearchEngine.run_google(query, max_results)
        elif self.engine == SearchEngineType.SERPER_GOOGLE:
            api = SerperWrapper()
            rsp = await api.run(query)
        elif self.engine == SearchEngineType.CUSTOM_ENGINE:
            rsp = self.run_func(query)
        else:
            raise NotImplementedError
        return rsp


def google_official_search(query: str, num_results: int = 8, focus=['snippet', 'link', 'title']) -> dict | list[dict]:
    """Perform a search using the official Google Custom Search API.
    
    Args:
        query (str): Search query
        num_results (int): Maximum number of results to return
        focus (list[str]): Fields to include in results
        
    Returns:
        dict|list[dict]: Search results containing specified fields
        
    Raises:
        HttpError: If there's an error with the Google API request
    """
    from googleapiclient.discovery import build
    from googleapiclient.errors import HttpError

    try:
        api_key = config.google_api_key
        custom_search_engine_id = config.google_cse_id

        with build("customsearch", "v1", developerKey=api_key) as service:
            result = (
                service.cse()
                .list(q=query, cx=custom_search_engine_id, num=num_results)
                .execute()
            )
            logger.info(result)
            
        # Extract the search result items from the response
        search_results = result.get("items", [])

        # Create a list of only the requested fields from the search results
        search_results_details = [{i: j for i, j in item_dict.items() if i in focus} for item_dict in search_results]

    except HttpError as e:
        # Handle errors in the API call
        error_details = json.loads(e.content.decode())

        # Check if the error is related to an invalid or missing API key
        if error_details.get("error", {}).get("code") == 403 and "invalid API key" in error_details.get("error", {}).get("message", ""):
            return "Error: The provided Google API key is invalid or missing."
        else:
            return f"Error: {e}"

    return search_results_details


def safe_google_results(results: str | list) -> str:
    """Format Google search results in a safe, consistent format.
    
    Args:
        results (str|list): Raw search results
        
    Returns:
        str: Safely formatted search results
    """
    if isinstance(results, list):
        safe_message = json.dumps(
            # Note: UTF-8 encoding was removed here, but exists in AutoGPT
            [result for result in results]
        )
    else:
        safe_message = results.encode("utf-8", "ignore").decode("utf-8")
    return safe_message


if __name__ == '__main__':
    SearchEngine.run(query='wtf')
