#!/bin/bash
# Install pre-commit hook script

echo "📦 Installing pre-commit hook..."

# Check if we're in the right directory
if [ ! -f "pre-commit-hook.sh" ]; then
    echo "❌ Error: pre-commit-hook.sh not found!"
    echo "Please run this script from the fergani/ directory"
    exit 1
fi

# Copy hook to .git/hooks/
cp pre-commit-hook.sh .git/hooks/pre-commit

# Make it executable
chmod +x .git/hooks/pre-commit

echo "✅ Pre-commit hook installed successfully!"
echo ""
echo "The hook will now run automatically on every commit."
echo "It will:"
echo "  • Format code with Black"
echo "  • Sort imports with isort"
echo "  • Check for syntax errors with Flake8"
echo ""
echo "To uninstall: rm .git/hooks/pre-commit"
