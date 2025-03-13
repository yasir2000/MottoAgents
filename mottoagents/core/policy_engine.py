from typing import Dict, List
from .bmm import BusinessPolicy, BusinessRule

class PolicyEngine:
    def __init__(self, config: Dict):
        self.policies = {}
        self.rules = {}
        self.compliance_threshold = config.get('compliance_threshold', 0.8)

    async def validate(self, context: Dict) -> bool:
        """Validate context against business policies and rules"""
        policy_score = await self._check_policy_compliance(context)
        rule_score = await self._verify_rule_compliance(context)
        return (policy_score + rule_score) / 2 >= self.compliance_threshold

    async def register_policy(self, policy: BusinessPolicy):
        """Register new business policy"""
        self.policies[policy.name] = policy
        await self._update_rule_chain(policy)

    async def _check_policy_compliance(self, context: Dict) -> float:
        """Calculate policy compliance score"""
        scores = []
        for policy in self.policies.values():
            score = await self._evaluate_policy(context, policy)
            scores.append(score)
        return sum(scores) / len(scores) if scores else 0.0

    async def _verify_rule_compliance(self, context: Dict) -> float:
        """Calculate rule compliance score"""
        scores = []
        for rule in self.rules.values():
            score = await self._evaluate_rule(context, rule)
            scores.append(score)
        return sum(scores) / len(scores) if scores else 0.0
