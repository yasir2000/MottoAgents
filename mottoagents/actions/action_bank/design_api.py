#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Time    : 2023/5/11 14:43
@Author  : alexanderwu
@From    : https://github.com/geekan/MetaGPT/blob/main/metagpt/actions/design_api.py

This module implements the WriteDesign action, which is responsible for
creating system designs based on PRD (Product Requirements Document).
It generates API definitions, data structures, and system architecture diagrams.
"""
import shutil
from pathlib import Path
from typing import List

from mottoagents.actions import Action, ActionOutput
from mottoagents.system.const import WORKSPACE_ROOT
from mottoagents.system.logs import logger
from mottoagents.system.utils.common import CodeParser
from mottoagents.system.utils.mermaid import mermaid_to_file

# Template for the design prompt
PROMPT_TEMPLATE = """
# Context
{context}

## Format example
{format_example}
-----
Role: You are an architect; the goal is to design a SOTA PEP8-compliant python system; make the best use of good open source tools
Requirement: Fill in the following missing information based on the context, note that all sections are response with code form separately
Max Output: 8192 chars or 2048 tokens. Try to use them up.
Attention: Use '##' to split sections, not '#', and '## <SECTION_NAME>' SHOULD WRITE BEFORE the code and triple quote.

## Implementation approach: Provide as Plain text. Analyze the difficult points of the requirements, select the appropriate open-source framework.

## Python package name: Provide as Python str with python triple quoto, concise and clear, characters only use a combination of all lowercase and underscores

## File list: Provided as Python list[str], the list of ONLY REQUIRED files needed to write the program(LESS IS MORE!). Only need relative paths, comply with PEP8 standards. ALWAYS write a main.py or app.py here

## Data structures and interface definitions: Use mermaid classDiagram code syntax, including classes (INCLUDING __init__ method) and functions (with type annotations), CLEARLY MARK the RELATIONSHIPS between classes, and comply with PEP8 standards. The data structures SHOULD BE VERY DETAILED and the API should be comprehensive with a complete design. 

## Program call flow: Use sequenceDiagram code syntax, COMPLETE and VERY DETAILED, using CLASSES AND API DEFINED ABOVE accurately, covering the CRUD AND INIT of each object, SYNTAX MUST BE CORRECT.

## Anything UNCLEAR: Provide as Plain text. Make clear here.
"""

# Example format for the design output
FORMAT_EXAMPLE = """
---
## Implementation approach
We will ...

## Python package name
```python
"snake_game"
```

## File list
```python
[
    "main.py",
]
```

## Data structures and interface definitions
```mermaid
classDiagram
    class Game{
        +int score
    }
    ...
    Game "1" -- "1" Food: has
```

## Program call flow
```mermaid
sequenceDiagram
    participant M as Main
    ...
    G->>M: end game
```

## Anything UNCLEAR
The requirement is clear to me.
---
"""

# Mapping of output sections to their expected types
OUTPUT_MAPPING = {
    "Implementation approach": (str, ...),
    "Python package name": (str, ...),
    "File list": (List[str], ...),
    "Data structures and interface definitions": (str, ...),
    "Program call flow": (str, ...),
    "Anything UNCLEAR": (str, ...),
}


class WriteDesign(Action):
    """Action for creating system designs based on PRD.
    
    This action takes a PRD as input and generates:
    - Implementation approach
    - Python package structure
    - Required file list
    - Data structures and API definitions
    - Program flow diagrams
    """

    def __init__(self, name, context=None, llm=None):
        """Initialize the WriteDesign action.
        
        Args:
            name (str): Action name
            context (str, optional): Initial context
            llm (LLM, optional): Language model to use
        """
        super().__init__(name, context, llm)
        self.desc = "Based on the PRD, think about the system design, and design the corresponding APIs, " \
                    "data structures, library tables, processes, and paths. Please provide your design, feedback " \
                    "clearly and in detail."

    def recreate_workspace(self, workspace: Path):
        """Recreate the workspace directory.
        
        Args:
            workspace (Path): Path to the workspace directory
        """
        try:
            shutil.rmtree(workspace)
        except FileNotFoundError:
            # Directory doesn't exist, but we don't care
            pass
        workspace.mkdir(parents=True, exist_ok=True)

    def _save_prd(self, docs_path, resources_path, prd):
        """Save the PRD and generate related diagrams.
        
        Args:
            docs_path (Path): Path to save documentation
            resources_path (Path): Path to save resources
            prd (str): PRD content
        """
        prd_file = docs_path / 'prd.md'
        quadrant_chart = CodeParser.parse_code(block="Competitive Quadrant Chart", text=prd)
        mermaid_to_file(quadrant_chart, resources_path / 'competitive_analysis')
        logger.info(f"Saving PRD to {prd_file}")
        prd_file.write_text(prd)

    def _save_system_design(self, docs_path, resources_path, content):
        """Save the system design and generate related diagrams.
        
        Args:
            docs_path (Path): Path to save documentation
            resources_path (Path): Path to save resources
            content (str): System design content
        """
        data_api_design = CodeParser.parse_code(block="Data structures and interface definitions", text=content)
        seq_flow = CodeParser.parse_code(block="Program call flow", text=content)
        mermaid_to_file(data_api_design, resources_path / 'data_api_design')
        mermaid_to_file(seq_flow, resources_path / 'seq_flow')
        system_design_file = docs_path / 'system_design.md'
        logger.info(f"Saving System Designs to {system_design_file}")
        system_design_file.write_text(content)

    def _save(self, context, system_design):
        """Save all design artifacts to the workspace.
        
        Args:
            context (list): Context information including PRD
            system_design (ActionOutput|str): Generated system design
        """
        if isinstance(system_design, ActionOutput):
            content = system_design.content
            ws_name = CodeParser.parse_str(block="Python package name", text=content)
        else:
            content = system_design
            ws_name = CodeParser.parse_str(block="Python package name", text=system_design)
            
        workspace = WORKSPACE_ROOT / ws_name
        self.recreate_workspace(workspace)
        
        # Create necessary directories
        docs_path = workspace / 'docs'
        resources_path = workspace / 'resources'
        docs_path.mkdir(parents=True, exist_ok=True)
        resources_path.mkdir(parents=True, exist_ok=True)
        
        # Save PRD and system design
        self._save_prd(docs_path, resources_path, context[-1].content)
        self._save_system_design(docs_path, resources_path, content)

    async def run(self, context):
        """Execute the WriteDesign action.
        
        Args:
            context (str): Input context including PRD
            
        Returns:
            ActionOutput|str: Generated system design
        """
        prompt = PROMPT_TEMPLATE.format(context=context, format_example=FORMAT_EXAMPLE)
        system_design = await self._aask_v1(prompt, "system_design", OUTPUT_MAPPING)
        self._save(context, system_design)
        return system_design