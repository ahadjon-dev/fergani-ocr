# Contributing to Fergani OCR

Thank you for considering contributing to Fergani OCR! This document provides guidelines and instructions for contributing.

## 📋 Table of Contents

- [Getting Started](#getting-started)
- [Development Workflow](#development-workflow)
- [Code Quality Standards](#code-quality-standards)
- [Testing](#testing)
- [Pull Request Process](#pull-request-process)
- [Reporting Issues](#reporting-issues)

## 🚀 Getting Started

### 1. Fork and Clone

```bash
# Fork the repository on GitHub, then:
git clone https://github.com/YOUR_USERNAME/fergani-ocr.git
cd fergani-ocr
```

### 2. Set Up Development Environment

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Install development tools
pip install black flake8 isort coverage

# Install Tesseract OCR
sudo apt-get install tesseract-ocr  # Ubuntu/Debian
brew install tesseract              # macOS
```

### 3. Configure Pre-commit Hook

```bash
chmod +x pre-commit-hook.sh
cp pre-commit-hook.sh .git/hooks/pre-commit
```

### 4. Run Migrations and Tests

```bash
cd fergani
python manage.py migrate
python manage.py test tests/
```

## 🌿 Development Workflow

### Branch Strategy

We use **Git Flow** workflow:

- `main` - Production branch (auto-deploys)
- `develop` - Development branch (all PRs merge here)
- `feature/*` - Feature branches
- `bugfix/*` - Bug fix branches
- `hotfix/*` - Urgent production fixes

### Creating a Feature

```bash
# 1. Checkout develop and pull latest
git checkout develop
git pull origin develop

# 2. Create feature branch
git checkout -b feature/awesome-feature

# 3. Make your changes
# ... code, code, code ...

# 4. Run quality checks (or let pre-commit hook do it)
cd fergani
black .
isort .
flake8 .
python manage.py test tests/

# 5. Commit your changes
git add .
git commit -m "Add awesome feature

- Feature does X
- Improves Y
- Fixes #123"

# 6. Push to your fork
git push origin feature/awesome-feature

# 7. Create Pull Request to 'develop' branch
```

## ✨ Code Quality Standards

### Code Formatting (Black)

```bash
# Format all Python files
cd fergani
black .

# Check without modifying
black --check .
```

**Rules:**

- Line length: 127 characters
- Automatic string quote normalization
- Consistent trailing commas

### Import Sorting (isort)

```bash
# Sort all imports
isort .

# Check without modifying
isort --check-only .
```

**Order:**

1. Standard library imports
2. Third-party imports
3. Local application imports

### Linting (Flake8)

```bash
# Check for errors
flake8 .
```

**Rules:**

- Max line length: 127
- Max complexity: 10
- No undefined names
- No syntax errors

### Type Hints (Optional but Encouraged)

```python
def process_image(image_file, language: str = 'eng') -> Dict[str, Any]:
    """Process image and return results."""
    ...
```

## 🧪 Testing

### Writing Tests

```python
# tests/ocr/test_my_feature.py
from django.test import TestCase
from rest_framework.test import APITestCase

class MyFeatureTests(APITestCase):
    def test_awesome_functionality(self):
        """Test that awesome feature works."""
        response = self.client.post('/api/endpoint/', data)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.data['success'])
```

### Running Tests

```bash
# Run all tests
python manage.py test tests/

# Run specific test file
python manage.py test tests.ocr.test_my_feature

# Run with coverage
coverage run --source='ocr' manage.py test tests/
coverage report
coverage html  # Open htmlcov/index.html
```

### Test Requirements

- ✅ All new features must have tests
- ✅ Maintain minimum 70% coverage
- ✅ Tests should be clear and descriptive
- ✅ Use meaningful test names

## 📝 Pull Request Process

### Before Submitting PR

Ensure:

- [ ] Code is formatted with Black
- [ ] Imports are sorted with isort
- [ ] No Flake8 errors
- [ ] All tests pass locally
- [ ] Coverage is above 70%
- [ ] Migrations are created (if models changed)
- [ ] Documentation is updated
- [ ] Commit messages are descriptive

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

Describe how you tested this

## Checklist

- [ ] Code follows project style guidelines
- [ ] Tests pass locally
- [ ] Added/updated tests
- [ ] Updated documentation
- [ ] No new warnings
```

### PR Review Process

1. Create PR to `develop` branch
2. Wait for CI checks to pass
3. Request review from maintainers
4. Address review comments
5. Once approved, maintainer will merge

### Commit Message Guidelines

**Format:**

```
<type>: <subject>

<body>

<footer>
```

**Types:**

- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style changes
- `refactor`: Code refactoring
- `test`: Adding/updating tests
- `chore`: Maintenance tasks

**Example:**

```
feat: Add PDF page selection feature

- Users can now extract specific pages from PDFs
- Add 'pages' parameter to API endpoint
- Update documentation with examples

Closes #42
```

## 🐛 Reporting Issues

### Bug Reports

Include:

- Clear, descriptive title
- Steps to reproduce
- Expected vs actual behavior
- Environment details (OS, Python version, etc.)
- Screenshots if applicable
- Error messages/stack traces

### Feature Requests

Include:

- Clear description of the feature
- Use case / problem it solves
- Possible implementation approach
- Examples from other projects (if applicable)

### Issue Template

```markdown
## Description

Clear description of the issue

## Steps to Reproduce

1. Step one
2. Step two
3. ...

## Expected Behavior

What should happen

## Actual Behavior

What actually happens

## Environment

- OS: Ubuntu 22.04
- Python: 3.11.0
- Django: 5.0.1
- Tesseract: 5.3.0

## Additional Context

Screenshots, logs, etc.
```

## 📜 Code of Conduct

### Our Standards

- Be respectful and inclusive
- Welcome newcomers
- Accept constructive criticism
- Focus on what's best for the project
- Show empathy towards others

### Unacceptable Behavior

- Harassment or discrimination
- Trolling or insulting comments
- Personal or political attacks
- Public or private harassment

## 🏆 Recognition

Contributors will be:

- Added to CONTRIBUTORS.md
- Mentioned in release notes
- Thanked publicly in announcements

## 📚 Resources

- [Main README](README.md) - Project overview
- [CI/CD Guide](CI_CD.md) - CI/CD documentation
- [Setup Guide](SETUP_CI.md) - Quick setup
- [Database Architecture](DATABASE_ARCHITECTURE.md) - DB design
- [Testing Guide](fergani/tests/README.md) - Test documentation

## 💬 Questions?

- Open an issue for bugs/features
- Start a discussion for questions
- Check existing issues first

## 📄 License

By contributing, you agree that your contributions will be licensed under the MIT License.

---

**Thank you for contributing to Fergani OCR! 🎉**
