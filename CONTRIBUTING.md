# Contributing to AnomaaH Delivery Platform

Thank you for your interest in contributing to AnomaaH! This document provides guidelines and instructions for contributing to the project.

## 🌟 How to Contribute

There are many ways to contribute to AnomaaH:

1. **Report bugs** - Help us identify and fix issues
2. **Suggest features** - Share ideas for new functionality
3. **Improve documentation** - Help make our docs clearer
4. **Write code** - Submit bug fixes or new features
5. **Review pull requests** - Help maintain code quality

## 🚀 Getting Started

### 1. Fork and Clone

```bash
# Fork the repository on GitHub, then clone your fork
git clone https://github.com/YOUR_USERNAME/AnomaaH-.git
cd AnomaaH-

# Add upstream remote
git remote add upstream https://github.com/Cedcast/AnomaaH-.git
```

### 2. Set Up Development Environment

```bash
# Copy environment file
cp .env.example .env

# Edit .env with your configuration
nano .env

# Start services
docker-compose up -d --build

# Verify setup
curl http://localhost:8000/health
```

### 3. Create a Branch

```bash
# Update your fork
git checkout main
git pull upstream main

# Create a feature branch
git checkout -b feature/your-feature-name
# or
git checkout -b fix/bug-description
```

## 📝 Development Guidelines

### Code Style

We follow PEP 8 for Python code with some modifications:

- **Line length**: 120 characters (instead of 79)
- **Imports**: Use absolute imports, grouped by: standard library, third-party, local
- **Docstrings**: Use Google style docstrings
- **Type hints**: Use type hints for function parameters and return values

### Example Code Style

```python
"""
Module docstring explaining the module purpose.
"""

import os
from typing import Optional, Dict, List

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from shared.ghana_utils import validate_ghana_phone


def process_order(
    order_id: str,
    customer_phone: str,
    amount: float
) -> Dict[str, any]:
    """
    Process a delivery order.
    
    Args:
        order_id: Unique order identifier
        customer_phone: Customer's Ghana phone number
        amount: Order amount in GHS
        
    Returns:
        Dictionary containing processed order details
        
    Raises:
        HTTPException: If validation fails
        
    Example:
        >>> process_order("ORD-123", "+233244123456", 50.00)
        {'order_id': 'ORD-123', 'status': 'confirmed', ...}
    """
    # Validate phone number
    phone_result = validate_ghana_phone(customer_phone)
    if not phone_result['valid']:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid phone number: {phone_result['error']}"
        )
    
    # Process order logic here
    return {
        'order_id': order_id,
        'status': 'confirmed',
        'phone': phone_result['formatted'],
        'amount': amount
    }
```

### Naming Conventions

- **Files**: `snake_case.py`
- **Classes**: `PascalCase`
- **Functions/Variables**: `snake_case`
- **Constants**: `UPPER_SNAKE_CASE`
- **Private members**: `_leading_underscore`

### Code Organization

```
services/
└── service_name/
    ├── main.py          # FastAPI app
    ├── models.py        # SQLAlchemy models
    ├── schemas.py       # Pydantic schemas
    ├── crud.py          # Database operations
    ├── dependencies.py  # FastAPI dependencies
    ├── requirements.txt # Service-specific deps
    └── tests/          # Service tests
        ├── test_main.py
        └── test_models.py
```

## ✅ Testing

### Writing Tests

We use `pytest` for testing. Write tests for:

1. **Unit tests** - Test individual functions
2. **Integration tests** - Test service interactions
3. **API tests** - Test endpoints

### Test Example

```python
# tests/test_ghana_utils.py
import pytest
from shared.ghana_utils import validate_ghana_phone


def test_validate_valid_ghana_phone():
    """Test validation of valid Ghana phone numbers."""
    result = validate_ghana_phone("+233244123456")
    assert result['valid'] is True
    assert result['network'] == 'MTN'
    assert result['formatted'] == '+233244123456'


def test_validate_invalid_ghana_phone():
    """Test validation of invalid phone numbers."""
    result = validate_ghana_phone("123456")
    assert result['valid'] is False
    assert result['error'] is not None


@pytest.mark.parametrize("phone,expected_network", [
    ("+233244123456", "MTN"),
    ("+233201234567", "Vodafone"),
    ("+233261234567", "AirtelTigo"),
])
def test_detect_mobile_network(phone, expected_network):
    """Test mobile network detection."""
    result = validate_ghana_phone(phone)
    assert result['network'] == expected_network
```

### Running Tests

```bash
# Run all tests
pytest

# Run specific test file
pytest tests/test_ghana_utils.py

# Run with coverage
pytest --cov=services --cov=shared

# Run specific test
pytest tests/test_ghana_utils.py::test_validate_valid_ghana_phone
```

