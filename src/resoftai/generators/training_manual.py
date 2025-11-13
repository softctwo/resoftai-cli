"""Training manual generator."""

from resoftai.generators.base import DocumentGenerator


class TrainingManualGenerator(DocumentGenerator):
    """Generates comprehensive training manual."""

    @property
    def document_name(self) -> str:
        return "Training Manual"

    @property
    def document_filename(self) -> str:
        return "training-manual.md"

    async def generate_content(self) -> str:
        """Generate training manual content."""
        content = self._get_project_summary()

        content += """## Training Program Overview

### Objectives
By the end of this training, users will be able to:
- Navigate the system effectively
- Perform common tasks independently
- Understand key features and functionality
- Troubleshoot basic issues

### Training Duration
Estimated time: 2-4 hours (depending on user experience)

### Prerequisites
- Basic computer skills
- Access to the system
- Training environment or demo account

## Module 1: Introduction and Setup

### Duration: 30 minutes

### Topics Covered:
1. System overview and purpose
2. Logging in and initial setup
3. User interface tour
4. Basic navigation

### Hands-on Exercise:
- Log into the system
- Explore the main interface
- Navigate between different sections

### Assessment:
Quiz on system navigation and basic features

## Module 2: Core Features

### Duration: 60 minutes

### Topics Covered:
1. Main feature overview
2. Step-by-step feature usage
3. Best practices
4. Common workflows

### Hands-on Exercise:
- Complete a typical workflow
- Practice using core features
- Create sample data/items

### Assessment:
Practical exercise completing a full workflow

## Module 3: Advanced Features

### Duration: 45 minutes

### Topics Covered:
1. Advanced functionality
2. Customization options
3. Integration features
4. Reporting and analytics

### Hands-on Exercise:
- Use advanced features
- Generate reports
- Customize settings

### Assessment:
Advanced feature usage exercise

## Module 4: Administration (if applicable)

### Duration: 45 minutes

### Topics Covered:
1. User management
2. System configuration
3. Security settings
4. Backup and maintenance

### Hands-on Exercise:
- Add/remove users
- Configure system settings
- Review security options

### Assessment:
Administrative tasks exercise

## Module 5: Troubleshooting and Support

### Duration: 30 minutes

### Topics Covered:
1. Common issues and solutions
2. Error messages and meanings
3. How to get help
4. Support resources

### Hands-on Exercise:
- Identify and resolve common issues
- Access help resources
- Contact support (simulation)

## Training Materials

### Provided Materials:
- This training manual
- User manual for reference
- Quick reference guide
- Sample data for exercises

### Additional Resources:
- Online help documentation
- Video tutorials (if available)
- Support contact information

## Training Exercises

### Exercise 1: Basic Navigation
Complete a series of navigation tasks

### Exercise 2: Core Workflow
Execute a complete business process

### Exercise 3: Advanced Features
Use advanced features to accomplish specific tasks

## Assessment and Certification

### Knowledge Check:
- Multiple choice questions
- Practical demonstrations
- Scenario-based questions

### Passing Criteria:
- 80% or higher on knowledge check
- Successful completion of practical exercises

### Certification:
Upon successful completion, users receive training certification

## Post-Training Support

### Resources Available:
- User manual for reference
- Online help system
- Email support
- Phone support during business hours

### Refresher Training:
Available upon request or when major updates are released

## Trainer Notes

### Preparation:
- Set up training environment
- Prepare sample data
- Test all features before training
- Review common questions

### Tips for Effective Training:
- Allow time for questions
- Encourage hands-on practice
- Relate features to real use cases
- Be patient with different learning speeds

"""

        return content
