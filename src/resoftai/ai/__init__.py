"""AI-powered advanced features for code analysis and improvement."""

from resoftai.ai.multi_model_collaboration import (
    MultiModelCollaborator,
    MultiModelCodeReviewer,
    CollaborationStrategy,
    ModelRole,
    ModelConfig,
    create_default_collaborator
)

from resoftai.ai.bug_prediction import (
    BugPredictor,
    BugPrediction,
    BugSeverity,
    BugCategory,
    BugPredictionReport,
    get_bug_predictor
)

from resoftai.ai.technical_debt import (
    TechnicalDebtAnalyzer,
    TechnicalDebtItem,
    TechnicalDebtReport,
    DebtType,
    DebtSeverity,
    get_technical_debt_analyzer
)

from resoftai.ai.refactoring import (
    RefactoringAnalyzer,
    RefactoringSuggestion,
    RefactoringReport,
    RefactoringType,
    get_refactoring_analyzer
)

from resoftai.ai.test_generation import (
    TestGenerator,
    TestFramework,
    GeneratedTest,
    TestGenerationReport,
    get_test_generator
)

__all__ = [
    # Multi-model collaboration
    'MultiModelCollaborator',
    'MultiModelCodeReviewer',
    'CollaborationStrategy',
    'ModelRole',
    'ModelConfig',
    'create_default_collaborator',

    # Bug prediction
    'BugPredictor',
    'BugPrediction',
    'BugSeverity',
    'BugCategory',
    'BugPredictionReport',
    'get_bug_predictor',

    # Technical debt
    'TechnicalDebtAnalyzer',
    'TechnicalDebtItem',
    'TechnicalDebtReport',
    'DebtType',
    'DebtSeverity',
    'get_technical_debt_analyzer',

    # Refactoring
    'RefactoringAnalyzer',
    'RefactoringSuggestion',
    'RefactoringReport',
    'RefactoringType',
    'get_refactoring_analyzer',

    # Test generation
    'TestGenerator',
    'TestFramework',
    'GeneratedTest',
    'TestGenerationReport',
    'get_test_generator'
]
