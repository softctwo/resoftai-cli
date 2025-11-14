"""Predictive Analysis Engine for project insights and forecasting."""
from enum import Enum
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass, field
from datetime import datetime, timedelta
import statistics
from collections import defaultdict

from resoftai.ai.multi_model_coordinator import MultiModelCoordinator, TaskComplexity


class RiskLevel(str, Enum):
    """Risk levels for project predictions."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class TrendDirection(str, Enum):
    """Trend direction for metrics."""
    IMPROVING = "improving"
    STABLE = "stable"
    DECLINING = "declining"


@dataclass
class ProgressPrediction:
    """Project progress prediction."""
    estimated_completion: datetime
    confidence: float  # 0-1
    current_progress: float  # 0-100
    projected_velocity: float  # tasks per day
    remaining_tasks: int
    bottlenecks: List[str]
    acceleration_opportunities: List[str]


@dataclass
class RiskAssessment:
    """Risk assessment for a project."""
    risk_level: RiskLevel
    risk_score: float  # 0-100
    identified_risks: List[Dict[str, Any]]
    mitigation_strategies: List[str]
    risk_factors: Dict[str, float]


@dataclass
class EffortEstimation:
    """Work effort estimation."""
    estimated_hours: float
    estimated_days: float
    confidence_range: Tuple[float, float]  # (min_hours, max_hours)
    complexity_score: float  # 0-100
    similar_projects: List[Dict[str, Any]]
    assumptions: List[str]


@dataclass
class QualityTrend:
    """Quality trend analysis."""
    current_quality: float  # 0-100
    trend: TrendDirection
    predicted_quality: float  # Future quality score
    quality_velocity: float  # Change rate
    improvement_areas: List[str]
    regression_risks: List[str]


@dataclass
class ResourceForecast:
    """Resource requirement forecast."""
    predicted_team_size: int
    predicted_budget: float
    predicted_infrastructure: Dict[str, Any]
    scaling_timeline: List[Dict[str, Any]]
    optimization_opportunities: List[str]


@dataclass
class PredictiveInsights:
    """Complete predictive analysis insights."""
    project_id: int
    analysis_timestamp: datetime
    progress_prediction: ProgressPrediction
    risk_assessment: RiskAssessment
    effort_estimation: EffortEstimation
    quality_trend: QualityTrend
    resource_forecast: ResourceForecast
    key_insights: List[str]
    recommended_actions: List[str]
    confidence_score: float  # Overall prediction confidence


class PredictiveAnalyzer:
    """AI-powered predictive analysis engine."""

    def __init__(self, coordinator: Optional[MultiModelCoordinator] = None):
        """Initialize predictive analyzer."""
        self.coordinator = coordinator
        self.historical_data: Dict[int, List[Dict[str, Any]]] = defaultdict(list)

    async def analyze_project(
        self,
        project_id: int,
        current_data: Dict[str, Any],
        historical_metrics: Optional[List[Dict[str, Any]]] = None
    ) -> PredictiveInsights:
        """
        Perform comprehensive predictive analysis for a project.

        Args:
            project_id: Project identifier
            current_data: Current project state and metrics
            historical_metrics: Historical project metrics

        Returns:
            PredictiveInsights with forecasts and recommendations
        """
        # Store historical data
        if historical_metrics:
            self.historical_data[project_id].extend(historical_metrics)

        # Perform individual analyses
        progress_pred = await self._predict_progress(project_id, current_data)
        risk_assess = await self._assess_risks(project_id, current_data)
        effort_est = await self._estimate_effort(project_id, current_data)
        quality_trend = await self._analyze_quality_trend(project_id, current_data)
        resource_forecast = await self._forecast_resources(project_id, current_data)

        # Generate insights and recommendations
        insights = await self._generate_insights(
            project_id,
            progress_pred,
            risk_assess,
            quality_trend
        )
        actions = await self._generate_recommendations(
            progress_pred,
            risk_assess,
            effort_est,
            quality_trend
        )

        # Calculate overall confidence
        confidence = self._calculate_overall_confidence(
            progress_pred.confidence,
            len(self.historical_data[project_id])
        )

        return PredictiveInsights(
            project_id=project_id,
            analysis_timestamp=datetime.now(),
            progress_prediction=progress_pred,
            risk_assessment=risk_assess,
            effort_estimation=effort_est,
            quality_trend=quality_trend,
            resource_forecast=resource_forecast,
            key_insights=insights,
            recommended_actions=actions,
            confidence_score=confidence
        )

    async def _predict_progress(
        self,
        project_id: int,
        current_data: Dict[str, Any]
    ) -> ProgressPrediction:
        """Predict project completion and progress."""
        # Extract metrics
        total_tasks = current_data.get('total_tasks', 100)
        completed_tasks = current_data.get('completed_tasks', 0)
        days_elapsed = current_data.get('days_elapsed', 1)

        # Calculate current velocity
        velocity = completed_tasks / max(days_elapsed, 1)

        # Predict completion
        remaining = total_tasks - completed_tasks
        days_remaining = remaining / max(velocity, 0.1)
        estimated_completion = datetime.now() + timedelta(days=days_remaining)

        # Calculate confidence based on data quality
        confidence = min(0.95, days_elapsed / 30)  # More confidence over time

        # Identify bottlenecks (using historical data)
        bottlenecks = self._identify_bottlenecks(project_id, current_data)

        # Find acceleration opportunities
        opportunities = [
            "Parallelize independent tasks",
            "Increase team capacity for critical path",
            "Automate repetitive tasks"
        ]

        return ProgressPrediction(
            estimated_completion=estimated_completion,
            confidence=confidence,
            current_progress=(completed_tasks / total_tasks * 100) if total_tasks > 0 else 0,
            projected_velocity=velocity,
            remaining_tasks=remaining,
            bottlenecks=bottlenecks,
            acceleration_opportunities=opportunities
        )

    async def _assess_risks(
        self,
        project_id: int,
        current_data: Dict[str, Any]
    ) -> RiskAssessment:
        """Assess project risks using AI."""
        # Calculate risk factors
        risk_factors = {}

        # Schedule risk
        progress = current_data.get('completed_tasks', 0) / max(current_data.get('total_tasks', 1), 1)
        time_progress = current_data.get('days_elapsed', 0) / max(current_data.get('total_days', 1), 1)
        schedule_risk = max(0, time_progress - progress) * 100
        risk_factors['schedule'] = schedule_risk

        # Quality risk
        quality_score = current_data.get('quality_score', 80)
        quality_risk = max(0, 100 - quality_score)
        risk_factors['quality'] = quality_risk

        # Team risk
        team_turnover = current_data.get('team_turnover', 0)
        team_risk = team_turnover * 20  # 20% risk per turnover
        risk_factors['team'] = team_risk

        # Technical debt risk
        code_issues = current_data.get('code_issues', 0)
        tech_debt_risk = min(100, code_issues * 2)
        risk_factors['technical_debt'] = tech_debt_risk

        # Calculate overall risk score
        risk_score = statistics.mean(risk_factors.values())

        # Determine risk level
        if risk_score < 25:
            risk_level = RiskLevel.LOW
        elif risk_score < 50:
            risk_level = RiskLevel.MEDIUM
        elif risk_score < 75:
            risk_level = RiskLevel.HIGH
        else:
            risk_level = RiskLevel.CRITICAL

        # Identify specific risks
        identified_risks = []
        for factor, score in risk_factors.items():
            if score > 30:
                identified_risks.append({
                    'factor': factor,
                    'score': score,
                    'description': f"High risk in {factor} area"
                })

        # Generate mitigation strategies
        mitigation = self._generate_mitigation_strategies(risk_factors)

        return RiskAssessment(
            risk_level=risk_level,
            risk_score=risk_score,
            identified_risks=identified_risks,
            mitigation_strategies=mitigation,
            risk_factors=risk_factors
        )

    async def _estimate_effort(
        self,
        project_id: int,
        current_data: Dict[str, Any]
    ) -> EffortEstimation:
        """Estimate remaining effort using historical data and AI."""
        # Get similar projects from history
        similar_projects = self._find_similar_projects(current_data)

        # Calculate complexity
        complexity_score = self._calculate_complexity(current_data)

        # Base estimation on similar projects
        if similar_projects:
            avg_hours = statistics.mean([p['total_hours'] for p in similar_projects])
            std_hours = statistics.stdev([p['total_hours'] for p in similar_projects]) if len(similar_projects) > 1 else avg_hours * 0.2
        else:
            # Fallback estimation
            remaining_tasks = current_data.get('total_tasks', 100) - current_data.get('completed_tasks', 0)
            avg_hours = remaining_tasks * 8  # 8 hours per task
            std_hours = avg_hours * 0.3

        # Adjust for complexity
        complexity_multiplier = 1 + (complexity_score / 100)
        estimated_hours = avg_hours * complexity_multiplier

        # Confidence range (±2 std dev)
        min_hours = max(0, estimated_hours - 2 * std_hours)
        max_hours = estimated_hours + 2 * std_hours

        return EffortEstimation(
            estimated_hours=estimated_hours,
            estimated_days=estimated_hours / 8,
            confidence_range=(min_hours, max_hours),
            complexity_score=complexity_score,
            similar_projects=similar_projects[:5],  # Top 5 similar
            assumptions=[
                "Team maintains current velocity",
                "No major scope changes",
                "Resources remain available"
            ]
        )

    async def _analyze_quality_trend(
        self,
        project_id: int,
        current_data: Dict[str, Any]
    ) -> QualityTrend:
        """Analyze quality trends and predict future quality."""
        # Get historical quality scores
        history = self.historical_data.get(project_id, [])
        quality_scores = [h.get('quality_score', 80) for h in history] + [current_data.get('quality_score', 80)]

        # Calculate trend
        if len(quality_scores) >= 3:
            # Linear regression for trend
            trend_slope = self._calculate_trend_slope(quality_scores)

            if trend_slope > 2:
                trend = TrendDirection.IMPROVING
            elif trend_slope < -2:
                trend = TrendDirection.DECLINING
            else:
                trend = TrendDirection.STABLE

            # Predict future quality
            predicted_quality = quality_scores[-1] + trend_slope * 5  # 5 periods ahead
            predicted_quality = max(0, min(100, predicted_quality))

            quality_velocity = trend_slope
        else:
            trend = TrendDirection.STABLE
            predicted_quality = quality_scores[-1]
            quality_velocity = 0

        # Identify improvement areas
        improvement_areas = []
        if current_data.get('test_coverage', 100) < 80:
            improvement_areas.append("Increase test coverage")
        if current_data.get('code_issues', 0) > 10:
            improvement_areas.append("Address code quality issues")
        if current_data.get('documentation', 100) < 70:
            improvement_areas.append("Improve documentation")

        # Identify regression risks
        regression_risks = []
        if trend == TrendDirection.DECLINING:
            regression_risks.append("Quality is declining - immediate action needed")
        if quality_velocity < -5:
            regression_risks.append("Rapid quality degradation detected")

        return QualityTrend(
            current_quality=quality_scores[-1],
            trend=trend,
            predicted_quality=predicted_quality,
            quality_velocity=quality_velocity,
            improvement_areas=improvement_areas,
            regression_risks=regression_risks
        )

    async def _forecast_resources(
        self,
        project_id: int,
        current_data: Dict[str, Any]
    ) -> ResourceForecast:
        """Forecast resource requirements."""
        # Estimate team size based on workload
        total_hours = current_data.get('estimated_total_hours', 1000)
        timeline_days = current_data.get('timeline_days', 90)
        hours_per_day_per_person = 6  # Productive hours

        predicted_team_size = int((total_hours / timeline_days) / hours_per_day_per_person) + 1

        # Estimate budget
        avg_hourly_rate = current_data.get('avg_hourly_rate', 100)
        predicted_budget = total_hours * avg_hourly_rate * 1.2  # 20% overhead

        # Infrastructure needs
        predicted_infrastructure = {
            'servers': max(1, predicted_team_size // 3),
            'storage_gb': total_hours * 10,  # 10GB per hour of work
            'ci_cd_runners': max(2, predicted_team_size // 2)
        }

        # Scaling timeline
        scaling_timeline = [
            {
                'phase': 'MVP',
                'team_size': max(2, predicted_team_size // 2),
                'timeline': f'{timeline_days // 3} days'
            },
            {
                'phase': 'Beta',
                'team_size': int(predicted_team_size * 0.75),
                'timeline': f'{timeline_days * 2 // 3} days'
            },
            {
                'phase': 'Production',
                'team_size': predicted_team_size,
                'timeline': f'{timeline_days} days'
            }
        ]

        # Optimization opportunities
        optimizations = [
            "Use automation tools to reduce manual effort",
            "Leverage cloud auto-scaling for cost optimization",
            "Implement CI/CD for faster delivery"
        ]

        return ResourceForecast(
            predicted_team_size=predicted_team_size,
            predicted_budget=predicted_budget,
            predicted_infrastructure=predicted_infrastructure,
            scaling_timeline=scaling_timeline,
            optimization_opportunities=optimizations
        )

    async def _generate_insights(
        self,
        project_id: int,
        progress: ProgressPrediction,
        risks: RiskAssessment,
        quality: QualityTrend
    ) -> List[str]:
        """Generate key insights using AI."""
        insights = []

        # Progress insights
        if progress.current_progress < 30 and progress.projected_velocity < 1:
            insights.append("Project is in early stages with low velocity - consider team ramp-up")

        if progress.remaining_tasks > 50 and progress.projected_velocity < 2:
            insights.append("High task backlog with low velocity - risk of delays")

        # Risk insights
        if risks.risk_level in [RiskLevel.HIGH, RiskLevel.CRITICAL]:
            insights.append(f"High risk detected ({risks.risk_level.value}) - immediate attention required")

        # Quality insights
        if quality.trend == TrendDirection.DECLINING:
            insights.append("Quality is declining - allocate time for technical debt")

        if quality.predicted_quality < 70:
            insights.append("Quality forecast is concerning - focus on quality improvements")

        # Use AI for deeper insights if coordinator available
        if self.coordinator:
            try:
                ai_insights = await self._get_ai_insights(progress, risks, quality)
                insights.extend(ai_insights)
            except Exception:
                pass

        return insights if insights else ["Project metrics are within normal ranges"]

    async def _generate_recommendations(
        self,
        progress: ProgressPrediction,
        risks: RiskAssessment,
        effort: EffortEstimation,
        quality: QualityTrend
    ) -> List[str]:
        """Generate actionable recommendations."""
        recommendations = []

        # Progress-based recommendations
        if progress.bottlenecks:
            recommendations.append(f"Address bottlenecks: {', '.join(progress.bottlenecks[:3])}")

        # Risk-based recommendations
        for strategy in risks.mitigation_strategies[:3]:
            recommendations.append(strategy)

        # Quality-based recommendations
        for area in quality.improvement_areas[:3]:
            recommendations.append(area)

        # Effort-based recommendations
        if effort.complexity_score > 75:
            recommendations.append("High complexity detected - consider breaking down into smaller phases")

        return recommendations if recommendations else ["Continue current approach"]

    def _identify_bottlenecks(self, project_id: int, current_data: Dict[str, Any]) -> List[str]:
        """Identify project bottlenecks."""
        bottlenecks = []

        # Check for blocked tasks
        if current_data.get('blocked_tasks', 0) > 5:
            bottlenecks.append("High number of blocked tasks")

        # Check for code review delays
        if current_data.get('pending_reviews', 0) > 10:
            bottlenecks.append("Code review backlog")

        # Check for testing delays
        if current_data.get('test_queue', 0) > 20:
            bottlenecks.append("Testing queue bottleneck")

        return bottlenecks

    def _generate_mitigation_strategies(self, risk_factors: Dict[str, float]) -> List[str]:
        """Generate risk mitigation strategies."""
        strategies = []

        for factor, score in risk_factors.items():
            if score > 50:
                if factor == 'schedule':
                    strategies.append("Add resources or reduce scope to meet deadlines")
                elif factor == 'quality':
                    strategies.append("Implement code review and testing processes")
                elif factor == 'team':
                    strategies.append("Focus on knowledge sharing and documentation")
                elif factor == 'technical_debt':
                    strategies.append("Allocate time for refactoring and debt reduction")

        return strategies

    def _find_similar_projects(self, current_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Find similar historical projects."""
        # Placeholder - in production, query database
        return []

    def _calculate_complexity(self, current_data: Dict[str, Any]) -> float:
        """Calculate project complexity score."""
        factors = {
            'total_tasks': current_data.get('total_tasks', 0) / 100,
            'team_size': current_data.get('team_size', 1) / 10,
            'tech_stack_count': current_data.get('tech_count', 1) / 5,
            'integration_count': current_data.get('integrations', 0) / 3,
        }

        complexity = sum(factors.values()) * 25
        return min(100, complexity)

    def _calculate_trend_slope(self, values: List[float]) -> float:
        """Calculate trend slope using linear regression."""
        n = len(values)
        if n < 2:
            return 0.0

        x = list(range(n))
        x_mean = statistics.mean(x)
        y_mean = statistics.mean(values)

        numerator = sum((x[i] - x_mean) * (values[i] - y_mean) for i in range(n))
        denominator = sum((x[i] - x_mean) ** 2 for i in range(n))

        if denominator == 0:
            return 0.0

        return numerator / denominator

    def _calculate_overall_confidence(self, base_confidence: float, data_points: int) -> float:
        """Calculate overall prediction confidence."""
        # More data points = higher confidence
        data_confidence = min(1.0, data_points / 30)
        return (base_confidence + data_confidence) / 2

    async def _get_ai_insights(
        self,
        progress: ProgressPrediction,
        risks: RiskAssessment,
        quality: QualityTrend
    ) -> List[str]:
        """Get additional insights from AI."""
        prompt = f"""Analyze this project status and provide 2-3 key insights:

Progress: {progress.current_progress:.1f}% complete, velocity: {progress.projected_velocity:.2f} tasks/day
Risk Level: {risks.risk_level.value}, score: {risks.risk_score:.1f}
Quality: {quality.current_quality:.1f}, trend: {quality.trend.value}

Provide concise, actionable insights."""

        try:
            response = await self.coordinator.execute(
                prompt=prompt,
                task_complexity=TaskComplexity.SIMPLE,
                max_models=1
            )

            # Parse insights from response
            insights = [line.strip() for line in response.final_output.split('\n') if line.strip() and not line.startswith('#')]
            return insights[:3]
        except Exception:
            return []
