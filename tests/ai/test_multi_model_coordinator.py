"""Tests for multi-model coordinator."""
import pytest
from unittest.mock import Mock, AsyncMock, patch

from resoftai.ai.multi_model_coordinator import (
    MultiModelCoordinator,
    CombinationStrategy,
    TaskComplexity,
    ModelConfig,
    ModelResponse
)
from resoftai.llm.factory import LLMFactory


class TestMultiModelCoordinator:
    """Test suite for MultiModelCoordinator."""

    @pytest.fixture
    def llm_factory(self):
        """Create a mock LLM factory."""
        factory = Mock(spec=LLMFactory)
        return factory

    @pytest.fixture
    def coordinator(self, llm_factory):
        """Create a coordinator instance."""
        return MultiModelCoordinator(llm_factory)

    @pytest.fixture
    def sample_model_config(self):
        """Create a sample model configuration."""
        return ModelConfig(
            provider="deepseek",
            model_name="deepseek-chat",
            weight=1.0,
            priority=1,
            cost_per_token=0.0001,
            quality_score=0.9
        )

    def test_add_model(self, coordinator, sample_model_config):
        """Test adding a model to coordinator."""
        coordinator.add_model(sample_model_config)

        assert len(coordinator.models) == 1
        assert coordinator.models[0].provider == "deepseek"

    def test_remove_model(self, coordinator, sample_model_config):
        """Test removing a model from coordinator."""
        coordinator.add_model(sample_model_config)
        success = coordinator.remove_model("deepseek", "deepseek-chat")

        assert success is True
        assert len(coordinator.models) == 0

    def test_select_models_by_complexity(self, coordinator):
        """Test model selection based on task complexity."""
        # Add multiple models
        for i in range(5):
            config = ModelConfig(
                provider=f"provider-{i}",
                model_name=f"model-{i}",
                priority=i + 1,
                quality_score=0.8 + i * 0.01
            )
            coordinator.add_model(config)

        # Select for simple task (should get 1 model)
        selected = coordinator._select_models(
            TaskComplexity.SIMPLE,
            max_models=None,
            quality_threshold=0.7
        )
        assert len(selected) == 1

        # Select for complex task (should get 3 models)
        selected = coordinator._select_models(
            TaskComplexity.COMPLEX,
            max_models=None,
            quality_threshold=0.7
        )
        assert len(selected) == 3

    def test_voting_strategy(self, coordinator):
        """Test voting combination strategy."""
        responses = [
            ModelResponse("p1", "m1", "Answer A", 100, 1.0, True, confidence=1.0),
            ModelResponse("p2", "m2", "Answer A", 100, 1.0, True, confidence=1.0),
            ModelResponse("p3", "m3", "Answer B", 100, 1.0, True, confidence=1.0),
        ]

        result = coordinator._combine_responses(responses, CombinationStrategy.VOTING)
        assert result == "Answer A"  # Majority wins

    def test_cascade_strategy(self, coordinator):
        """Test cascade combination strategy."""
        responses = [
            ModelResponse("p1", "m1", "First answer", 100, 1.0, True, confidence=1.0),
            ModelResponse("p2", "m2", "Second answer", 100, 1.0, True, confidence=1.0),
        ]

        result = coordinator._combine_responses(responses, CombinationStrategy.CASCADE)
        assert result == "First answer"  # Takes first successful

    def test_calculate_consensus(self, coordinator):
        """Test consensus calculation."""
        # Perfect consensus
        responses = [
            ModelResponse("p1", "m1", "Same answer", 100, 1.0, True),
            ModelResponse("p2", "m2", "Same answer", 100, 1.0, True),
            ModelResponse("p3", "m3", "Same answer", 100, 1.0, True),
        ]
        consensus = coordinator._calculate_consensus(responses)
        assert consensus == 1.0

        # Partial consensus
        responses = [
            ModelResponse("p1", "m1", "Answer A", 100, 1.0, True),
            ModelResponse("p2", "m2", "Answer A", 100, 1.0, True),
            ModelResponse("p3", "m3", "Answer B", 100, 1.0, True),
        ]
        consensus = coordinator._calculate_consensus(responses)
        assert consensus == 2/3  # 2 out of 3 agree

    def test_performance_tracking(self, coordinator):
        """Test performance history tracking."""
        responses = [
            ModelResponse("deepseek", "chat", "answer", 100, 2.0, True),
            ModelResponse("deepseek", "chat", "answer", 100, 3.0, True),
        ]

        coordinator._update_performance_history(responses)

        assert "deepseek/chat" in coordinator.performance_history
        assert len(coordinator.performance_history["deepseek/chat"]) == 2

    def test_optimize_model_selection(self, coordinator):
        """Test cost-based model optimization."""
        # Add models with different costs
        models = [
            ModelConfig("p1", "m1", cost_per_token=0.001, quality_score=0.9),
            ModelConfig("p2", "m2", cost_per_token=0.0001, quality_score=0.8),
            ModelConfig("p3", "m3", cost_per_token=0.01, quality_score=0.95),
        ]

        for model in models:
            coordinator.add_model(model)

        # Optimize for budget
        selected = coordinator.optimize_model_selection(cost_budget=2.0)

        # Should prefer high quality/cost ratio
        assert len(selected) > 0
        assert all(m.cost_per_token <= 0.001 for m in selected)
