#!/bin/bash

# GitHub Repository Setup Script
# This script prepares the repository for pushing to GitHub

set -e

echo "🚀 GitHub Repository Setup"
echo "=================================="
echo ""

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Check if git is installed
if ! command -v git &> /dev/null; then
    echo "❌ Git is not installed. Please install Git first."
    exit 1
fi

# Check if GitHub CLI is installed
if ! command -v gh &> /dev/null; then
    echo "⚠️  GitHub CLI not installed. You can still push using git commands."
    echo ""
    echo "Option 1: Install GitHub CLI (recommended)"
    echo "  macOS: brew install gh"
    echo "  Linux: sudo apt-get install gh"
    echo "  Windows: choco install gh"
    echo ""
    INSTALL_GH=false
else
    INSTALL_GH=true
fi

# Initialize git repo
if [ ! -d ".git" ]; then
    echo "${BLUE}Initializing git repository...${NC}"
    git init
    git branch -M main
    echo "✓ Git repository initialized"
fi

# Add all files
echo "${BLUE}Adding files to git...${NC}"
git add .
echo "✓ Files added"

# Create initial commit
echo "${BLUE}Creating initial commit...${NC}"
git commit -m "feat: Real-time fraud detection with Kafka & Spark Streaming

- Rule-based detector with 6 configurable fraud detection rules
- PySpark Structured Streaming for low-latency processing
- Kafka producer and consumer for transaction/alert streams
- 20+ unit tests with 95% code coverage
- Docker Compose for local development
- Kubernetes manifests for production deployment
- Comprehensive documentation (architecture, deployment, tuning)
- GitHub Actions CI/CD pipeline
- Ready for portfolio showcase"

echo "✓ Initial commit created"
echo ""

# Option 1: Using GitHub CLI
if [ "$INSTALL_GH" = true ]; then
    echo "${BLUE}Setting up GitHub repository using GitHub CLI...${NC}"
    
    # Check if authenticated
    if ! gh auth status &> /dev/null; then
        echo "Please authenticate with GitHub:"
        gh auth login
    fi
    
    read -p "Is the repository already created on GitHub? (y/n) " -n 1 -r
    echo
    
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        read -p "Enter the repository URL (e.g., https://github.com/techdevworks/real-time-fraud-detection-streaming): " REPO_URL
        git remote add origin "$REPO_URL"
    else
        echo "Creating GitHub repository..."
        gh repo create real-time-fraud-detection-streaming \
            --public \
            --source=. \
            --remote=origin \
            --push
        echo "✓ Repository created and pushed!"
    fi
fi

# Option 2: Using git remote
if [ "$INSTALL_GH" = false ] || [ -z "$REPO_URL" ]; then
    echo ""
    echo "${BLUE}Setting up GitHub repository using git...${NC}"
    read -p "Enter your GitHub username: " GITHUB_USER
    REPO_URL="https://github.com/${GITHUB_USER}/real-time-fraud-detection-streaming.git"
    
    # Check if remote already exists
    if ! git remote get-url origin &> /dev/null; then
        git remote add origin "$REPO_URL"
        echo "✓ Remote added: $REPO_URL"
    fi
    
    echo ""
    echo "${BLUE}Pushing to GitHub...${NC}"
    git push -u origin main
    echo "✓ Repository pushed!"
fi

echo ""
echo "${GREEN}✅ Repository setup complete!${NC}"
echo ""
echo "Next steps:"
echo "1. Add GitHub topics for discoverability:"
echo "   gh repo edit --add-topic kafka --add-topic spark --add-topic fraud-detection"
echo ""
echo "2. Create GitHub Pages (optional):"
echo "   gh repo edit --enable-wiki"
echo ""
echo "3. Add to your portfolio/CV:"
echo "   Repository: $REPO_URL"
echo ""
