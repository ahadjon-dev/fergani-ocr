#!/bin/bash
# Pre-commit hook for Fergani OCR
# Copy this to .git/hooks/pre-commit and make it executable:
# chmod +x .git/hooks/pre-commit

set -e

echo "🚀 Running pre-commit checks..."
echo ""

# Change to fergani directory
cd fergani

# 1. Format code with Black
echo "🎨 Formatting code with Black..."
black . --quiet
if [ $? -eq 0 ]; then
    echo "✅ Black formatting: PASSED"
else
    echo "❌ Black formatting: FAILED"
    exit 1
fi
echo ""

# 2. Sort imports with isort
echo "📋 Sorting imports with isort..."
isort . --quiet
if [ $? -eq 0 ]; then
    echo "✅ Import sorting: PASSED"
else
    echo "❌ Import sorting: FAILED"
    exit 1
fi
echo ""

# 3. Run flake8
echo "🔍 Running flake8 linter..."
flake8 . --quiet
if [ $? -eq 0 ]; then
    echo "✅ Flake8 linting: PASSED"
else
    echo "❌ Flake8 linting: FAILED"
    echo "Run 'flake8 .' to see detailed errors"
    exit 1
fi
echo ""

# 4. Check for missing migrations
echo "🔧 Checking for missing migrations..."
python manage.py makemigrations --check --dry-run --no-input > /dev/null 2>&1
if [ $? -eq 0 ]; then
    echo "✅ Migrations check: PASSED"
else
    echo "⚠️  Warning: You may have unapplied model changes"
    echo "Run 'python manage.py makemigrations' if needed"
fi
echo ""

# 5. Run tests
echo "🧪 Running tests..."
python manage.py test tests/ --verbosity=0
if [ $? -eq 0 ]; then
    echo "✅ Tests: PASSED"
else
    echo "❌ Tests: FAILED"
    echo "Run 'python manage.py test tests/ --verbosity=2' for details"
    exit 1
fi
echo ""

# Add formatted files back to staging
cd ..
git add fergani/

echo "✅ All pre-commit checks passed!"
echo "🎉 Ready to commit!"
echo ""

exit 0
