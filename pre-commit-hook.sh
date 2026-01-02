#!/bin/bash
# Pre-commit hook for Fergani OCR
# Automatically runs Black, isort, and Flake8 on commit

echo "� Running pre-commit checks..."

# Get list of staged Python files
PYTHON_FILES=$(git diff --cached --name-only --diff-filter=ACM | grep '\.py$' || true)

if [ -z "$PYTHON_FILES" ]; then
    echo "✅ No Python files to check"
    exit 0
fi

echo "📋 Checking Python files:"
echo "$PYTHON_FILES"
echo ""

# 1. Run Black formatter
echo "🎨 Running Black formatter..."
black $PYTHON_FILES
BLACK_EXIT=$?

if [ $BLACK_EXIT -eq 0 ]; then
    echo "✅ Black formatting complete"
else
    echo "❌ Black formatting failed"
    exit 1
fi
echo ""

# 2. Run isort
echo "� Checking import sorting with isort..."
isort $PYTHON_FILES
ISORT_EXIT=$?

if [ $ISORT_EXIT -eq 0 ]; then
    echo "✅ Import sorting complete"
else
    echo "❌ Import sorting failed"
    exit 1
fi
echo ""

# 3. Run flake8 with detailed output
echo "🔍 Running flake8 syntax check..."
flake8 $PYTHON_FILES
FLAKE8_EXIT=$?

if [ $FLAKE8_EXIT -eq 0 ]; then
    echo "✅ Flake8 checks passed"
else
    echo "❌ Flake8 found issues (see above for details)"
    exit 1
fi
echo ""

# Re-add formatted files to staging area
git add $PYTHON_FILES

echo "✅ All pre-commit checks passed!"
echo "🎉 Proceeding with commit..."
echo ""

exit 0
