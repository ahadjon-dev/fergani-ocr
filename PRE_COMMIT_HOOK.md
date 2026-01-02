# Git Pre-Commit Hook Setup

This directory contains a pre-commit hook that automatically runs Black and isort before each commit.

## Features

- ✅ **Automatic Black formatting** - Formats Python code on commit
- ✅ **Automatic isort sorting** - Sorts imports on commit  
- ✅ **Flake8 syntax checking** - Prevents commits with syntax errors
- ✅ **Auto-fix and re-stage** - Automatically formats and re-adds files

## Installation

Run this command from the project root (`fergani/` directory):

```bash
cp pre-commit-hook.sh .git/hooks/pre-commit && chmod +x .git/hooks/pre-commit
```

Or use the install script:

```bash
./install-hook.sh
```

## What It Does

When you run `git commit`, the hook will:

1. **Find all Python files** being committed
2. **Run Black** to check formatting
   - If issues found: Auto-formats and re-stages files
3. **Run isort** to check import order
   - If issues found: Auto-fixes and re-stages files
4. **Run Flake8** for syntax errors
   - If errors found: Blocks commit (you must fix manually)

## Usage

Just commit as normal:

```bash
git add .
git commit -m "Your commit message"
```

The hook runs automatically and will:
- ✅ Format your code with Black
- ✅ Sort your imports with isort
- ✅ Check for syntax errors
- ✅ Auto-stage the formatted files

## Bypass Hook (Not Recommended)

If you need to bypass the hook temporarily:

```bash
git commit --no-verify -m "Your message"
```

⚠️ **Warning**: This skips all checks and should only be used in emergencies.

## Uninstall

To remove the hook:

```bash
rm .git/hooks/pre-commit
```

## Requirements

Make sure these tools are installed in your virtual environment:

```bash
pip install black isort flake8
```

(These should already be in your `requirements.txt`)