## 🔍 Code Review Process

### Before Submitting

1. **Run tests**: Ensure all tests pass
2. **Run linters**: Fix any linting issues
3. **Update documentation**: Update relevant docs
4. **Test manually**: Verify your changes work

```bash
# Run linters
flake8 services shared
black --check services shared
isort --check services shared

# Run tests
pytest

# Validate environment
python3 scripts/validate_env.py
```

### Pull Request Guidelines

1. **One feature per PR** - Keep changes focused
2. **Clear description** - Explain what and why
3. **Reference issues** - Link related issues
4. **Add tests** - Include tests for new features
5. **Update docs** - Update relevant documentation

### PR Template

```markdown
## Description
Brief description of changes

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Breaking change
- [ ] Documentation update

## Testing
- [ ] Unit tests added/updated
- [ ] Integration tests added/updated
- [ ] Manual testing completed

## Checklist
- [ ] Code follows project style guidelines
- [ ] Tests pass locally
- [ ] Documentation updated
- [ ] No new warnings/errors
- [ ] Self-reviewed code

## Screenshots (if applicable)
Add screenshots for UI changes
```

## 🐛 Reporting Bugs

### Before Reporting

1. **Search existing issues** - Check if already reported
2. **Update to latest** - Verify bug exists in latest version
3. **Reproduce** - Can you consistently reproduce it?

### Bug Report Template

```markdown
## Bug Description
Clear description of the bug

## Steps to Reproduce
1. Go to '...'
2. Click on '...'
3. Scroll down to '...'
4. See error

## Expected Behavior
What should happen

## Actual Behavior
What actually happens

## Environment
- OS: [e.g. Ubuntu 22.04]
- Python: [e.g. 3.11]
- Docker: [e.g. 24.0]
- Browser: [e.g. Chrome 120]

## Additional Context
Screenshots, logs, or other relevant information
```

## 💡 Suggesting Features

### Feature Request Template

```markdown
## Feature Description
Clear description of the feature

## Problem Statement
What problem does this solve?

## Proposed Solution
How should this feature work?

## Alternatives Considered
Other approaches you've considered

## Ghana-Specific Relevance
How does this benefit Ghanaian users/businesses?

## Additional Context
Mockups, examples, or references
```

## 📚 Documentation

### Documentation Standards

- **Clear and concise** - Easy to understand
- **Examples** - Include code examples
- **Up-to-date** - Keep in sync with code
- **Well-structured** - Logical organization

### Documentation Types

1. **Code comments** - Explain complex logic
2. **Docstrings** - Document functions/classes
3. **README files** - Service overviews
4. **Guides** - Step-by-step instructions
5. **API docs** - Endpoint documentation

## 🔐 Security

### Reporting Security Issues

**DO NOT** create public issues for security vulnerabilities.

Instead:
1. Email security@anomaah.gh
2. Include detailed description
3. Wait for response before disclosing

### Security Guidelines

- Never commit secrets/credentials
- Use environment variables
- Validate all inputs
- Follow security best practices
- Review [SECURITY.md](SECURITY.md)

## 🌍 Ghana-Specific Contributions

We especially welcome contributions that improve the platform for Ghanaian users:

- **Localization** - Translations (Twi, Ga, Ewe, etc.)
- **Payment integrations** - Local payment providers
- **Regional features** - Ghana-specific functionality
- **Documentation** - Ghana deployment guides
- **Testing** - With Ghana-specific data

## 📋 Commit Messages

### Format

```
<type>(<scope>): <subject>

<body>

<footer>
```

### Types

- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style changes (formatting)
- `refactor`: Code refactoring
- `test`: Adding/updating tests
- `chore`: Maintenance tasks

### Examples

```
feat(auth): add biometric authentication support

Implement fingerprint and face recognition login for rider app.
Supports Android biometric API for secure authentication.

Closes #123
```

```
fix(booking): validate Ghana phone numbers correctly

Fix phone validation regex to properly accept 0XX format.
Add tests for various Ghana phone number formats.

Fixes #456
```

## 👥 Community

### Communication Channels

- **GitHub Issues** - Bug reports, features
- **GitHub Discussions** - Questions, ideas
- **Email** - support@anomaah.gh

### Code of Conduct

Be respectful, inclusive, and constructive. We welcome contributors of all backgrounds and experience levels.

## 📜 License

By contributing, you agree that your contributions will be licensed under the same license as the project (MIT License).

## 🙏 Recognition

Contributors are recognized in:
- `CONTRIBUTORS.md` file
- Release notes
- Project README

Thank you for contributing to AnomaaH! 🇬🇭
