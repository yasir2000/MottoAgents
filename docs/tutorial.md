# MottoAgents Tutorial

## Table of Contents
1. [Getting Started](#getting-started)
2. [Basic Concepts](#basic-concepts)
3. [Installation Guide](#installation-guide)
4. [Quick Start](#quick-start)
5. [Working with Roles](#working-with-roles)
6. [Creating Actions](#creating-actions)
7. [Memory Management](#memory-management)
8. [Advanced Topics](#advanced-topics)
9. [Troubleshooting](#troubleshooting)

## Getting Started

### What is MottoAgents?
MottoAgents is an AI-powered agent system that allows you to create and manage autonomous agents with specific roles and capabilities. These agents can perform various tasks, from code generation to system design, using large language models and other AI technologies.

### Prerequisites
- Python 3.8 or higher
- pip package manager
- Basic understanding of async programming
- Familiarity with AI/ML concepts

## Basic Concepts

### 1. Roles
Roles are autonomous agents with specific capabilities and responsibilities. Each role has:
- A defined goal
- Set of constraints
- Available actions
- Memory system

### 2. Actions
Actions are specific tasks that roles can perform, such as:
- Writing code
- Designing systems
- Reviewing code
- Managing resources

### 3. Memory
The memory system allows roles to:
- Store information
- Recall past interactions
- Share data between roles
- Maintain context

## Installation Guide

1. Clone the repository:
```bash
git clone https://github.com/yourusername/mottoagents.git
cd mottoagents
```

2. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Configure the environment:
```bash
cp config/config.yaml.example config/config.yaml
# Edit config.yaml with your settings
```

## Quick Start

### 1. Basic Usage Example
```python
from mottoagents.roles import Engineer
from mottoagents.actions import WriteCode

# Create an engineer role
engineer = Engineer(
    name="Alex",
    profile="Python Developer",
    goal="Write clean, efficient code",
    constraints="Follow PEP8"
)

# Run a coding task
async def main():
    result = await engineer.run("Create a simple web server using Flask")
    print(result)
```

### 2. Running the Example
```bash
python examples/quickstart.py
```

## Working with Roles

### 1. Creating a Custom Role
```python
from mottoagents.roles import Role

class DataScientist(Role):
    def __init__(self, name="Data Scientist", **kwargs):
        super().__init__(
            name=name,
            profile="Data Scientist",
            goal="Analyze data and build models",
            constraints="Use best practices",
            **kwargs
        )
        self._init_actions([AnalyzeData, BuildModel])
```

### 2. Role Configuration
```python
data_scientist = DataScientist(
    name="Alice",
    llm_api_key="your-api-key",
    use_code_review=True
)
```

### 3. Role Interaction
```python
# Send a task to the role
response = await data_scientist.handle(
    Message("Analyze the customer satisfaction data")
)

# Get role's memory
history = data_scientist.history
```

## Creating Actions

### 1. Basic Action Structure
```python
from mottoagents.actions import Action

class AnalyzeData(Action):
    def __init__(self, name, context=None, llm=None):
        super().__init__(name, context, llm)
        self.desc = "Analyze data using statistical methods"

    async def run(self, context):
        # Implementation here
        return analysis_result
```

### 2. Action with Memory
```python
class BuildModel(Action):
    async def run(self, context):
        # Access memory
        data = self._rc.memory.get_by_action(AnalyzeData)
        
        # Process data
        model = await self._build_model(data)
        
        # Store results
        self._rc.memory.add(Message(model))
        return model
```

## Memory Management

### 1. Using Short-term Memory
```python
# Store information
role._rc.memory.add(Message("Important information"))

# Retrieve information
recent_messages = role._rc.memory.get()
```

### 2. Long-term Memory
```python
# Enable long-term memory
role._rc.long_term_memory = True

# Store persistent information
role._rc.memory.add(
    Message("This will be stored permanently")
)
```

### 3. Memory Filtering
```python
# Get messages by action type
analysis_results = role._rc.memory.get_by_actions([AnalyzeData])

# Get messages by timeframe
recent = role._rc.memory.get_recent(hours=24)
```

## Advanced Topics

### 1. Parallel Processing
```python
from mottoagents.utils import gather_ordered_k

async def process_multiple(tasks, max_concurrent=3):
    results = await gather_ordered_k(tasks, max_concurrent)
    return results
```

### 2. Custom Search Integration
```python
from mottoagents.tools import SearchEngine

class CustomSearch(SearchEngine):
    async def run(self, query: str):
        # Implement custom search logic
        return results
```

### 3. Role Collaboration
```python
# Create roles
engineer = Engineer()
reviewer = CodeReviewer()

# Set up collaboration
engineer.set_env(shared_environment)
reviewer.set_env(shared_environment)

# Execute collaborative task
code = await engineer.run("Implement feature X")
review = await reviewer.run(code)
```

## Troubleshooting

### Common Issues and Solutions

1. **API Key Issues**
```python
# Check API key configuration
from mottoagents.system.config import Config
config = Config()
print(config.openai_api_key)  # Should not be None
```

2. **Memory Errors**
```python
# Clear memory if needed
role._rc.memory.clear()

# Check memory size
print(len(role._rc.memory.get()))
```

3. **Action Failures**
```python
try:
    result = await action.run(context)
except Exception as e:
    logger.error(f"Action failed: {str(e)}")
    # Implement fallback logic
```

### Debugging Tips

1. Enable debug logging:
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

2. Monitor role state:
```python
print(f"Current state: {role._rc.state}")
print(f"Active action: {role._rc.todo}")
```

3. Check environment:
```python
print(f"Environment: {role._rc.env}")
print(f"Memory size: {len(role._rc.memory.get())}")
```

## Best Practices

1. **Role Design**
   - Keep roles focused on specific tasks
   - Implement proper error handling
   - Use appropriate memory management
   - Document role capabilities

2. **Action Implementation**
   - Make actions atomic and reusable
   - Include proper validation
   - Handle edge cases
   - Add comprehensive logging

3. **Memory Usage**
   - Clean up unnecessary data
   - Use appropriate memory type
   - Implement data retention policies
   - Monitor memory usage

4. **Performance Optimization**
   - Use parallel processing when appropriate
   - Implement caching strategies
   - Monitor resource usage
   - Profile performance bottlenecks

## Supported Language Models

### Available Models

1. **OpenAI Models**
   - GPT-4 (Recommended)
     ```python
     config.openai_api_model = "gpt-4"
     ```
   - GPT-3.5-turbo
     ```python
     config.openai_api_model = "gpt-3.5-turbo"
     ```
   - GPT-4-turbo
     ```python
     config.openai_api_model = "gpt-4-turbo-preview"
     ```

2. **Anthropic Models**
   - Claude 2
     ```python
     config.claude_api_key = "your-claude-api-key"
     config.model_type = "claude"
     ```
   - Claude Instant
     ```python
     config.model_type = "claude-instant"
     ```

3. **Azure OpenAI**
   ```python
   config.openai_api_type = "azure"
   config.openai_api_base = "your-azure-endpoint"
   config.openai_api_version = "2023-05-15"
   config.deployment_id = "your-deployment-id"
   ```

4. **Ollama Local Models**
   - Any Ollama-supported model
     ```python
     config.model_type = "ollama"
     config.ollama_model = "llama2"  # or any other Ollama model
     config.ollama_host = "http://localhost:11434"  # default Ollama host
     ```
   
   Supported Ollama Models:
   - Llama 2
     ```python
     config.ollama_model = "llama2"
     ```
   - CodeLlama
     ```python
     config.ollama_model = "codellama"
     ```
   - Mistral
     ```python
     config.ollama_model = "mistral"
     ```
   - Neural Chat
     ```python
     config.ollama_model = "neural-chat"
     ```
   - Other custom models
     ```python
     config.ollama_model = "your-custom-model"
     ```

### Model Configuration

1. **Setting Default Model**
```python
from mottoagents.system.config import Config

config = Config()
config.openai_api_model = "gpt-4"  # or other model name
```

2. **Per-Role Model Configuration**
```python
engineer = Engineer(
    name="Alex",
    llm_api_key="your-api-key",
    model_name="gpt-4"
)
```

3. **Model Fallback Configuration**
```python
config.fallback_models = ["gpt-4", "gpt-3.5-turbo"]
config.retry_on_failure = True
```

### Model-specific Settings

1. **OpenAI Settings**
```python
config.openai_api_rpm = 3  # Rate limit (requests per minute)
config.max_tokens_rsp = 2048  # Maximum response tokens
```

2. **Claude Settings**
```python
config.claude_max_tokens = 4096
config.claude_temperature = 0.7
```

3. **Azure OpenAI Settings**
```python
config.azure_deployment_id = "deployment-name"
config.azure_api_version = "2023-05-15"
```

4. **Ollama Settings**
```python
# Basic configuration
config.ollama_host = "http://localhost:11434"
config.ollama_model = "llama2"
config.ollama_timeout = 30  # seconds

# Model parameters
config.ollama_parameters = {
    "temperature": 0.7,
    "top_p": 0.9,
    "num_ctx": 4096,  # context window size
    "repeat_penalty": 1.1
}

# Custom model configuration
config.ollama_custom_model = {
    "name": "your-custom-model",
    "path": "/path/to/model/weights",
    "parameters": {
        "temperature": 0.8,
        "top_p": 0.95
    }
}
```

### Example: Using Ollama Models

1. **Basic Usage**
```python
from mottoagents.system.config import Config
from mottoagents.roles import Engineer

# Configure Ollama
config = Config()
config.model_type = "ollama"
config.ollama_model = "codellama"

# Create role with Ollama model
engineer = Engineer(
    name="LocalDev",
    profile="Python Developer",
    goal="Write efficient code",
    constraints="Follow PEP8"
)

# Run tasks
async def main():
    result = await engineer.run("Create a simple web server")
    print(result)
```

2. **Multiple Model Strategy with Ollama**
```python
class HybridRole(Role):
    def __init__(self, name, **kwargs):
        super().__init__(name, **kwargs)
        self.model_strategy = {
            "code_generation": {
                "type": "ollama",
                "model": "codellama"
            },
            "code_review": {
                "type": "ollama",
                "model": "llama2"
            },
            "system_design": {
                "type": "openai",
                "model": "gpt-4"
            }
        }

    async def select_model(self, task_type):
        strategy = self.model_strategy.get(task_type, {
            "type": "ollama",
            "model": "llama2"
        })
        
        if strategy["type"] == "ollama":
            config.model_type = "ollama"
            config.ollama_model = strategy["model"]
        else:
            config.model_type = strategy["type"]
            config.openai_api_model = strategy["model"]
        
        return strategy
```

3. **Custom Ollama Model Setup**
```python
# Define custom model
config.ollama_custom_model = {
    "name": "custom-python-assistant",
    "base_model": "codellama",
    "parameters": {
        "temperature": 0.8,
        "top_p": 0.95,
        "num_ctx": 8192
    }
}

# Use custom model
config.ollama_model = "custom-python-assistant"
```

### Updated Model Comparison

| Model | Best For | Context Length | Cost | Speed | Deployment |
|-------|----------|---------------|------|-------|------------|
| GPT-4 | Complex reasoning | 8K tokens | High | Moderate | Cloud |
| GPT-3.5-turbo | Simple tasks | 4K tokens | Low | Fast | Cloud |
| Claude 2 | Long-form content | 100K tokens | Medium | Moderate | Cloud |
| Llama 2 (Ollama) | General tasks | 4K tokens | Free | Fast | Local |
| CodeLlama (Ollama) | Code generation | 4K tokens | Free | Fast | Local |
| Mistral (Ollama) | Balanced tasks | 8K tokens | Free | Fast | Local |

### Best Practices for Ollama Usage

1. **Model Selection**
   - Use CodeLlama for code-related tasks
   - Use Llama 2 for general tasks
   - Use Mistral for balanced performance
   - Consider custom fine-tuned models for specific domains

2. **Performance Optimization**
   - Run Ollama on GPU for better performance
   - Adjust context window based on task requirements
   - Use appropriate temperature settings
   - Monitor system resources

3. **Error Handling**
```python
try:
    response = await llm.aask(prompt)
except ConnectionError:
    logger.error("Ollama server not running")
    # Start Ollama server or fallback to cloud model
except Exception as e:
    logger.error(f"Ollama error: {str(e)}")
    # Implement fallback logic
```

4. **Resource Management**
```python
# Monitor system resources
import psutil

def check_resources():
    cpu_percent = psutil.cpu_percent()
    memory_percent = psutil.virtual_memory().percent
    if cpu_percent > 90 or memory_percent > 90:
        logger.warning("System resources running high")
        # Implement resource management strategy
```

## Next Steps

1. Explore the [examples](../examples) directory
2. Read the [API documentation](./api.md)
3. Join the community discussions
4. Contribute to the project

---

For more detailed information, please refer to:
- [Project Documentation](./project_documentation.md)
- [API Reference](./api.md)
- [Development Roadmap](./ROADMAP.md)