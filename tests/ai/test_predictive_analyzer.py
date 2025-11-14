"""Tests for predictive analyzer."""
import pytest
from datetime import datetime, timedelta

from resoftai.ai.predictive_analyzer import (
    PredictiveAnalyzer,
    RiskLevel,
    TrendDirection
)


class TestPredictiveAnalyzer:
    """Test suite for PredictiveAnalyzer."""

    @pytest.fixture
    def analyzer(self):
        """Create an analyzer instance."""
        return PredictiveAnalyzer()

    @pytest.fixture
    def sample_project_data(self):
        """Create sample project data."""
        return {
            'total_tasks': 100,
            'completed_tasks': 50,
            'days_elapsed': 10,
            'total_days': 30,
            'quality_score': 85,
            'team_size': 5,
            'team_turnover': 0,
            'code_issues': 5,
            'test_coverage': 75
        }

    @pytest.mark.asyncio
    async def test_predict_progress(self, analyzer, sample_project_data):
        """Test progress prediction."""
        prediction = await analyzer._predict_progress(1, sample_project_data)

        assert prediction is not None
        assert prediction.remaining_tasks == 50
        assert prediction.current_progress == 50.0
        assert prediction.projected_velocity > 0
        assert isinstance(prediction.estimated_completion, datetime)

    @pytest.mark.asyncio
    async def test_assess_risks(self, analyzer, sample_project_data):
        """Test risk assessment."""
        assessment = await analyzer._assess_risks(1, sample_project_data)

        assert assessment is not None
        assert assessment.risk_level in RiskLevel
        assert 0 <= assessment.risk_score <= 100
        assert 'schedule' in assessment.risk_factors
        assert 'quality' in assessment.risk_factors
        assert 'team' in assessment.risk_factors

    @pytest.mark.asyncio
    async def test_high_risk_detection(self, analyzer):
        """Test high risk detection."""
        high_risk_data = {
            'total_tasks': 100,
            'completed_tasks': 10,  # Very behind
            'days_elapsed': 50,  # Too much time spent
            'total_days': 60,
            'quality_score': 40,  # Low quality
            'team_turnover': 3,  # High turnover
            'code_issues': 100,  # Many issues
            'team_size': 2
        }

        assessment = await analyzer._assess_risks(1, high_risk_data)

        assert assessment.risk_level in [RiskLevel.HIGH, RiskLevel.CRITICAL]
        assert assessment.risk_score > 50

    @pytest.mark.asyncio
    async def test_estimate_effort(self, analyzer, sample_project_data):
        """Test effort estimation."""
        estimation = await analyzer._estimate_effort(1, sample_project_data)

        assert estimation is not None
        assert estimation.estimated_hours > 0
        assert estimation.estimated_days > 0
        assert estimation.confidence_range[0] <= estimation.confidence_range[1]
        assert 0 <= estimation.complexity_score <= 100

    @pytest.mark.asyncio
    async def test_analyze_quality_trend(self, analyzer, sample_project_data):
        """Test quality trend analysis."""
        # Add historical data
        analyzer.historical_data[1] = [
            {'quality_score': 70},
            {'quality_score': 75},
            {'quality_score': 80},
        ]

        trend = await analyzer._analyze_quality_trend(1, sample_project_data)

        assert trend is not None
        assert trend.trend in TrendDirection
        assert 0 <= trend.current_quality <= 100
        assert 0 <= trend.predicted_quality <= 100

    @pytest.mark.asyncio
    async def test_improving_quality_trend(self, analyzer):
        """Test detection of improving quality trend."""
        analyzer.historical_data[1] = [
            {'quality_score': 60},
            {'quality_score': 70},
            {'quality_score': 80},
        ]

        current_data = {'quality_score': 85}
        trend = await analyzer._analyze_quality_trend(1, current_data)

        assert trend.trend == TrendDirection.IMPROVING

    @pytest.mark.asyncio
    async def test_declining_quality_trend(self, analyzer):
        """Test detection of declining quality trend."""
        analyzer.historical_data[1] = [
            {'quality_score': 90},
            {'quality_score': 80},
            {'quality_score': 70},
        ]

        current_data = {'quality_score': 60}
        trend = await analyzer._analyze_quality_trend(1, current_data)

        assert trend.trend == TrendDirection.DECLINING
        assert len(trend.regression_risks) > 0

    @pytest.mark.asyncio
    async def test_forecast_resources(self, analyzer, sample_project_data):
        """Test resource forecasting."""
        sample_project_data['estimated_total_hours'] = 1000
        sample_project_data['timeline_days'] = 90
        sample_project_data['avg_hourly_rate'] = 100

        forecast = await analyzer._forecast_resources(1, sample_project_data)

        assert forecast is not None
        assert forecast.predicted_team_size > 0
        assert forecast.predicted_budget > 0
        assert 'servers' in forecast.predicted_infrastructure
        assert len(forecast.scaling_timeline) > 0

    def test_calculate_complexity(self, analyzer):
        """Test complexity calculation."""
        data = {
            'total_tasks': 200,
            'team_size': 10,
            'tech_count': 5,
            'integrations': 3
        }

        complexity = analyzer._calculate_complexity(data)

        assert 0 <= complexity <= 100
        assert complexity > 0  # Should have some complexity

    def test_calculate_trend_slope(self, analyzer):
        """Test trend slope calculation."""
        # Increasing trend
        values = [10, 20, 30, 40, 50]
        slope = analyzer._calculate_trend_slope(values)
        assert slope > 0

        # Decreasing trend
        values = [50, 40, 30, 20, 10]
        slope = analyzer._calculate_trend_slope(values)
        assert slope < 0

        # Flat trend
        values = [50, 50, 50, 50, 50]
        slope = analyzer._calculate_trend_slope(values)
        assert abs(slope) < 0.01

    @pytest.mark.asyncio
    async def test_analyze_project_integration(self, analyzer, sample_project_data):
        """Test complete project analysis integration."""
        insights = await analyzer.analyze_project(
            project_id=1,
            current_data=sample_project_data
        )

        assert insights is not None
        assert insights.project_id == 1
        assert insights.progress_prediction is not None
        assert insights.risk_assessment is not None
        assert insights.effort_estimation is not None
        assert insights.quality_trend is not None
        assert insights.resource_forecast is not None
        assert len(insights.key_insights) > 0
        assert len(insights.recommended_actions) > 0
        assert 0 <= insights.confidence_score <= 1.0

    def test_identify_bottlenecks(self, analyzer):
        """Test bottleneck identification."""
        data_with_bottlenecks = {
            'blocked_tasks': 10,
            'pending_reviews': 15,
            'test_queue': 25
        }

        bottlenecks = analyzer._identify_bottlenecks(1, data_with_bottlenecks)

        assert len(bottlenecks) > 0
        assert any('blocked' in b.lower() for b in bottlenecks)
        assert any('review' in b.lower() for b in bottlenecks)
        assert any('test' in b.lower() for b in bottlenecks)

    def test_generate_mitigation_strategies(self, analyzer):
        """Test mitigation strategy generation."""
        risk_factors = {
            'schedule': 60,
            'quality': 70,
            'team': 30,
            'technical_debt': 80
        }

        strategies = analyzer._generate_mitigation_strategies(risk_factors)

        assert len(strategies) > 0
        # High technical debt should have strategy
        assert any('debt' in s.lower() or 'refactor' in s.lower() for s in strategies)
