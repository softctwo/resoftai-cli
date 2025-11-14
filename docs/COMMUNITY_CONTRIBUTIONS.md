# Community Contributions - Plugin and Template Marketplace

## Overview

This document outlines the community contribution system for ResoftAI plugins and templates. The system enables developers to share their plugins and templates with the community through a curated marketplace.

## Architecture

### Components

1. **Plugin Marketplace** (Existing + Enhancements)
   - Plugin publishing and versioning
   - Plugin discovery and installation
   - Community reviews and ratings
   - Plugin collections

2. **Template Marketplace** (New)
   - Template publishing to database
   - Template discovery and application
   - Template reviews and ratings
   - Template collections

3. **Review and Approval System**
   - Automated validation
   - Manual review workflow
   - Quality standards enforcement
   - Security scanning

4. **Contributor Recognition**
   - Contributor profiles
   - Badges and achievements
   - Download/install statistics
   - Featured contributors

## Data Models

### Template Marketplace Models

#### TemplateModel (Database)
```python
class TemplateModel(Base):
    """Template in marketplace - published by community"""
    id: int
    name: str
    slug: str (unique)
    description: str
    long_description: str

    # Author
    author_id: int
    author_name: str
    organization_id: Optional[int]

    # Classification
    category: TemplateCategory
    tags: JSON (List[str])

    # Version
    version: str
    min_platform_version: Optional[str]

    # Content
    template_data: JSON  # Serialized Template object
    package_url: Optional[str]  # Git repo or zip
    source_url: Optional[str]

    # Marketplace
    status: TemplateStatus  # draft, submitted, approved, rejected
    is_featured: bool
    is_official: bool

    # Statistics
    downloads_count: int
    installs_count: int
    rating_average: float
    rating_count: int

    # Timestamps
    created_at: datetime
    updated_at: datetime
    published_at: Optional[datetime]
```

#### TemplateVersion
```python
class TemplateVersion(Base):
    """Version history for templates"""
    id: int
    template_id: int
    version: str
    changelog: str
    template_data: JSON
    package_url: str
    is_stable: bool
    downloads_count: int
    created_at: datetime
```

#### TemplateInstallation
```python
class TemplateInstallation(Base):
    """Track template usage"""
    id: int
    template_id: int
    user_id: int
    project_id: int
    installed_version: str
    variables_used: JSON
    created_at: datetime
```

#### TemplateReview
```python
class TemplateReview(Base):
    """Template reviews"""
    id: int
    template_id: int
    user_id: int
    rating: int  # 1-5
    title: Optional[str]
    content: Optional[str]
    helpful_count: int
    created_at: datetime
```

### Contributor Models

#### ContributorProfile
```python
class ContributorProfile(Base):
    """Contributor profile and statistics"""
    id: int
    user_id: int

    # Profile
    display_name: str
    bio: Optional[str]
    avatar_url: Optional[str]
    website: Optional[str]
    github_url: Optional[str]

    # Statistics
    plugins_count: int
    templates_count: int
    total_downloads: int
    total_installs: int
    average_rating: float

    # Badges
    badges: JSON  # List of badge IDs
    is_verified: bool
    is_featured: bool

    # Timestamps
    created_at: datetime
    updated_at: datetime
```

#### ContributorBadge
```python
class ContributorBadge(Base):
    """Achievement badges for contributors"""
    id: int
    code: str (unique)  # "first_plugin", "top_rated", "verified"
    name: str
    description: str
    icon_url: str
    requirements: JSON  # Criteria for earning badge
    created_at: datetime
```

## API Endpoints

### Template Marketplace APIs

#### Publishing
```
POST   /api/templates/publish           - Publish new template
PUT    /api/templates/{id}               - Update template metadata
POST   /api/templates/{id}/versions     - Publish new version
DELETE /api/templates/{id}               - Delete template (author only)
```

#### Discovery
```
GET    /api/templates/marketplace        - Browse templates
GET    /api/templates/marketplace/search - Search templates
GET    /api/templates/marketplace/{id}   - Get template details
GET    /api/templates/categories         - List categories
GET    /api/templates/trending           - Trending templates
```

#### Usage
```
POST   /api/templates/{id}/install       - Track template usage
GET    /api/templates/installations      - User's template usage history
```

#### Reviews
```
POST   /api/templates/{id}/reviews       - Create review
GET    /api/templates/{id}/reviews       - List reviews
PUT    /api/templates/{id}/reviews/{review_id} - Update review
DELETE /api/templates/{id}/reviews/{review_id} - Delete review
```

### Plugin Version Management

#### Enhanced Plugin APIs
```
POST   /api/plugins/{id}/versions        - Publish new version
GET    /api/plugins/{id}/versions        - List versions
GET    /api/plugins/{id}/versions/{version} - Get version details
```

### Review and Approval APIs (Admin)

```
GET    /api/admin/plugins/pending        - List pending plugins
GET    /api/admin/templates/pending      - List pending templates
POST   /api/admin/plugins/{id}/approve   - Approve plugin
POST   /api/admin/plugins/{id}/reject    - Reject plugin
POST   /api/admin/templates/{id}/approve - Approve template
POST   /api/admin/templates/{id}/reject  - Reject template
```

### Contributor APIs

```
GET    /api/contributors                 - List contributors
GET    /api/contributors/{id}            - Get contributor profile
PUT    /api/contributors/me              - Update own profile
GET    /api/contributors/me/stats        - Get own statistics
GET    /api/contributors/leaderboard     - Contributor leaderboard
GET    /api/badges                       - List available badges
```

## Contribution Workflow

### Plugin Contribution Flow

