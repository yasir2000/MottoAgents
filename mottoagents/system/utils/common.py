#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Time    : 2023/4/29 16:07
@Author  : alexanderwu
@File    : common.py
@From    : https://github.com/geekan/MetaGPT/blob/main/metagpt/utils/common.py

This module provides common utility functions and classes used throughout the MottoAgents project.
It includes tools for command checking, output parsing, and code parsing.
"""
import ast
import inspect
import os
import re
from typing import List, Tuple

from mottoagents.system.logs import logger


def check_cmd_exists(command) -> int:
    """Check if a shell command exists in the system.
    
    Args:
        command (str): The command to check for existence
        
    Returns:
        int: Returns 0 if the command exists, non-zero otherwise
    """
    check_command = 'command -v ' + command + ' >/dev/null 2>&1 || { echo >&2 "no mermaid"; exit 1; }'
    result = os.system(check_command)
    return result


class OutputParser:
    """A utility class for parsing different types of output formats.
    
    This class provides methods to parse blocks of text, code snippets,
    and structured data from various output formats.
    """

    @classmethod
    def parse_blocks(cls, text: str):
        """Parse text into blocks based on '##' delimiters.
        
        Args:
            text (str): The text to parse into blocks
            
        Returns:
            dict: A dictionary mapping block titles to their content
        """
        # First split the text into different blocks based on "##"
        blocks = text.split("##")

        # Create a dictionary to store the title and content of each block
        block_dict = {}

        # Iterate through all blocks
        for block in blocks:
            # If the block is not empty, continue processing
            if block.strip() != "":
                # Split the block's title and content, and remove whitespace from both ends
                block_title, block_content = block.split("\n", 1)
                # Handle potential LLM formatting issues
                if block_title[-1] == ":":
                    block_title = block_title[:-1]
                block_dict[block_title.strip()] = block_content.strip()

        return block_dict

    @classmethod
    def parse_code(cls, text: str, lang: str = "") -> str:
        """Extract code blocks from text.
        
        Args:
            text (str): The text containing code blocks
            lang (str): The programming language of the code block
            
        Returns:
            str: The extracted code
            
        Raises:
            Exception: If no code block is found
        """
        pattern = rf'```{lang}.*?\s+(.*?)```'
        match = re.search(pattern, text, re.DOTALL)
        if match:
            code = match.group(1)
        else:
            raise Exception
        return code

    @classmethod
    def parse_str(cls, text: str):
        """Parse a string value from text.
        
        Args:
            text (str): The text to parse
            
        Returns:
            str: The parsed string value with quotes and whitespace removed
        """
        text = text.split("=")[-1]
        text = text.strip().strip("'").strip("\"")
        return text

    @classmethod
    def parse_file_list(cls, text: str) -> list[str]:
        """Parse a list of files from text.
        
        Args:
            text (str): The text containing a list of files
            
        Returns:
            list[str]: The list of parsed file names
        """
        # Regular expression pattern to find the tasks list
        pattern = r'\s*(.*=.*)?(\[.*\])'

        # Extract tasks list string using regex
        match = re.search(pattern, text, re.DOTALL)
        if match:
            tasks_list_str = match.group(2)
            # Convert string representation of list to a Python list
            tasks = ast.literal_eval(tasks_list_str)
        else:
            tasks = text.split("\n")
        return tasks

    @classmethod
    def parse_data(cls, data):
        block_dict = cls.parse_blocks(data)
        parsed_data = {}
        for block, content in block_dict.items():
            # Try to remove code markers
            try:
                content = cls.parse_code(text=content)
            except Exception:
                pass

            # Try to parse list
            try:
                content = cls.parse_file_list(text=content)
            except Exception:
                pass
            parsed_data[block] = content
        return parsed_data

    @classmethod
    def parse_data_with_mapping(cls, data, mapping):
        block_dict = cls.parse_blocks(data)
        parsed_data = {}
        for block, content in block_dict.items():
            # Try to remove code markers
            try:
                content = cls.parse_code(text=content)
            except Exception:
                pass
            typing_define = mapping.get(block, None)
            if isinstance(typing_define, tuple):
                typing = typing_define[0]
            else:
                typing = typing_define
            if typing == List[str] or typing == List[Tuple[str, str]]:
                # Try to parse list
                try:
                    content = cls.parse_file_list(text=content)
                except Exception:
                    pass
            # TODO: Removing extra quotes is risky, will solve it later
            # elif typing == str:
            #     # Try to remove extra quotes
            #     try:
            #         content = cls.parse_str(text=content)
            #     except Exception:
            #         pass
            parsed_data[block] = content
        return parsed_data


class CodeParser:

    @classmethod
    def parse_block(cls, block: str, text: str) -> str:
        blocks = cls.parse_blocks(text)
        for k, v in blocks.items():
            if block in k:
                return v
        return ""

    @classmethod
    def parse_blocks(cls, text: str):
        # First split the text into different blocks based on "##"
        blocks = text.split("##")

        # Create a dictionary to store the title and content of each block
        block_dict = {}

        # Iterate through all blocks
        for block in blocks:
            # If the block is not empty, continue processing
            if block.strip() != "":
                # Split the block's title and content, and remove whitespace from both ends
                block_title, block_content = block.split("\n", 1)
                block_dict[block_title.strip()] = block_content.strip()

        return block_dict

    @classmethod
    def parse_code(cls, block: str, text: str, lang: str = "") -> str:
        if block:
            text = cls.parse_block(block, text)
        pattern = rf'```{lang}.*?\s+(.*?)```'
        match = re.search(pattern, text, re.DOTALL)
        if match:
            code = match.group(1)
        else:
            logger.error(f"{pattern} not match following text:")
            logger.error(text)
            raise Exception
        return code

    @classmethod
    def parse_str(cls, block: str, text: str, lang: str = ""):
        code = cls.parse_code(block, text, lang)
        code = code.split("=")[-1]
        code = code.strip().strip("'").strip("\"")
        return code

    @classmethod
    def parse_file_list(cls, block: str, text: str, lang: str = "") -> list[str]:
        # Regular expression pattern to find the tasks list.
        code = cls.parse_code(block, text, lang)
        print(code)
        pattern = r'\s*(.*=.*)?(\[.*\])'

        # Extract tasks list string using regex.
        match = re.search(pattern, code, re.DOTALL)
        if match:
            tasks_list_str = match.group(2)

            # Convert string representation of list to a Python list using ast.literal_eval.
            tasks = ast.literal_eval(tasks_list_str)
        else:
            raise Exception
        return tasks


class NoMoneyException(Exception):
    """Raised when the operation cannot be completed due to insufficient funds"""

    def __init__(self, amount, message="Insufficient funds"):
        self.amount = amount
        self.message = message
        super().__init__(self.message)

    def __str__(self):
        return f'{self.message} -> Amount required: {self.amount}'


def print_members(module, indent=0):
    """
    https://stackoverflow.com/questions/1796180/how-can-i-get-a-list-of-all-classes-within-current-module-in-python
    :param module:
    :param indent:
    :return:
    """
    prefix = ' ' * indent
    for name, obj in inspect.getmembers(module):
        print(name, obj)
        if inspect.isclass(obj):
            print(f'{prefix}Class: {name}')
            # print the methods within the class
            if name in ['__class__', '__base__']:
                continue
            print_members(obj, indent + 2)
        elif inspect.isfunction(obj):
            print(f'{prefix}Function: {name}')
        elif inspect.ismethod(obj):
            print(f'{prefix}Method: {name}')
