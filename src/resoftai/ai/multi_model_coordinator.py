"""Multi-Model Coordination System for collaborative AI processing."""
from enum import Enum
from typing import List, Dict, Any, Optional, Callable
from dataclasses import dataclass
import asyncio
import statistics
from collections import Counter

from resoftai.llm.factory import LLMFactory


class CombinationStrategy(str, Enum):
    """Strategy for combining multiple model outputs."""
    VOTING = "voting"  # Majority voting
    WEIGHTED_AVERAGE = "weighted_average"  # Weighted by model quality/cost
    CASCADE = "cascade"  # Sequential fallback
    ENSEMBLE = "ensemble"  # Combine all outputs
    BEST_OF_N = "best_of_n"  # Select best based on criteria


class TaskComplexity(str, Enum):
    """Task complexity levels for model selection."""
    SIMPLE = "simple"  # Simple tasks (GPT-3.5, DeepSeek-chat)
    MODERATE = "moderate"  # Moderate complexity (GPT-4, Claude Sonnet)
    COMPLEX = "complex"  # Complex tasks (GPT-4, Claude Opus)
    CRITICAL = "critical"  # Mission-critical (multiple models, voting)


@dataclass
class ModelConfig:
    """Configuration for a single model in multi-model setup."""
    provider: str
    model_name: str
    weight: float = 1.0  # Weight for weighted combinations
    priority: int = 1  # Priority for cascade strategy (lower = higher priority)
    cost_per_token: float = 0.0  # Cost optimization
    quality_score: float = 1.0  # Historical quality score
    max_tokens: int = 4096
    temperature: float = 0.7
    timeout: int = 30


@dataclass
class ModelResponse:
    """Response from a single model."""
    provider: str
    model_name: str
    content: str
    tokens_used: int
    latency: float  # seconds
    success: bool
    error: Optional[str] = None
    confidence: float = 1.0  # Model's confidence in response


@dataclass
class CoordinatedResponse:
    """Combined response from multiple models."""
    final_output: str
    strategy_used: CombinationStrategy
    individual_responses: List[ModelResponse]
    total_tokens: int
    total_cost: float
    avg_latency: float
    consensus_score: float  # How much models agreed (0-1)
    metadata: Dict[str, Any]


