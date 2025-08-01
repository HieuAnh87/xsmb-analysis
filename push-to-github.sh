#!/bin/bash

echo "🎲 NORTHERN VIETNAM LOTTERY ANALYSIS SYSTEM"
echo "=============================================="
echo ""
echo "🚀 Push to GitHub Script"
echo ""

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${YELLOW}⚠️  IMPORTANT: Make sure you have created the repository on GitHub first!${NC}"
echo ""
echo "📋 Steps to create repository:"
echo "1. Go to: https://github.com/new"
echo "2. Repository name: xsmb-analysis"
echo "3. Description: 🎲 Hệ thống Thu thập và Phân tích Xổ số Miền Bắc tự động"
echo "4. Choose: Public"
echo "5. DON'T check: Add README, .gitignore, license"
echo "6. Click: Create repository"
echo ""

read -p "Have you created the repository on GitHub? (y/n): " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo -e "${RED}❌ Please create the repository first, then run this script again.${NC}"
    exit 1
fi

echo ""
echo "🚀 Pushing code to GitHub..."
echo ""

# Try to push
if git push -u origin main; then
    echo ""
    echo -e "${GREEN}🎉 SUCCESS! Code pushed to GitHub successfully!${NC}"
    echo ""
    echo "📍 Your repository: https://github.com/hieuda/xsmb-analysis"
    echo ""
    echo "🔧 Next steps:"
    echo "1. Go to: https://github.com/hieuda/xsmb-analysis"
    echo "2. Click 'Actions' tab"
    echo "3. Click 'I understand my workflows, go ahead and enable them'"
    echo "4. Click on the workflow name"
    echo "5. Click 'Run workflow' to test"
    echo ""
    echo -e "${GREEN}✅ Your lottery analysis system is now live on GitHub!${NC}"
else
    echo ""
    echo -e "${RED}❌ Failed to push to GitHub.${NC}"
    echo ""
    echo "🔍 Possible issues:"
    echo "1. Repository not created on GitHub"
    echo "2. Repository name incorrect"
    echo "3. No push permissions"
    echo ""
    echo "💡 Solutions:"
    echo "1. Make sure repository exists: https://github.com/hieuda/xsmb-analysis"
    echo "2. Check you're logged into the correct GitHub account"
    echo "3. Try again after creating the repository"
fi
