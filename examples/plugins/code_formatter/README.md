# Python Code Formatter Plugin

A ResoftAI plugin that automatically formats Python code using Black and isort.

## Features

- ✅ Formats Python code with Black
- ✅ Sorts imports with isort
- ✅ Configurable line length
- ✅ Multiple isort profiles
- ✅ Automatic code fixing

## Installation

1. Ensure Black and isort are installed:
```bash
pip install black isort
```

2. Install the plugin:
```bash
# Via ResoftAI marketplace
resoftai plugin install python-code-formatter

# Or manually copy to plugins directory
cp -r code_formatter ~/.resoftai/plugins/
```

## Configuration

The plugin supports the following configuration options:

```json
{
  "black_line_length": 100,
  "use_isort": true,
  "isort_profile": "black"
}
```

### Options

- **black_line_length** (integer, default: 100): Maximum line length for Black formatter (50-200)
- **use_isort** (boolean, default: true): Enable import sorting with isort
- **isort_profile** (string, default: "black"): isort profile to use
  - Options: "black", "django", "pycharm", "google"

## Usage

### As a Code Quality Check

The plugin automatically runs during code analysis:

```python
from resoftai.plugins.manager import PluginManager

manager = PluginManager(["/path/to/plugins"])
manager.discover_plugins()
manager.load_plugin("python-code-formatter", context)
manager.activate_plugin("python-code-formatter")

plugin = manager.get_plugin("python-code-formatter")
result = plugin.analyze_code(python_code, language="python")

if result["needs_formatting"]:
    print("Code needs formatting")
    print(f"Tools: {result['tools_used']}")
    for issue in result["issues"]:
        print(f"  - {issue['tool']}: {issue['message']}")
```

### Automatic Code Fixing

```python
formatted_code = plugin.fix_code(python_code, language="python")
print(formatted_code)
```

## Example

**Before formatting:**

```python
import os
import sys
from typing import List,Dict
def hello(  x,y   ):
    return    x+y
```

**After formatting:**

```python
import os
import sys
from typing import Dict, List


def hello(x, y):
    return x + y
```

## Development

### Running Tests

```bash
pytest tests/
```

### Project Structure

```
code_formatter/
├── plugin.json          # Plugin manifest
├── formatter_plugin.py  # Main plugin code
├── README.md           # This file
└── tests/              # Test suite
    └── test_formatter.py
```

## Dependencies

- Python ≥ 3.8
- Black ≥ 22.0.0
- isort ≥ 5.0.0

## License

MIT License

## Author

ResoftAI Team

## Support

For issues and feature requests, please visit:
https://github.com/resoftai/plugins/issues
