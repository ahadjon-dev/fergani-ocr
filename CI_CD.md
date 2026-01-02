# Fergani OCR - CI/CD Documentation

This document describes the Continuous Integration and Continuous Deployment (CI/CD) pipeline for the Fergani OCR project.

## Workflow Overview

We use **GitHub Actions** for automated testing, linting, and deployment.

### Branch Strategy

```
develop (development) → PR with CI checks → main (production)
```

- **`develop`**: Development branch where all features are merged
- **`main`**: Production branch, auto-deploys to Railway

---

## CI Workflow (Runs on PRs to `develop`)

### Triggered On:

- Pull requests to `develop` branch
- Direct pushes to `develop` branch

### What It Does:

1. **🎨 Code Formatting Check (Black)**

   - Ensures code follows Python Black formatting standards
   - Line length: 127 characters
   - Fails if code is not formatted

2. **📋 Import Sorting Check (isort)**

   - Verifies imports are properly organized
   - Compatible with Black formatting
   - Fails if imports are not sorted

3. **🔍 Linting (Flake8)**

   - Checks for syntax errors and code quality issues
   - Max complexity: 10
   - Catches undefined names and syntax errors

4. **🔧 Migration Check**

   - Verifies no unapplied model changes
   - Runs `makemigrations --check --dry-run`
   - Fails if migrations are missing

5. **🗄️ Database Migration Test**

   - Applies all migrations on PostgreSQL test database
   - Ensures migrations are valid
   - Uses PostgreSQL 15 service container

6. **🧪 Test Suite Execution**
   - Runs all 44+ tests
   - Measures code coverage
   - Requires minimum 70% coverage
   - Generates coverage report

### Service Containers:

- **PostgreSQL 15**: Test database
- **Tesseract OCR**: Installed via apt-get

---

## Deployment Workflow (Runs on Push to `main`)

### Triggered On:

- Pushes to `main` branch (after merging from `develop`)

### What It Does:

1. **✅ Sanity Checks**

   - Runs `python manage.py check --deploy`
   - Validates production settings

2. **🚀 Auto-Deploy to Railway**
   - Railway automatically deploys from `main` branch
   - No manual deployment needed

---

## Local Development Workflow

### Before Creating a PR:

1. **Format your code:**

```bash
cd fergani
black .
isort .
```

2. **Run linting:**

```bash
flake8 .
```

3. **Check for missing migrations:**

```bash
python manage.py makemigrations --check --dry-run
```

4. **Run tests locally:**

```bash
python manage.py test tests/
```

5. **Check coverage:**

```bash
coverage run --source='ocr' manage.py test tests/
coverage report
```

### Install Development Tools:

```bash
pip install black flake8 isort coverage
```

---

## Setting Up Your Workflow

### 1. Install Pre-commit Hook (Optional but Recommended)

Create `.git/hooks/pre-commit`:

```bash
#!/bin/bash
cd fergani
echo "🎨 Formatting code with Black..."
black .

echo "📋 Sorting imports with isort..."
isort .

echo "🔍 Running flake8..."
flake8 . || exit 1

echo "🧪 Running tests..."
python manage.py test tests/ || exit 1

echo "✅ All checks passed! Proceeding with commit..."
```

Make it executable:

```bash
chmod +x .git/hooks/pre-commit
```

### 2. GitHub Repository Settings

#### Required Status Checks

Go to: `Settings` → `Branches` → `Branch protection rules` → `develop`

Enable:

- ✅ Require status checks to pass before merging
- ✅ Require branches to be up to date before merging
- Select checks:
  - `Run Tests & Quality Checks`

#### Auto-merge from develop to main

Option 1: Manual merge after PR approval

Option 2: GitHub Action (create `.github/workflows/auto-merge.yml`):

```yaml
name: Auto-merge to main
on:
  push:
    branches: [develop]
jobs:
  merge:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Merge to main
        run: |
          git config user.name github-actions
          git config user.email github-actions@github.com
          git checkout main
          git merge develop
          git push
```

---

## CI/CD File Structure

```
.github/
└── workflows/
    ├── ci.yml        # CI checks for PRs to develop
    └── deploy.yml    # Auto-deploy on push to main

.flake8               # Flake8 configuration
pyproject.toml        # Black, isort, coverage config
```

---

## Workflow Status Badges

Add these to your README.md:

```markdown
![CI Status](https://github.com/YOUR_USERNAME/fergani-ocr/workflows/CI%20-%20Fergani%20OCR/badge.svg?branch=develop)
![Deployment](https://github.com/YOUR_USERNAME/fergani-ocr/workflows/Deploy%20to%20Production/badge.svg?branch=main)
```

---

## Code Quality Standards

### Black (Code Formatter)

- Line length: 127 characters
- Python 3.11+ syntax
- Automatically formats code

### isort (Import Sorter)

- Groups imports: stdlib → third-party → local
- Compatible with Black
- One import per line

### Flake8 (Linter)

- Max line length: 127
- Max complexity: 10
- Ignores Black-incompatible rules

### Coverage

- Minimum: 70%
- Excludes: migrations, tests, admin, apps, **init**
- Reports missing lines

---

## Troubleshooting

### CI Fails: "Code not formatted with Black"

**Fix:**

```bash
cd fergani
black .
git add .
git commit -m "Format code with Black"
git push
```

### CI Fails: "Imports not sorted"

**Fix:**

```bash
cd fergani
isort .
git add .
git commit -m "Sort imports with isort"
git push
```

### CI Fails: "Missing migrations"

**Fix:**

```bash
cd fergani
python manage.py makemigrations
git add ocr/migrations/
git commit -m "Add missing migrations"
git push
```

### CI Fails: "Tests failed"

**Debug:**

```bash
cd fergani
python manage.py test tests/ --verbosity=2
```

### CI Fails: "Coverage below 70%"

**Check coverage:**

```bash
coverage run --source='ocr' manage.py test tests/
coverage report
coverage html  # Open htmlcov/index.html in browser
```

---

## Best Practices

### For Developers:

1. ✅ Always work on feature branches
2. ✅ Run tests before creating PR
3. ✅ Format code with Black before committing
4. ✅ Keep test coverage above 70%
5. ✅ Write meaningful commit messages

### For Code Reviews:

1. ✅ Check CI status before reviewing
2. ✅ Verify tests are meaningful
3. ✅ Ensure new features have tests
4. ✅ Check for proper error handling

### Git Workflow:

```bash
# Create feature branch from develop
git checkout develop
git pull origin develop
git checkout -b feature/my-feature

# Make changes and commit
git add .
git commit -m "Add feature X"

# Push and create PR
git push origin feature/my-feature

# After PR is merged to develop, delete branch
git checkout develop
git pull origin develop
git branch -d feature/my-feature
```

---

## Monitoring

### GitHub Actions Dashboard

- View workflow runs: `Actions` tab in GitHub
- Check logs for failed jobs
- Re-run failed workflows

### Railway Deployment

- Monitor: https://railway.app/dashboard
- View logs in Railway dashboard
- Check deployment status

---

## Future Enhancements

Consider adding:

- [ ] Automated dependency updates (Dependabot)
- [ ] Security scanning (CodeQL)
- [ ] Performance testing
- [ ] E2E testing with Playwright/Selenium
- [ ] Automated changelog generation
- [ ] Release automation
- [ ] Slack/Discord notifications

---

**Your CI/CD pipeline is ready! 🚀**

Every PR to `develop` will be automatically tested, and every push to `main` will deploy to production!
