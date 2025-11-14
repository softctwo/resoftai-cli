"""
Security Scanner Plugin - Example Plugin for ResoftAI

This plugin demonstrates how to create a code quality plugin that
scans for security vulnerabilities.
"""
import re
from typing import Dict, Any, List
from resoftai.plugins.base import CodeQualityPlugin, PluginContext


class SecurityScannerPlugin(CodeQualityPlugin):
    """
    Security vulnerability scanner plugin

    Scans code for common security issues:
    - SQL injection vulnerabilities
    - Cross-site scripting (XSS)
    - Hardcoded secrets and credentials
    - Command injection
    - Path traversal
    - Insecure random number generation
    """

    def __init__(self, metadata, config):
        super().__init__(metadata, config)
        self.severity_threshold = config.get("severity_threshold", "medium")
        self.enabled_checks = config.get("enabled_checks", [
            "sql_injection",
            "xss",
            "hardcoded_secrets",
            "command_injection",
            "path_traversal",
            "weak_crypto"
        ])

        # Patterns for vulnerability detection
        self.patterns = {
            "sql_injection": [
                (r'execute\s*\([^)]*%[sdf]', "Potential SQL injection via string formatting"),
                (r'execute\s*\([^)]*\+', "Potential SQL injection via string concatenation"),
                (r'\.raw\s*\([^)]*\+', "Potential SQL injection in raw query"),
            ],
            "xss": [
                (r'\.innerHTML\s*=', "Potential XSS via innerHTML"),
                (r'document\.write\s*\(', "Potential XSS via document.write"),
                (r'dangerouslySetInnerHTML', "Potential XSS via dangerouslySetInnerHTML"),
            ],
            "hardcoded_secrets": [
                (r'password\s*=\s*["\'][^"\']+["\']', "Hardcoded password detected"),
                (r'api_key\s*=\s*["\'][^"\']+["\']', "Hardcoded API key detected"),
                (r'secret\s*=\s*["\'][^"\']+["\']', "Hardcoded secret detected"),
                (r'token\s*=\s*["\'][a-zA-Z0-9]{20,}["\']', "Hardcoded token detected"),
            ],
            "command_injection": [
                (r'os\.system\s*\(', "Potential command injection via os.system"),
                (r'subprocess\.call\s*\([^)]*shell\s*=\s*True', "Potential command injection with shell=True"),
                (r'exec\s*\(', "Use of exec() can be dangerous"),
                (r'eval\s*\(', "Use of eval() can be dangerous"),
            ],
            "path_traversal": [
                (r'open\s*\([^)]*\.\.\/', "Potential path traversal with ../"),
                (r'os\.path\.join\s*\([^)]*\.\.\/', "Potential path traversal in path.join"),
            ],
            "weak_crypto": [
                (r'random\.random\(\)', "Insecure random number generation"),
                (r'md5\s*\(', "MD5 is cryptographically broken"),
                (r'sha1\s*\(', "SHA1 is cryptographically weak"),
            ]
        }

        # Severity mapping
        self.severity_map = {
            "sql_injection": "high",
            "xss": "high",
            "hardcoded_secrets": "critical",
            "command_injection": "high",
            "path_traversal": "medium",
            "weak_crypto": "medium"
        }

    def load(self, context: PluginContext) -> bool:
        """Initialize plugin"""
        self.context = context
        self.context.log_info(f"Loading {self.metadata.name} v{self.metadata.version}")

        # Validate configuration
        if self.severity_threshold not in ["low", "medium", "high", "critical"]:
            self.context.log_error(f"Invalid severity threshold: {self.severity_threshold}")
            return False

        self.context.log_info(f"Severity threshold: {self.severity_threshold}")
        self.context.log_info(f"Enabled checks: {', '.join(self.enabled_checks)}")

        return True

    def activate(self) -> bool:
        """Activate plugin and register hooks"""
        self.context.log_info(f"Activating {self.metadata.name}")

        # Register filter hook for code analysis
        # This hook will be called during code quality checks
        # Note: Hook registration happens at the PluginManager level
        # This is a placeholder showing the intent

        self.context.log_info(f"{self.metadata.name} activated successfully")
        return True

    def deactivate(self) -> bool:
        """Deactivate plugin"""
        self.context.log_info(f"Deactivating {self.metadata.name}")
        # Unregister hooks here
        return True

    def unload(self) -> bool:
        """Clean up resources"""
        self.context.log_info(f"Unloading {self.metadata.name}")
        return True

    def get_tool_name(self) -> str:
        """Return tool identifier"""
        return "security_scanner"

    async def analyze_code(self, code: str, language: str) -> Dict[str, Any]:
        """
        Scan code for security vulnerabilities

        Args:
            code: Source code to analyze
            language: Programming language

        Returns:
            Analysis results with vulnerabilities found
        """
        issues = []
        lines = code.split('\n')

        # Scan each line for patterns
        for check_type in self.enabled_checks:
            if check_type not in self.patterns:
                continue

            patterns = self.patterns[check_type]
            severity = self.severity_map.get(check_type, "medium")

            for line_num, line in enumerate(lines, 1):
                for pattern, message in patterns:
                    if re.search(pattern, line, re.IGNORECASE):
                        issues.append({
                            "type": check_type,
                            "severity": severity,
                            "line": line_num,
                            "message": message,
                            "code": line.strip(),
                            "recommendation": self._get_recommendation(check_type)
                        })

        # Filter by severity threshold
        filtered_issues = self._filter_by_severity(issues)

        # Calculate security score (0-100)
        score = self._calculate_score(filtered_issues, len(lines))

        return {
            "tool": self.get_tool_name(),
            "issues": filtered_issues,
            "total_issues": len(filtered_issues),
            "issues_by_severity": self._count_by_severity(filtered_issues),
            "score": score,
            "passed": len(filtered_issues) == 0
        }

    def _filter_by_severity(self, issues: List[Dict]) -> List[Dict]:
        """Filter issues by severity threshold"""
        severity_levels = ["low", "medium", "high", "critical"]
        threshold_index = severity_levels.index(self.severity_threshold)

        return [
            issue for issue in issues
            if severity_levels.index(issue["severity"]) >= threshold_index
        ]

    def _count_by_severity(self, issues: List[Dict]) -> Dict[str, int]:
        """Count issues by severity"""
        counts = {"low": 0, "medium": 0, "high": 0, "critical": 0}
        for issue in issues:
            counts[issue["severity"]] += 1
        return counts

    def _calculate_score(self, issues: List[Dict], total_lines: int) -> float:
        """Calculate security score (0-100)"""
        if total_lines == 0:
            return 100.0

        # Weighted penalty by severity
        severity_weights = {
            "low": 1,
            "medium": 3,
            "high": 10,
            "critical": 25
        }

        penalty = sum(severity_weights.get(issue["severity"], 0) for issue in issues)

        # Normalize to lines of code
        penalty_per_100_lines = (penalty / total_lines) * 100

        # Score = 100 - penalty (minimum 0)
        score = max(0.0, 100.0 - penalty_per_100_lines)

        return round(score, 2)

    def _get_recommendation(self, check_type: str) -> str:
        """Get remediation recommendation for vulnerability type"""
        recommendations = {
            "sql_injection": "Use parameterized queries or an ORM to prevent SQL injection",
            "xss": "Sanitize user input and use safe DOM methods",
            "hardcoded_secrets": "Use environment variables or a secrets management service",
            "command_injection": "Avoid shell execution or properly sanitize inputs",
            "path_traversal": "Validate and sanitize file paths",
            "weak_crypto": "Use cryptographically secure random number generators and modern hash functions"
        }
        return recommendations.get(check_type, "Review and fix security issue")

    def get_config_schema(self) -> Dict[str, Any]:
        """Return JSON Schema for plugin configuration"""
        return {
            "type": "object",
            "properties": {
                "severity_threshold": {
                    "type": "string",
                    "enum": ["low", "medium", "high", "critical"],
                    "default": "medium",
                    "description": "Minimum severity level to report"
                },
                "enabled_checks": {
                    "type": "array",
                    "items": {
                        "type": "string",
                        "enum": [
                            "sql_injection",
                            "xss",
                            "hardcoded_secrets",
                            "command_injection",
                            "path_traversal",
                            "weak_crypto"
                        ]
                    },
                    "default": [
                        "sql_injection",
                        "xss",
                        "hardcoded_secrets",
                        "command_injection",
                        "path_traversal",
                        "weak_crypto"
                    ],
                    "description": "List of security checks to enable"
                }
            }
        }

    def validate_config(self, config: Dict[str, Any]) -> bool:
        """Validate plugin configuration"""
        # Check severity threshold
        if "severity_threshold" in config:
            if config["severity_threshold"] not in ["low", "medium", "high", "critical"]:
                return False

        # Check enabled checks
        if "enabled_checks" in config:
            valid_checks = set([
                "sql_injection", "xss", "hardcoded_secrets",
                "command_injection", "path_traversal", "weak_crypto"
            ])
            if not all(check in valid_checks for check in config["enabled_checks"]):
                return False

        return True