class MultiModelCoordinator:
    """Coordinates multiple AI models for improved results."""

    def __init__(self, llm_factory: LLMFactory):
        """Initialize coordinator with LLM factory."""
        self.llm_factory = llm_factory
        self.models: List[ModelConfig] = []
        self.performance_history: Dict[str, List[float]] = {}

    def add_model(self, config: ModelConfig) -> None:
        """Add a model to the coordination pool."""
        self.models.append(config)

    def remove_model(self, provider: str, model_name: str) -> bool:
        """Remove a model from the coordination pool."""
        initial_count = len(self.models)
        self.models = [
            m for m in self.models
            if not (m.provider == provider and m.model_name == model_name)
        ]
        return len(self.models) < initial_count

    async def execute(
        self,
        prompt: str,
        strategy: CombinationStrategy = CombinationStrategy.VOTING,
        task_complexity: TaskComplexity = TaskComplexity.MODERATE,
        max_models: Optional[int] = None,
        quality_threshold: float = 0.7,
        **kwargs
    ) -> CoordinatedResponse:
        """
        Execute prompt using multiple models with specified strategy.

        Args:
            prompt: The input prompt
            strategy: How to combine model outputs
            task_complexity: Complexity level for model selection
            max_models: Maximum number of models to use
            quality_threshold: Minimum quality score for model selection
            **kwargs: Additional parameters for models

        Returns:
            CoordinatedResponse with combined results
        """
        # Select models based on complexity and quality
        selected_models = self._select_models(
            task_complexity, max_models, quality_threshold
        )

        if not selected_models:
            raise ValueError("No models available for execution")

        # Execute on all selected models
        responses = await self._execute_on_models(selected_models, prompt, **kwargs)

        # Combine responses using strategy
        final_output = self._combine_responses(responses, strategy)

        # Calculate metrics
        total_tokens = sum(r.tokens_used for r in responses if r.success)
        total_cost = sum(
            r.tokens_used * m.cost_per_token
            for r, m in zip(responses, selected_models)
            if r.success
        )
        avg_latency = statistics.mean([r.latency for r in responses if r.success])
        consensus_score = self._calculate_consensus(responses)

        # Update performance history
        self._update_performance_history(responses)

        return CoordinatedResponse(
            final_output=final_output,
            strategy_used=strategy,
            individual_responses=responses,
            total_tokens=total_tokens,
            total_cost=total_cost,
            avg_latency=avg_latency,
            consensus_score=consensus_score,
            metadata={
                "models_used": len(selected_models),
                "successful_responses": sum(1 for r in responses if r.success),
                "task_complexity": task_complexity.value,
            }
        )

    def _select_models(
        self,
        complexity: TaskComplexity,
        max_models: Optional[int],
        quality_threshold: float
    ) -> List[ModelConfig]:
        """Select appropriate models based on task complexity."""
        # Filter by quality threshold
        candidates = [m for m in self.models if m.quality_score >= quality_threshold]

        # Sort by priority and quality
        candidates.sort(key=lambda m: (m.priority, -m.quality_score))

        # Determine number of models based on complexity
        if max_models is None:
            model_count = {
                TaskComplexity.SIMPLE: 1,
                TaskComplexity.MODERATE: 2,
                TaskComplexity.COMPLEX: 3,
                TaskComplexity.CRITICAL: 5,
            }.get(complexity, 2)
        else:
            model_count = max_models

        return candidates[:model_count]

    async def _execute_on_models(
        self,
        models: List[ModelConfig],
        prompt: str,
        **kwargs
    ) -> List[ModelResponse]:
        """Execute prompt on multiple models concurrently."""
        tasks = [
            self._execute_single_model(model, prompt, **kwargs)
            for model in models
        ]
        return await asyncio.gather(*tasks, return_exceptions=False)

    async def _execute_single_model(
        self,
        model_config: ModelConfig,
        prompt: str,
        **kwargs
    ) -> ModelResponse:
        """Execute prompt on a single model."""
        import time

        start_time = time.time()

        try:
            # Get LLM provider
            provider = self.llm_factory.create(model_config.provider)

            # Prepare messages
            messages = kwargs.get("messages", [{"role": "user", "content": prompt}])

            # Generate response
            response = await asyncio.wait_for(
                provider.generate(
                    messages=messages,
                    model=model_config.model_name,
                    max_tokens=model_config.max_tokens,
                    temperature=model_config.temperature,
                ),
                timeout=model_config.timeout
            )

            latency = time.time() - start_time

            return ModelResponse(
                provider=model_config.provider,
                model_name=model_config.model_name,
                content=response,
                tokens_used=len(response.split()) * 2,  # Rough estimate
                latency=latency,
                success=True,
                confidence=1.0
            )

        except asyncio.TimeoutError:
            return ModelResponse(
                provider=model_config.provider,
                model_name=model_config.model_name,
                content="",
                tokens_used=0,
                latency=time.time() - start_time,
                success=False,
                error="Timeout",
                confidence=0.0
            )
        except Exception as e:
            return ModelResponse(
                provider=model_config.provider,
                model_name=model_config.model_name,
                content="",
                tokens_used=0,
                latency=time.time() - start_time,
                success=False,
                error=str(e),
                confidence=0.0
            )

    def _combine_responses(
        self,
        responses: List[ModelResponse],
        strategy: CombinationStrategy
    ) -> str:
        """Combine multiple model responses using specified strategy."""
        successful_responses = [r for r in responses if r.success]

        if not successful_responses:
            return "Error: No successful responses from models"

        if strategy == CombinationStrategy.VOTING:
            return self._voting_strategy(successful_responses)
        elif strategy == CombinationStrategy.WEIGHTED_AVERAGE:
            return self._weighted_strategy(successful_responses)
        elif strategy == CombinationStrategy.CASCADE:
            return self._cascade_strategy(successful_responses)
        elif strategy == CombinationStrategy.ENSEMBLE:
            return self._ensemble_strategy(successful_responses)
        elif strategy == CombinationStrategy.BEST_OF_N:
            return self._best_of_n_strategy(successful_responses)
        else:
            return successful_responses[0].content

    def _voting_strategy(self, responses: List[ModelResponse]) -> str:
        """Select most common response (majority voting)."""
        contents = [r.content for r in responses]
        counter = Counter(contents)
        return counter.most_common(1)[0][0]

    def _weighted_strategy(self, responses: List[ModelResponse]) -> str:
        """Select response weighted by confidence and quality."""
        # Weight by confidence and historical performance
        best_response = max(
            responses,
            key=lambda r: r.confidence * self._get_model_quality(r.provider, r.model_name)
        )
        return best_response.content

    def _cascade_strategy(self, responses: List[ModelResponse]) -> str:
        """Return first successful response (already sorted by priority)."""
        return responses[0].content

    def _ensemble_strategy(self, responses: List[ModelResponse]) -> str:
        """Combine all responses into comprehensive output."""
        combined = "\n\n---\n\n".join([
            f"**{r.provider}/{r.model_name}**:\n{r.content}"
            for r in responses
        ])
        return f"Ensemble Response:\n\n{combined}"

    def _best_of_n_strategy(self, responses: List[ModelResponse]) -> str:
        """Select best response based on length and quality indicators."""
        # Prefer longer, more detailed responses from higher quality models
        best_response = max(
            responses,
            key=lambda r: (
                len(r.content) * self._get_model_quality(r.provider, r.model_name)
            )
        )
        return best_response.content

    def _calculate_consensus(self, responses: List[ModelResponse]) -> float:
        """Calculate how much models agree (0-1)."""
        successful = [r for r in responses if r.success]
        if len(successful) <= 1:
            return 1.0

        # Simple consensus: ratio of most common response
        contents = [r.content for r in successful]
        counter = Counter(contents)
        most_common_count = counter.most_common(1)[0][1]
        return most_common_count / len(successful)

    def _get_model_quality(self, provider: str, model_name: str) -> float:
        """Get quality score for a model from history."""
        key = f"{provider}/{model_name}"
        if key in self.performance_history:
            return statistics.mean(self.performance_history[key])
        return 0.5  # Default quality

    def _update_performance_history(self, responses: List[ModelResponse]) -> None:
        """Update performance history for models."""
        for response in responses:
            if response.success:
                key = f"{response.provider}/{response.model_name}"
                if key not in self.performance_history:
                    self.performance_history[key] = []

                # Quality based on latency and success
                quality = min(1.0, 10.0 / response.latency)  # Faster is better
                self.performance_history[key].append(quality)

                # Keep only recent history
                if len(self.performance_history[key]) > 100:
                    self.performance_history[key].pop(0)

    def get_performance_stats(self) -> Dict[str, Dict[str, float]]:
        """Get performance statistics for all models."""
        stats = {}
        for key, history in self.performance_history.items():
            if history:
                stats[key] = {
                    "avg_quality": statistics.mean(history),
                    "std_quality": statistics.stdev(history) if len(history) > 1 else 0.0,
                    "min_quality": min(history),
                    "max_quality": max(history),
                    "sample_count": len(history),
                }
        return stats

    def optimize_model_selection(self, cost_budget: float) -> List[ModelConfig]:
        """Optimize model selection based on cost budget."""
        # Sort models by quality/cost ratio
        models_with_ratio = [
            (m, m.quality_score / max(m.cost_per_token, 0.0001))
            for m in self.models
        ]
        models_with_ratio.sort(key=lambda x: x[1], reverse=True)

        # Select models within budget
        selected = []
        total_cost = 0.0
        for model, _ in models_with_ratio:
            estimated_cost = model.cost_per_token * 1000  # Estimate for 1k tokens
            if total_cost + estimated_cost <= cost_budget:
                selected.append(model)
                total_cost += estimated_cost

        return selected
