"""
Multi-model collaboration system for enhanced AI capabilities.

This module enables multiple AI models to work together on complex tasks,
combining their strengths to produce better results.
"""

import asyncio
import logging
from dataclasses import dataclass
from enum import Enum
from typing import List, Dict, Any, Optional, Callable
from datetime import datetime

from resoftai.llm.base import LLMProvider, LLMConfig, LLMResponse
from resoftai.llm.factory import LLMFactory

logger = logging.getLogger(__name__)


class CollaborationStrategy(str, Enum):
    """Collaboration strategies for multi-model systems."""
    CONSENSUS = "consensus"  # All models vote, majority wins
    ENSEMBLE = "ensemble"    # Combine outputs from all models
    WATERFALL = "waterfall"  # Sequential processing
    PARALLEL = "parallel"    # Parallel processing, best result wins
    SPECIALIST = "specialist" # Route to specialized models


class ModelRole(str, Enum):
    """Specialized roles for different models."""
    CODE_GENERATION = "code_generation"
    CODE_REVIEW = "code_review"
    BUG_DETECTION = "bug_detection"
    REFACTORING = "refactoring"
    DOCUMENTATION = "documentation"
    TESTING = "testing"
    ARCHITECTURE = "architecture"


@dataclass
class ModelConfig:
    """Configuration for a model in collaboration."""
    llm_config: LLMConfig
    role: ModelRole
    weight: float = 1.0  # Weight for voting/ensemble
    priority: int = 0     # Priority for waterfall


@dataclass
class CollaborationResult:
    """Result from multi-model collaboration."""
    strategy: CollaborationStrategy
    final_output: str
    individual_outputs: List[Dict[str, Any]]
    consensus_score: Optional[float] = None
    execution_time: float = 0.0
    model_votes: Optional[Dict[str, int]] = None


