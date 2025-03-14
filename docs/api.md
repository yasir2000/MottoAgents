# MottoAgents API Reference

## Core Components

### Business Motivation Model (BMM)

#### BMMContext
Central class managing business motivation and context.

```python
class BMMContext:
    def __init__()
    
    def validate_action(action_context: Dict) -> bool
        """Validate action against business rules and policies"""
    
    def align_with_strategy(action_plan: Dict) -> bool
        """Check strategic alignment of action plan"""
    
    def assess_influencer(influencer: Dict, type: InfluencerType) -> Assessment
        """Assess business influencer impact"""
    
    def validate_directive_chain(action: Dict) -> bool
        """Validate complete directive chain"""
```

#### BusinessArchitect
Primary role for managing BMM implementation.

```python
class BusinessArchitect(Role):
    async def analyze_business_context(context: Dict) -> Dict
        """Analyze and update business context"""
    
    async def define_strategy(vision: str, goals: List[str]) -> Dict
        """Define business strategy"""
    
    async def evaluate_policies(context: Dict) -> Dict
        """Evaluate and update policies"""
    
    async def track_objectives(goals: List[str]) -> Dict
        """Track objectives against goals"""
```

#### PolicyEngine
Handles policy enforcement and validation.

```python
class PolicyEngine:
    def __init__(config: Dict)
    
    async def validate(context: Dict) -> bool
        """Validate against policies and rules"""
    
    async def register_policy(policy: BusinessPolicy)
        """Register new business policy"""
```

#### BMMMemory
Memory system with BMM context awareness.

```python
class BMMMemory(Memory):
    def add_with_context(message: Dict, bmm_context: Dict)
        """Add memory with BMM context"""
    
    def get_by_objective(objective_id: str) -> List[Dict]
        """Get objective-related memories"""
    
    def get_strategic_context(strategy_id: str) -> Optional[Dict]
        """Get strategic context"""
```

### Data Structures

#### BusinessRule
```python
@dataclass
class BusinessRule:
    name: str          # Rule identifier
    definition: str    # Rule definition
    scope: str        # Application scope
    source: str       # Rule source
    rationale: str    # Business rationale
```

#### BusinessPolicy
```python
@dataclass
class BusinessPolicy:
    name: str                 # Policy name
    description: str          # Policy description
    rules: List[BusinessRule] # Associated rules
    rationale: str           # Policy rationale
    impact: Dict[str, str]   # Impact analysis
```

#### Assessment
```python
@dataclass
class Assessment:
    swot: Dict[str, List[str]]  # SWOT analysis
    evaluations: List[Dict]     # Detailed evaluations
```

### Core Architecture

#### MottoAgentsArchitecture
```python
class MottoAgentsArchitecture:
    def __init__()
    
    async def register_role(role_id: str, role_config: Dict)
        """Register role with BMM context"""
    
    async def execute_action_chain(actions: List[Dict]) -> Dict
        """Execute BMM-validated actions"""
    
    async def validate_bmm_compliance(action: Dict) -> bool
        """Validate BMM compliance"""
```

#### MottoAgentsOrchestrator
```python
class MottoAgentsOrchestrator:
    def __init__()
    
    async def initialize_bmm_environment(config: Dict)
        """Initialize BMM environment"""
    
    async def execute_task(task: Dict) -> Dict
        """Execute BMM-aware task"""
```

### Configuration

#### BMM Configuration Options
```yaml
bmm:
  enable_validation: bool           # Enable validation
  strategy_alignment_threshold: float # Alignment threshold
  policy_compliance_mode: str       # Compliance mode
  objective_tracking: bool          # Enable tracking
  
  maturity_levels:                  # BMM maturity levels
    1: "Initial BMM Implementation"
    2: "Managed BMM Process"
    3: "Defined BMM Architecture"
    4: "Quantitatively Managed BMM"
    5: "Optimizing BMM"
```

### Model Control Protocol (MCP)

#### ModelControlProtocol
```python
class ModelControlProtocol:
    def __init__(config: Dict)
    
    async def validate_model_usage(model: str, context: Dict) -> bool
        """Validate model usage against MCP policies"""
    
    async def register_mcp_policy(policy: MCPPolicy)
        """Register new MCP policy"""
        
    async def update_model_settings(model: str, settings: Dict)
        """Update model-specific settings"""
```

#### MCP Configuration
```yaml
mcp:
  control_level: "strict" | "moderate" | "permissive"
  safety_threshold: float
  model_settings: Dict[str, ModelConfig]
  safety_controls: SafetyControls
  access_controls: AccessControls
```

### Usage Examples

#### Creating a Business Architect
```python
architect = BusinessArchitect(
    name="Enterprise Architect",
    vision="Market Leadership",
    goals=["Improve Efficiency", "Reduce Costs"],
    mission="Transform Operations"
)
```

#### Defining Business Strategy
```python
strategy = await architect.define_strategy(
    vision="Digital Excellence",
    goals=[
        "Achieve 95% Automation",
        "Reduce Manual Processes by 70%"
    ]
)
```

#### Policy Enforcement
```python
policy_engine = PolicyEngine(config)
await policy_engine.register_policy(
    BusinessPolicy(
        name="SecurityFirst",
        description="Ensure System Security",
        rules=[
            BusinessRule(
                name="DataEncryption",
                definition="All Data Must Be Encrypted",
                scope="global"
            )
        ]
    )
)
```

#### Memory Operations
```python
memory = BMMMemory()
memory.add_with_context(
    message={"action": "strategy_update"},
    bmm_context={"objective": "market_expansion"}
)

# Retrieve objective-specific memories
memories = memory.get_by_objective("market_expansion")
```

#### MCP Usage Example
```python
# Configure MCP for a model
await mcp.update_model_settings("gpt-4", {
    "max_tokens": 8192,
    "temperature": 0.7,
    "rate_limit": 100
})

# Register MCP policy
policy = MCPPolicy(
    name="EnterprisePolicy",
    control_level=MCPControlLevel.STRICT,
    allowed_models=["gpt-4"],
    restricted_actions=["system_modification"],
    safety_checks={"content_filtering": True}
)
await mcp.register_mcp_policy(policy)
```

For complete implementation details, refer to the source code and [project documentation](project_documentation.md).
