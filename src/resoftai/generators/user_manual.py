"""User manual generator."""

from resoftai.generators.base import DocumentGenerator


class UserManualGenerator(DocumentGenerator):
    """Generates comprehensive user manual."""

    @property
    def document_name(self) -> str:
        return "User Manual"

    @property
    def document_filename(self) -> str:
        return "user-manual.md"

    async def generate_content(self) -> str:
        """Generate user manual content."""
        content = self._get_project_summary()

        content += """## Table of Contents

1. Introduction
2. Getting Started
3. Features and Functionality
4. Common Tasks
5. Troubleshooting
6. FAQ

## 1. Introduction

### Purpose
This manual provides comprehensive guidance for using the software system.

### Audience
This manual is designed for end users of the system.

### How to Use This Manual
Navigate using the table of contents above to find relevant information.

## 2. Getting Started

### First Login
Instructions for first-time users:
1. Open the application
2. Enter your credentials
3. Complete initial setup

### User Interface Overview
Description of the main interface elements and navigation.

### Basic Navigation
How to navigate through the application.

## 3. Features and Functionality

"""

        # Add feature descriptions from requirements
        if "detailed_requirements" in self.project_state.requirements:
            content += "### Main Features\n\n"
            content += "Detailed feature descriptions based on requirements.\n\n"

        content += """## 4. Common Tasks

### Task 1: [Common Task Name]
Step-by-step instructions:
1. Step one
2. Step two
3. Step three

### Task 2: [Common Task Name]
Step-by-step instructions:
1. Step one
2. Step two
3. Step three

## 5. Troubleshooting

### Common Issues

**Issue:** Unable to log in
**Solution:** Verify credentials and check internet connection

**Issue:** Feature not working
**Solution:** Check system requirements and refresh the application

## 6. Frequently Asked Questions

**Q: How do I reset my password?**
A: Click on "Forgot Password" on the login screen and follow instructions.

**Q: How do I contact support?**
A: Support contact information provided in the system.

## Support and Contact

For additional assistance:
- Email: support@example.com
- Phone: +1-XXX-XXX-XXXX
- Online Help: [URL]

"""

        return content
