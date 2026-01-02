# Setting Up CI/CD for Fergani OCR

Quick guide to set up the CI/CD pipeline for local development and GitHub Actions.

## 📦 Installation

### 1. Install Development Tools

```bash
cd /home/ahadjon/work/fergani/fergani-ocr
pip install black flake8 isort coverage
```

### 2. Install Pre-commit Hook (Optional but Recommended)

```bash
# Make the script executable
chmod +x pre-commit-hook.sh

# Copy to git hooks
cp pre-commit-hook.sh .git/hooks/pre-commit
chmod +x .git/hooks/pre-commit
```

Now every time you commit, it will automatically:

- Format code with Black
- Sort imports with isort
- Run flake8 linting
- Check for missing migrations
- Run all tests

## 🎯 Usage

### Format Code

```bash
cd fergani
black .
isort .
```

### Run Linting

```bash
flake8 .
```

### Check Migrations

```bash
python manage.py makemigrations --check --dry-run
```

### Run Tests with Coverage

```bash
coverage run --source='ocr' manage.py test tests/
coverage report
coverage html  # Generate HTML report
```

## 🌿 Branch Workflow

```bash
# 1. Create feature branch from develop
git checkout develop
git pull origin develop
git checkout -b feature/awesome-feature

# 2. Make changes and commit
# (pre-commit hook runs automatically)
git add .
git commit -m "Add awesome feature"

# 3. Push and create PR to develop
git push origin feature/awesome-feature

# 4. After PR is merged, merge develop to main
git checkout main
git pull origin main
git merge develop
git push origin main  # This triggers deployment!
```

## 🚀 GitHub Actions

### CI Workflow (on PR to develop)

- Runs on every PR to `develop` branch
- Checks: formatting, linting, migrations, tests
- Must pass before merging

### Deploy Workflow (on push to main)

- Runs on every push to `main` branch
- Auto-deploys to Railway

## 🔧 Configuration Files

- `.github/workflows/ci.yml` - CI workflow
- `.github/workflows/deploy.yml` - Deployment workflow
- `.flake8` - Flake8 configuration
- `pyproject.toml` - Black, isort, coverage configuration
- `.gitignore` - Git ignore patterns

## 📚 Documentation

See [CI_CD.md](CI_CD.md) for detailed documentation.

## ✅ Quick Checklist Before Committing

- [ ] Code is formatted with Black
- [ ] Imports are sorted with isort
- [ ] No flake8 errors
- [ ] All tests pass
- [ ] Coverage is above 70%
- [ ] No unapplied migrations

**Pro tip**: Install the pre-commit hook to do all this automatically!
