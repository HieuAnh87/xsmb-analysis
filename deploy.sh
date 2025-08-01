#!/bin/bash

# 🚀 Northern Vietnam Lottery Analysis System - Deployment Script
# Tự động triển khai hệ thống lên GitHub

echo "🎲 NORTHERN VIETNAM LOTTERY ANALYSIS SYSTEM"
echo "=============================================="
echo "🚀 Automated Deployment Script"
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

print_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

# Check if git is installed
if ! command -v git &> /dev/null; then
    print_error "Git is not installed. Please install Git first."
    exit 1
fi

print_status "Git is available"

# Check if we're in the right directory
if [ ! -f "README.md" ] || [ ! -d "src" ] || [ ! -d ".github" ]; then
    print_error "Please run this script from the project root directory"
    exit 1
fi

print_status "Project structure verified"

# Get GitHub repository URL from user
echo ""
print_info "Please provide your GitHub repository information:"
echo ""

read -p "Enter your GitHub username: " GITHUB_USERNAME
read -p "Enter repository name (default: xsmb-analysis): " REPO_NAME

# Set default repo name if empty
if [ -z "$REPO_NAME" ]; then
    REPO_NAME="xsmb-analysis"
fi

REPO_URL="https://github.com/$GITHUB_USERNAME/$REPO_NAME.git"

echo ""
print_info "Repository URL: $REPO_URL"
echo ""

# Confirm before proceeding
read -p "Is this correct? (y/n): " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    print_warning "Deployment cancelled by user"
    exit 1
fi

echo ""
print_info "Starting deployment process..."
echo ""

# Check if git repository is already initialized
if [ ! -d ".git" ]; then
    print_info "Initializing Git repository..."
    git init
    print_status "Git repository initialized"
else
    print_status "Git repository already exists"
fi

# Check if there are any changes to commit
if git diff --quiet && git diff --staged --quiet; then
    print_warning "No changes to commit"
else
    print_info "Adding files to Git..."
    git add .
    
    print_info "Creating commit..."
    git commit -m "🚀 Deploy: Northern Vietnam Lottery Analysis System

🎲 Automated deployment of lottery analysis system
✨ Ready for GitHub Actions execution
📊 Includes all modules: collection, validation, analytics, notifications"
    
    print_status "Changes committed successfully"
fi

# Set up remote origin
print_info "Setting up remote repository..."

# Remove existing origin if it exists
git remote remove origin 2>/dev/null || true

# Add new origin
git remote add origin "$REPO_URL"
print_status "Remote origin configured"

# Set main branch
print_info "Setting up main branch..."
git branch -M main

# Push to GitHub
print_info "Pushing code to GitHub..."
echo ""
print_warning "You may be prompted for GitHub credentials..."
echo ""

if git push -u origin main; then
    print_status "Code successfully pushed to GitHub!"
else
    print_error "Failed to push to GitHub. Please check:"
    echo "  1. Repository exists on GitHub"
    echo "  2. You have push permissions"
    echo "  3. Your GitHub credentials are correct"
    echo ""
    print_info "You can try pushing manually with:"
    echo "  git push -u origin main"
    exit 1
fi

echo ""
echo "🎉 DEPLOYMENT COMPLETED SUCCESSFULLY!"
echo "====================================="
echo ""
print_status "Your lottery analysis system is now on GitHub!"
echo ""
print_info "Next steps:"
echo "  1. Visit: https://github.com/$GITHUB_USERNAME/$REPO_NAME"
echo "  2. Go to Actions tab and enable workflows"
echo "  3. Optionally configure GitHub Secrets for notifications"
echo "  4. Run workflow manually to test, or wait for 7 PM Vietnam time"
echo ""
print_info "Useful links:"
echo "  📊 Repository: https://github.com/$GITHUB_USERNAME/$REPO_NAME"
echo "  ⚙️  Actions: https://github.com/$GITHUB_USERNAME/$REPO_NAME/actions"
echo "  🔧 Settings: https://github.com/$GITHUB_USERNAME/$REPO_NAME/settings"
echo ""
print_info "Documentation:"
echo "  📖 README.md - Complete usage guide"
echo "  🚀 DEPLOYMENT.md - Detailed deployment instructions"
echo "  📝 CHANGELOG.md - Version history"
echo ""

# Offer to open GitHub repository
if command -v xdg-open &> /dev/null; then
    read -p "Open GitHub repository in browser? (y/n): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        xdg-open "https://github.com/$GITHUB_USERNAME/$REPO_NAME"
    fi
elif command -v open &> /dev/null; then
    read -p "Open GitHub repository in browser? (y/n): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        open "https://github.com/$GITHUB_USERNAME/$REPO_NAME"
    fi
fi

echo ""
print_status "Deployment script completed!"
print_info "Your Northern Vietnam Lottery Analysis System is ready! 🎲✨"