class MultiModelCollaborator:
    """
    Multi-model collaboration system.

    Supports various collaboration strategies to leverage multiple AI models
    for improved accuracy, reliability, and quality.
    """

    def __init__(self, models: List[ModelConfig]):
        """
        Initialize multi-model collaborator.

        Args:
            models: List of model configurations
        """
        self.models = models
        self.providers: Dict[ModelRole, LLMProvider] = {}

        # Initialize providers
        for model_config in models:
            self.providers[model_config.role] = LLMFactory.create(model_config.llm_config)

        logger.info(f"MultiModelCollaborator initialized with {len(models)} models")

    async def collaborate(
        self,
        prompt: str,
        strategy: CollaborationStrategy,
        system_prompt: Optional[str] = None,
        roles: Optional[List[ModelRole]] = None,
        **kwargs
    ) -> CollaborationResult:
        """
        Execute multi-model collaboration.

        Args:
            prompt: The task prompt
            strategy: Collaboration strategy to use
            system_prompt: Optional system prompt
            roles: Specific roles to involve (None = all)
            **kwargs: Additional arguments

        Returns:
            Collaboration result
        """
        start_time = datetime.now()

        # Select models to use
        active_providers = self._select_providers(roles)

        if not active_providers:
            raise ValueError("No models available for collaboration")

        # Execute strategy
        if strategy == CollaborationStrategy.CONSENSUS:
            result = await self._consensus_strategy(prompt, active_providers, system_prompt, **kwargs)
        elif strategy == CollaborationStrategy.ENSEMBLE:
            result = await self._ensemble_strategy(prompt, active_providers, system_prompt, **kwargs)
        elif strategy == CollaborationStrategy.WATERFALL:
            result = await self._waterfall_strategy(prompt, active_providers, system_prompt, **kwargs)
        elif strategy == CollaborationStrategy.PARALLEL:
            result = await self._parallel_strategy(prompt, active_providers, system_prompt, **kwargs)
        elif strategy == CollaborationStrategy.SPECIALIST:
            result = await self._specialist_strategy(prompt, active_providers, system_prompt, **kwargs)
        else:
            raise ValueError(f"Unknown strategy: {strategy}")

        # Calculate execution time
        execution_time = (datetime.now() - start_time).total_seconds()
        result.execution_time = execution_time

        logger.info(f"Collaboration completed in {execution_time:.2f}s using {strategy} strategy")

        return result

    def _select_providers(self, roles: Optional[List[ModelRole]]) -> Dict[ModelRole, LLMProvider]:
        """Select providers based on roles."""
        if roles is None:
            return self.providers

        return {role: provider for role, provider in self.providers.items() if role in roles}

    async def _consensus_strategy(
        self,
        prompt: str,
        providers: Dict[ModelRole, LLMProvider],
        system_prompt: Optional[str],
        **kwargs
    ) -> CollaborationResult:
        """
        Consensus strategy: All models vote, majority wins.
        """
        # Get responses from all models
        tasks = []
        for role, provider in providers.items():
            tasks.append(self._get_model_response(provider, role, prompt, system_prompt, **kwargs))

        responses = await asyncio.gather(*tasks, return_exceptions=True)

        # Filter out exceptions
        valid_responses = [r for r in responses if not isinstance(r, Exception)]

        if not valid_responses:
            raise RuntimeError("All models failed to respond")

        # Count votes for each unique response
        votes: Dict[str, int] = {}
        weighted_votes: Dict[str, float] = {}

        for response in valid_responses:
            content = response['content']
            role = response['role']
            weight = self._get_model_weight(role)

            if content in votes:
                votes[content] += 1
                weighted_votes[content] += weight
            else:
                votes[content] = 1
                weighted_votes[content] = weight

        # Select response with highest weighted vote
        final_output = max(weighted_votes.items(), key=lambda x: x[1])[0]

        # Calculate consensus score
        consensus_score = weighted_votes[final_output] / sum(weighted_votes.values())

        return CollaborationResult(
            strategy=CollaborationStrategy.CONSENSUS,
            final_output=final_output,
            individual_outputs=valid_responses,
            consensus_score=consensus_score,
            model_votes=votes
        )

    async def _ensemble_strategy(
        self,
        prompt: str,
        providers: Dict[ModelRole, LLMProvider],
        system_prompt: Optional[str],
        **kwargs
    ) -> CollaborationResult:
        """
        Ensemble strategy: Combine outputs from all models.
        """
        # Get responses from all models
        tasks = []
        for role, provider in providers.items():
            tasks.append(self._get_model_response(provider, role, prompt, system_prompt, **kwargs))

        responses = await asyncio.gather(*tasks, return_exceptions=True)

        # Filter out exceptions
        valid_responses = [r for r in responses if not isinstance(r, Exception)]

        if not valid_responses:
            raise RuntimeError("All models failed to respond")

        # Combine outputs
        combined_output = self._combine_outputs(valid_responses)

        return CollaborationResult(
            strategy=CollaborationStrategy.ENSEMBLE,
            final_output=combined_output,
            individual_outputs=valid_responses
        )

    async def _waterfall_strategy(
        self,
        prompt: str,
        providers: Dict[ModelRole, LLMProvider],
        system_prompt: Optional[str],
        **kwargs
    ) -> CollaborationResult:
        """
        Waterfall strategy: Sequential processing through models.
        """
        # Sort models by priority
        sorted_models = sorted(
            [(role, provider) for role, provider in providers.items()],
            key=lambda x: self._get_model_priority(x[0])
        )

        current_prompt = prompt
        all_responses = []

        for role, provider in sorted_models:
            response = await self._get_model_response(
                provider, role, current_prompt, system_prompt, **kwargs
            )
            all_responses.append(response)

            # Use output as input for next model
            current_prompt = response['content']

        return CollaborationResult(
            strategy=CollaborationStrategy.WATERFALL,
            final_output=current_prompt,
            individual_outputs=all_responses
        )

    async def _parallel_strategy(
        self,
        prompt: str,
        providers: Dict[ModelRole, LLMProvider],
        system_prompt: Optional[str],
        **kwargs
    ) -> CollaborationResult:
        """
        Parallel strategy: Run all models in parallel, select best result.
        """
        # Get responses from all models in parallel
        tasks = []
        for role, provider in providers.items():
            tasks.append(self._get_model_response(provider, role, prompt, system_prompt, **kwargs))

        responses = await asyncio.gather(*tasks, return_exceptions=True)

        # Filter out exceptions
        valid_responses = [r for r in responses if not isinstance(r, Exception)]

        if not valid_responses:
            raise RuntimeError("All models failed to respond")

        # Select best response based on quality metrics
        best_response = self._select_best_response(valid_responses)

        return CollaborationResult(
            strategy=CollaborationStrategy.PARALLEL,
            final_output=best_response['content'],
            individual_outputs=valid_responses
        )

    async def _specialist_strategy(
        self,
        prompt: str,
        providers: Dict[ModelRole, LLMProvider],
        system_prompt: Optional[str],
        **kwargs
    ) -> CollaborationResult:
        """
        Specialist strategy: Route to specialized model based on task.
        """
        # Determine task type and select appropriate specialist
        task_type = kwargs.get('task_type', 'general')

        specialist_role = self._determine_specialist(task_type, providers.keys())

        if specialist_role not in providers:
            # Fallback to first available provider
            specialist_role = list(providers.keys())[0]

        # Get response from specialist
        response = await self._get_model_response(
            providers[specialist_role],
            specialist_role,
            prompt,
            system_prompt,
            **kwargs
        )

        return CollaborationResult(
            strategy=CollaborationStrategy.SPECIALIST,
            final_output=response['content'],
            individual_outputs=[response]
        )

    async def _get_model_response(
        self,
        provider: LLMProvider,
        role: ModelRole,
        prompt: str,
        system_prompt: Optional[str],
        **kwargs
    ) -> Dict[str, Any]:
        """Get response from a single model."""
        try:
            response = await provider.generate(prompt, system_prompt, **kwargs)

            return {
                'role': role,
                'provider': provider.provider_name,
                'content': response.content,
                'usage': response.usage,
                'timestamp': datetime.now().isoformat()
            }
        except Exception as e:
            logger.error(f"Model {role} failed: {e}")
            raise

    def _get_model_weight(self, role: ModelRole) -> float:
        """Get weight for a model role."""
        for model in self.models:
            if model.role == role:
                return model.weight
        return 1.0

    def _get_model_priority(self, role: ModelRole) -> int:
        """Get priority for a model role."""
        for model in self.models:
            if model.role == role:
                return model.priority
        return 0

    def _combine_outputs(self, responses: List[Dict[str, Any]]) -> str:
        """Combine multiple model outputs into a single result."""
        # Simple combination: concatenate with sections
        combined = "# Collaborative Result\n\n"

        for i, response in enumerate(responses, 1):
            combined += f"## Response from {response['role'].value}\n\n"
            combined += f"{response['content']}\n\n"

        # Add synthesis section
        combined += "## Synthesis\n\n"
        combined += "This result combines insights from multiple AI models for enhanced quality.\n"

        return combined

    def _select_best_response(self, responses: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Select the best response from multiple options."""
        # Simple heuristic: prefer longer, more detailed responses
        # In practice, you'd use more sophisticated quality metrics

        scored_responses = []
        for response in responses:
            content = response['content']
            score = len(content)  # Simple length-based score

            # Bonus for code blocks
            score += content.count('```') * 100

            # Bonus for structured content
            score += content.count('#') * 50
            score += content.count('-') * 10

            scored_responses.append((score, response))

        # Return response with highest score
        return max(scored_responses, key=lambda x: x[0])[1]

    def _determine_specialist(
        self,
        task_type: str,
        available_roles: List[ModelRole]
    ) -> ModelRole:
        """Determine which specialist to use for a task."""
        # Map task types to specialist roles
        task_role_map = {
            'code_generation': ModelRole.CODE_GENERATION,
            'review': ModelRole.CODE_REVIEW,
            'bug_detection': ModelRole.BUG_DETECTION,
            'refactoring': ModelRole.REFACTORING,
            'documentation': ModelRole.DOCUMENTATION,
            'testing': ModelRole.TESTING,
            'architecture': ModelRole.ARCHITECTURE
        }

        preferred_role = task_role_map.get(task_type.lower())

        if preferred_role and preferred_role in available_roles:
            return preferred_role

        # Fallback to first available
        return list(available_roles)[0]


class MultiModelCodeReviewer:
    """
    Multi-model code reviewer using collaboration for thorough reviews.
    """

    def __init__(self, collaborator: MultiModelCollaborator):
        """Initialize code reviewer with multi-model collaborator."""
        self.collaborator = collaborator

    async def review_code(
        self,
        code: str,
        language: str,
        filename: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Review code using multiple AI models.

        Args:
            code: Source code to review
            language: Programming language
            filename: Optional filename

        Returns:
            Comprehensive review results
        """
        review_prompt = f"""Please review the following {language} code for:
1. **Code Quality**: Best practices, readability, maintainability
2. **Security**: Potential vulnerabilities and security issues
3. **Performance**: Optimization opportunities
4. **Bugs**: Potential bugs or logic errors
5. **Design**: Architecture and design patterns

Code:
```{language}
{code}
```

Provide a structured review with specific recommendations."""

        system_prompt = """You are an expert code reviewer with deep knowledge of software engineering best practices, security, and performance optimization. Provide thorough, actionable feedback."""

        # Use consensus strategy for reliability
        result = await self.collaborator.collaborate(
            prompt=review_prompt,
            strategy=CollaborationStrategy.CONSENSUS,
            system_prompt=system_prompt,
            roles=[ModelRole.CODE_REVIEW, ModelRole.BUG_DETECTION]
        )

        return {
            'review': result.final_output,
            'consensus_score': result.consensus_score,
            'individual_reviews': result.individual_outputs,
            'execution_time': result.execution_time
        }


def create_default_collaborator(primary_config: LLMConfig) -> MultiModelCollaborator:
    """
    Create a default multi-model collaborator with common roles.

    Args:
        primary_config: Primary LLM configuration

    Returns:
        Configured MultiModelCollaborator
    """
    models = [
        ModelConfig(
            llm_config=primary_config,
            role=ModelRole.CODE_GENERATION,
            weight=1.0,
            priority=1
        ),
        ModelConfig(
            llm_config=primary_config,
            role=ModelRole.CODE_REVIEW,
            weight=1.2,  # Higher weight for reviews
            priority=2
        ),
        ModelConfig(
            llm_config=primary_config,
            role=ModelRole.BUG_DETECTION,
            weight=1.1,
            priority=3
        )
    ]

    return MultiModelCollaborator(models)