1. **Development**
   - Developer creates plugin following SDK guidelines
   - Implements required interfaces
   - Adds comprehensive tests
   - Prepares documentation

2. **Submission**
   ```
   POST /api/plugins
   {
     "name": "My Awesome Plugin",
     "slug": "my-awesome-plugin",
     "category": "code_quality",
     "version": "1.0.0",
     "description": "...",
     "package_url": "https://github.com/...",
     "source_url": "https://github.com/...",
     "license": "MIT"
   }
   ```
   - Status: SUBMITTED
   - Automated validation triggered

3. **Automated Validation**
   - Package accessibility check
   - Manifest validation (plugin.json)
   - Security scanning (bandit, semgrep)
   - License verification
   - Documentation completeness

4. **Manual Review** (if auto-validation passes)
   - Code quality review
   - Security audit
   - Functionality verification
   - Documentation review

5. **Approval/Rejection**
   - Approved → Status: APPROVED, published_at set
   - Rejected → Status: REJECTED, feedback provided

6. **Version Updates**
   ```
   POST /api/plugins/{id}/versions
   {
     "version": "1.1.0",
     "changelog": "Added new features...",
     "package_url": "..."
   }
   ```

### Template Contribution Flow

1. **Development**
   - Create template structure
   - Define variables with validation
   - Add setup instructions
   - Test template application

2. **Submission**
   ```
   POST /api/templates/publish
   {
     "name": "FastAPI Microservice",
     "slug": "fastapi-microservice",
     "category": "microservice",
     "version": "1.0.0",
     "description": "...",
     "template_data": {
       "variables": [...],
       "files": [...],
       "directories": [...]
     },
     "source_url": "https://github.com/..."
   }
   ```

3. **Validation & Review**
   - Template structure validation
   - Variable validation
   - File content scanning
   - Documentation review

4. **Approval & Publishing**
   - Same as plugins

## Quality Standards

### Plugin Quality Checklist

- [ ] Valid plugin.json manifest
- [ ] Proper semantic versioning
- [ ] Comprehensive README
- [ ] At least 70% test coverage
- [ ] No critical security vulnerabilities
- [ ] Clear licensing information
- [ ] Example usage provided
- [ ] Dependencies documented
- [ ] Compatible with platform version

### Template Quality Checklist

- [ ] All variables properly documented
- [ ] Clear category and tags
- [ ] Working setup instructions
- [ ] Tested template application
- [ ] No hardcoded secrets or credentials
- [ ] Proper file structure
- [ ] README with usage examples
- [ ] License information

## Security Considerations

### Plugin Security

1. **Automated Scanning**
   - Static analysis with bandit
   - Dependency vulnerability scanning
   - License compliance check

2. **Sandboxing**
   - Plugins run in isolated environment
   - Limited filesystem access
   - Network policy restrictions

3. **Code Review**
   - Manual security audit for new plugins
   - Review of sensitive operations
   - Verification of permission requirements

### Template Security

1. **Content Scanning**
   - No hardcoded credentials
   - No malicious scripts
   - Safe default configurations

2. **Variable Validation**
   - Input sanitization
   - Type checking
   - Injection prevention

## Contributor Recognition

### Badge System

Badges are earned automatically based on achievements:

- **First Contribution**: First plugin or template published
- **Top Rated**: Average rating ≥ 4.5 with 10+ reviews
- **Popular Creator**: 1,000+ total downloads
- **Prolific**: 10+ published plugins/templates
- **Verified Developer**: Identity verified + official contributions
- **Community Champion**: Active in discussions, helpful reviews
- **Early Adopter**: Contributed in first 100 contributors

### Leaderboard

Rankings based on:
1. Total downloads (weight: 40%)
2. Average rating (weight: 30%)
3. Number of contributions (weight: 20%)
4. Community engagement (weight: 10%)

## Documentation Structure

### For Contributors

1. **CONTRIBUTING.md**
   - How to contribute
   - Code of conduct
   - Submission guidelines

2. **PLUGIN_DEVELOPMENT.md**
   - Plugin SDK reference
   - Plugin types and capabilities
   - Best practices
   - Example plugins

3. **TEMPLATE_DEVELOPMENT.md**
   - Template structure
   - Variable system
   - File templating
   - Best practices
   - Example templates

### For Users

1. **Plugin Discovery Guide**
   - How to find plugins
   - Installation process
   - Configuration

2. **Template Usage Guide**
   - Browsing templates
   - Applying templates
   - Customization

## Implementation Phases

### Phase 1: Foundation (Week 1)
- [x] Design architecture
- [ ] Create template database models
- [ ] Implement template CRUD operations
- [ ] Add template marketplace APIs

### Phase 2: Publishing (Week 2)
- [ ] Plugin version management API
- [ ] Template publishing API
- [ ] Validation framework
- [ ] Admin review APIs

### Phase 3: Community (Week 3)
- [ ] Contributor profiles
- [ ] Badge system
- [ ] Leaderboard
- [ ] Enhanced statistics

### Phase 4: Documentation (Week 4)
- [ ] Plugin development guide
- [ ] Template development guide
- [ ] Contribution guidelines
- [ ] API documentation

### Phase 5: Testing & Launch
- [ ] Integration tests
- [ ] Security testing
- [ ] Performance testing
- [ ] Beta launch with selected contributors

## Success Metrics

- Number of published plugins: Target 50+ in 3 months
- Number of published templates: Target 30+ in 3 months
- Active contributors: Target 100+ in 6 months
- Average plugin rating: Target ≥ 4.0
- Average template rating: Target ≥ 4.0
- Review turnaround time: Target < 48 hours
