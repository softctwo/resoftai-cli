# Contributing to ResoftAI

Thank you for your interest in contributing to ResoftAI! This document provides guidelines and instructions for contributing plugins, templates, and code to the project.

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Ways to Contribute](#ways-to-contribute)
- [Plugin Contributions](#plugin-contributions)
- [Template Contributions](#template-contributions)
- [Code Contributions](#code-contributions)
- [Review Process](#review-process)
- [Community Guidelines](#community-guidelines)

## Code of Conduct

### Our Standards

We are committed to providing a welcoming and inspiring community for all. Please be respectful and constructive in your interactions.

**Expected Behavior:**
- Be respectful and inclusive
- Provide constructive feedback
- Focus on what is best for the community
- Show empathy towards other community members

**Unacceptable Behavior:**
- Harassment, discrimination, or trolling
- Publishing others' private information
- Spam or self-promotion without value
- Other conduct which could reasonably be considered inappropriate

## Ways to Contribute

### 1. Plugin Contributions

Share your custom plugins with the community! Plugins extend ResoftAI's capabilities by adding:
- Custom AI agents
- New LLM provider integrations
- Code quality tools (linters, formatters)
- Third-party integrations (Jira, Slack, GitHub, etc.)
- Workflow automation
- And more!

**See**: [docs/PLUGIN_DEVELOPMENT.md](docs/PLUGIN_DEVELOPMENT.md) for detailed instructions.

**Quick Start:**
1. Develop your plugin using the Plugin SDK
2. Test thoroughly
3. Submit via API or web interface
4. Wait for review and approval

### 2. Template Contributions

Share project templates to help others get started quickly!

Templates can include:
- Web application scaffolds
- REST API boilerplates
- CLI tool templates
- Microservice architectures
- Data pipeline templates
- Machine learning project templates

**See**: [docs/TEMPLATE_DEVELOPMENT.md](docs/TEMPLATE_DEVELOPMENT.md) for detailed instructions.

**Quick Start:**
1. Create your template structure
2. Define variables and customization options
3. Test template application
4. Submit via API or web interface
5. Wait for review and approval

### 3. Code Contributions

Contribute to the ResoftAI core platform:
- Bug fixes
- New features
- Documentation improvements
- Performance optimizations
- Test coverage improvements

**Process:**
1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Write tests
5. Run test suite (`pytest tests/`)
6. Commit your changes (`git commit -m 'Add amazing feature'`)
7. Push to branch (`git push origin feature/amazing-feature`)
8. Open a Pull Request

## Plugin Contributions

### Plugin Quality Standards

Before submitting a plugin, ensure it meets these requirements:

#### Required
- [ ] Valid `plugin.json` manifest file
- [ ] Semantic versioning (e.g., 1.0.0)
- [ ] Comprehensive README.md
- [ ] Clear licensing information (MIT, Apache-2.0, etc.)
- [ ] No critical security vulnerabilities
- [ ] Compatible with current ResoftAI platform version

#### Recommended
- [ ] At least 70% test coverage
- [ ] Example usage in README
- [ ] Detailed API documentation
- [ ] Change log for updates
- [ ] Type hints (for Python plugins)

### Plugin Submission Process

1. **Prepare Your Plugin**
   ```bash
   # Ensure your plugin structure is correct
   my-plugin/
   ├── plugin.json          # Manifest
   ├── README.md            # Documentation
   ├── __init__.py          # Entry point
   ├── requirements.txt     # Dependencies
   └── tests/               # Test suite
   ```

2. **Test Locally**
   ```bash
   # Run your plugin tests
   PYTHONPATH=src pytest my-plugin/tests/

   # Test plugin loading
   python -m resoftai.plugins.manager --test my-plugin/
   ```

3. **Submit via API**
   ```python
   import requests

   response = requests.post(
       "https://api.resoftai.com/api/plugins",
       json={
           "name": "My Awesome Plugin",
           "slug": "my-awesome-plugin",
           "category": "code_quality",
           "version": "1.0.0",
           "description": "...",
           "package_url": "https://github.com/username/my-plugin",
           "source_url": "https://github.com/username/my-plugin",
           "license": "MIT"
       },
       headers={"Authorization": f"Bearer {token}"}
   )
   ```

4. **Review Process** (see below)

### Plugin Update Process

To publish a new version:

```python
response = requests.post(
    f"https://api.resoftai.com/api/plugins/{plugin_id}/versions",
    json={
        "version": "1.1.0",
        "changelog": "Added new features...",
        "package_url": "...",
        "package_checksum": "sha256:..."
    },
    headers={"Authorization": f"Bearer {token}"}
)
```

## Template Contributions

### Template Quality Standards

#### Required
- [ ] Clear template name and description
- [ ] All variables properly documented
- [ ] Working setup instructions
- [ ] Tested template application
- [ ] No hardcoded secrets or credentials
- [ ] Proper file structure
- [ ] License information

#### Recommended
- [ ] Example screenshots
- [ ] Detailed variable descriptions
- [ ] Post-setup instructions
- [ ] Common troubleshooting tips

### Template Submission Process

1. **Prepare Your Template**
   ```python
   from resoftai.templates.base import Template, TemplateVariable, TemplateFile, TemplateCategory

   template = Template(
       id="my-fastapi-api",
       name="FastAPI REST API",
       description="Complete FastAPI REST API with authentication",
       category=TemplateCategory.REST_API,
       variables=[
           TemplateVariable(
               name="project_name",
               description="Name of your project",
               required=True
           ),
           TemplateVariable(
               name="database",
               description="Database type",
               type="choice",
               choices=["postgresql", "mysql", "sqlite"],
               default="postgresql"
           )
       ],
       files=[...],
       directories=[...]
   )
   ```

2. **Test Your Template**
   ```python
   from resoftai.templates.manager import TemplateManager
   from pathlib import Path

   manager = TemplateManager()
   manager.register_template(template)

   # Test application
   manager.apply_template(
       template_id="my-fastapi-api",
       output_dir=Path("/tmp/test-project"),
       variables={
           "project_name": "MyAPI",
           "database": "postgresql"
       }
   )
   ```

3. **Submit via API**
   ```python
   response = requests.post(
       "https://api.resoftai.com/api/templates/marketplace",
       json={
           "name": "FastAPI REST API",
           "slug": "fastapi-rest-api",
           "category": "rest_api",
           "version": "1.0.0",
           "description": "...",
           "template_data": template.to_dict(),
           "source_url": "https://github.com/username/template",
           "license": "MIT"
       },
       headers={"Authorization": f"Bearer {token}"}
   )
   ```

## Review Process

### Automated Review

When you submit a plugin or template, it undergoes automated validation:

**Plugins:**
- [ ] Package accessibility check
- [ ] Manifest validation
- [ ] Security scanning (bandit, semgrep)
- [ ] License verification
- [ ] Documentation completeness check

**Templates:**
- [ ] Structure validation
- [ ] Variable definition check
- [ ] File content scanning (no secrets)
- [ ] Documentation completeness

### Manual Review

If automated checks pass, your submission enters manual review:

1. **Code Quality Review** (2-3 days)
   - Code readability and maintainability
   - Best practices adherence
   - Architecture and design

2. **Security Audit** (1-2 days)
   - Security vulnerability scan
   - Permission requirements review
   - Data handling practices

3. **Functionality Verification** (1-2 days)
   - Installation testing
   - Feature testing
   - Compatibility testing

4. **Documentation Review** (1 day)
   - README completeness
   - API documentation
   - Example clarity

**Total Review Time:** ~5-7 days

### Review Outcomes

**Approved ✓**
- Your contribution is published to the marketplace
- You receive email notification
- Contributor profile is updated
- Eligible for badges

**Rejected ✗**
- You receive detailed feedback
- You can address issues and resubmit
- No penalties for rejected submissions

### Resubmission

If your submission is rejected, you can:
1. Review the feedback provided
2. Make necessary changes
3. Update your plugin/template
4. Resubmit (no limit on resubmissions)

## Community Guidelines

### Contributor Recognition

We value our contributors! Here's how we recognize your efforts:

**Badges:**
- 🥉 First Contribution - Your first approved plugin or template
- ⭐ Top Rated - Average rating ≥ 4.5 with 10+ reviews
- 🔥 Popular Creator - 1,000+ total downloads
- 🚀 Prolific - 10+ approved plugins/templates
- ✓ Verified Developer - Identity verified contributor
- 💬 Community Champion - Active helper in discussions

**Leaderboard:**
- Top contributors ranked by downloads, ratings, and contributions
- Monthly featured contributors
- Annual contributor awards

**Benefits:**
- Contributor badge on your profile
- Featured in ResoftAI blog posts
- Early access to new features (for top contributors)
- Direct communication channel with ResoftAI team

### Best Practices

1. **Documentation First**
   - Write clear documentation
   - Include examples
   - Explain use cases

2. **Test Thoroughly**
   - Write comprehensive tests
   - Test edge cases
   - Test on different environments

3. **Version Responsibly**
   - Follow semantic versioning
   - Document breaking changes
   - Provide migration guides

4. **Respond to Feedback**
   - Address review comments promptly
   - Engage with users
   - Fix bugs quickly

5. **Stay Updated**
   - Keep dependencies updated
   - Maintain compatibility
   - Update documentation

### Getting Help

**Documentation:**
- [Plugin Development Guide](docs/PLUGIN_DEVELOPMENT.md)
- [Template Development Guide](docs/TEMPLATE_DEVELOPMENT.md)
- [API Documentation](docs/API.md)
- [Community Contributions Overview](docs/COMMUNITY_CONTRIBUTIONS.md)

**Community:**
- GitHub Discussions: Ask questions and share ideas
- Discord: Real-time chat with other contributors
- Stack Overflow: Tag questions with `resoftai`

**Support:**
- GitHub Issues: Bug reports and feature requests
- Email: contributors@resoftai.com
- Documentation: https://docs.resoftai.com

## License

By contributing to ResoftAI, you agree that your contributions will be licensed under the project's MIT License. You retain copyright to your contributions, but grant ResoftAI and users of ResoftAI the right to use, modify, and distribute your contributions.

---

Thank you for contributing to ResoftAI! Your contributions help make software development more accessible and efficient for everyone. 🚀
