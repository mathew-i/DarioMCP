#!/bin/bash
# Script to set up main and develop branches
# Run this script after merging the initial commit

set -e

echo "Setting up repository branches..."

# Create main branch if it doesn't exist
if ! git show-ref --quiet refs/heads/main; then
    echo "Creating main branch..."
    git branch main
    git push origin main
else
    echo "main branch already exists"
fi

# Create develop branch from main if it doesn't exist
if ! git show-ref --quiet refs/heads/develop; then
    echo "Creating develop branch from main..."
    git branch develop main
    git push origin develop
else
    echo "develop branch already exists"
fi

echo "Branch setup complete!"
echo "To set develop as the default branch:"
echo "1. Go to GitHub repository Settings"
echo "2. Click on Branches"
echo "3. Change default branch to 'develop'"
