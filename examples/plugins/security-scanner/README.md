# Security Scanner Plugin

A comprehensive security scanner plugin for ResoftAI that identifies common security vulnerabilities in your code.

## Features

### Vulnerability Detection

- **SQL Injection**: Detects potential SQL injection via string formatting and concatenation
- **Cross-Site Scripting (XSS)**: Identifies unsafe DOM manipulation
- **Hardcoded Secrets**: Finds hardcoded passwords, API keys, and tokens
- **Command Injection**: Detects unsafe command execution
- **Path Traversal**: Identifies potential directory traversal vulnerabilities
- **Weak Cryptography**: Flags use of insecure random number generation and deprecated hash functions

### Configuration Options

```json
{
  "severity_threshold": "medium",
  "enabled_checks": [
    "sql_injection",
    "xss",
    "hardcoded_secrets",
    "command_injection",
    "path_traversal",
    "weak_crypto"
  ]
}
```

## Installation

### Via ResoftAI CLI

```bash
resoftai plugin install security-scanner
```

### Via API

```bash
curl -X POST http://localhost:8000/api/plugins/123/install \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "config": {
      "severity_threshold": "high",
      "enabled_checks": ["sql_injection", "xss", "hardcoded_secrets"]
    }
  }'
```

### Manual Installation

1. Copy the plugin directory to your ResoftAI plugins folder:
   ```bash
   cp -r security-scanner /path/to/resoftai/plugins/
   ```

2. Restart ResoftAI to load the plugin

## Usage

Once installed, the security scanner will automatically run during code quality checks.

### Programmatic Usage

```python
from resoftai.plugins.manager import PluginManager
from resoftai.plugins.base import PluginContext

# Initialize plugin manager
manager = PluginManager(plugin_dirs=["/path/to/plugins"])

# Discover plugins
plugins = manager.discover_plugins()

# Load and activate plugin
context = PluginContext()
manager.load_plugin("security-scanner", context)
manager.activate_plugin("security-scanner")

# Get plugin instance
plugin = manager.get_plugin("security-scanner")

# Analyze code
code = """
password = "hardcoded123"
conn.execute(f"SELECT * FROM users WHERE id = {user_id}")
"""

result = await plugin.analyze_code(code, "python")

print(f"Security Score: {result['score']}/100")
print(f"Issues Found: {result['total_issues']}")

for issue in result['issues']:
    print(f"  [{issue['severity'].upper()}] Line {issue['line']}: {issue['message']}")
    print(f"    Code: {issue['code']}")
    print(f"    Fix: {issue['recommendation']}")
```

## Output Example

```json
{
  "tool": "security_scanner",
  "issues": [
    {
      "type": "hardcoded_secrets",
      "severity": "critical",
      "line": 1,
      "message": "Hardcoded password detected",
      "code": "password = \"hardcoded123\"",
      "recommendation": "Use environment variables or a secrets management service"
    },
    {
      "type": "sql_injection",
      "severity": "high",
      "line": 2,
      "message": "Potential SQL injection via string formatting",
      "code": "conn.execute(f\"SELECT * FROM users WHERE id = {user_id}\")",
      "recommendation": "Use parameterized queries or an ORM to prevent SQL injection"
    }
  ],
  "total_issues": 2,
  "issues_by_severity": {
    "low": 0,
    "medium": 0,
    "high": 1,
    "critical": 1
  },
  "score": 75.0,
  "passed": false
}
```

## Configuration Reference

### severity_threshold

Minimum severity level to report. Issues below this threshold will be filtered out.

- **Values**: `"low"`, `"medium"`, `"high"`, `"critical"`
- **Default**: `"medium"`

Example:
```json
{
  "severity_threshold": "high"
}
```

### enabled_checks

List of security checks to enable. Disable checks you don't need to improve performance.

- **Values**: Array of check names
- **Default**: All checks enabled

Available checks:
- `sql_injection`
- `xss`
- `hardcoded_secrets`
- `command_injection`
- `path_traversal`
- `weak_crypto`

Example:
```json
{
  "enabled_checks": ["sql_injection", "xss"]
}
```

## Integration with ResoftAI

The security scanner integrates seamlessly with ResoftAI's code quality pipeline:

1. **Automatic Scanning**: Runs during project creation and updates
2. **Real-time Feedback**: Provides immediate security feedback to agents
3. **Quality Gates**: Can be configured to block deployments with critical issues
4. **Audit Trail**: All findings are logged for compliance

## Best Practices

1. **Start with High Severity**: Begin with `severity_threshold: "high"` and gradually lower it
2. **Review False Positives**: Some patterns may flag legitimate code
3. **Combine with Other Tools**: Use alongside other security scanners for comprehensive coverage
4. **Keep Updated**: Regularly update the plugin for new vulnerability patterns
5. **Customize Patterns**: Fork and modify patterns for your specific needs

## Development

### Adding New Checks

To add a new vulnerability check:

1. Add patterns to `self.patterns` dictionary
2. Add severity mapping to `self.severity_map`
3. Add recommendation to `_get_recommendation()`
4. Update `enabled_checks` enum in config schema

Example:
```python
self.patterns["new_check"] = [
    (r'dangerous_function\s*\(', "Dangerous function usage"),
]
self.severity_map["new_check"] = "high"
```

### Testing

```bash
# Run plugin tests
pytest tests/test_security_scanner.py

# Test with sample code
python -m examples.plugins.security-scanner.test
```

## Troubleshooting

### Plugin Not Loading

1. Check plugin directory is in `PLUGIN_DIR`
2. Verify `plugin.json` is valid JSON
3. Check logs: `tail -f /app/logs/plugins.log`

### False Positives

Adjust `severity_threshold` or disable specific checks:

```json
{
  "enabled_checks": ["sql_injection", "hardcoded_secrets"]
}
```

### Performance Issues

For large codebases:
1. Disable non-critical checks
2. Increase severity threshold
3. Run scanning asynchronously

## Support

- **Documentation**: https://docs.resoftai.com/plugins/security-scanner
- **Issues**: https://github.com/resoftai/plugin-security-scanner/issues
- **Community**: https://discord.gg/resoftai

## License

MIT License - See LICENSE file for details

## Credits

Developed by the ResoftAI Team as an example plugin demonstrating the plugin system capabilities.
