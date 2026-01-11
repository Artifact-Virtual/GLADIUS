#!/bin/bash

# Enterprise Automation Suite - Quick Setup Script

echo "=================================================="
echo "Enterprise Automation Suite - Quick Setup"
echo "=================================================="
echo ""

# Check Python version
echo "Checking Python version..."
PYTHON_VERSION=$(python3 --version 2>&1 | awk '{print $2}')
echo "Found Python $PYTHON_VERSION"

if ! command -v python3 &> /dev/null; then
    echo "ERROR: Python 3 is not installed!"
    exit 1
fi

# Create .env file
echo ""
echo "Setting up configuration..."
if [ ! -f .env ]; then
    echo "Copying .env.template to .env..."
    cp .env.template .env
    echo "✅ Created .env file"
    echo "⚠️  Please edit .env and add your API keys!"
else
    echo "ℹ️  .env file already exists, skipping..."
fi

# Install dependencies
echo ""
echo "Installing dependencies..."
pip3 install --upgrade pip
pip3 install -r requirements.txt

echo ""
echo "=================================================="
echo "Setup Complete!"
echo "=================================================="
echo ""
echo "Next steps:"
echo ""
echo "1. Edit your .env file:"
echo "   nano .env"
echo ""
echo "2. Add your API keys:"
echo "   - AI_API_KEY (OpenAI, Anthropic, or Cohere)"
echo "   - Social media credentials"
echo "   - ERP system credentials"
echo "   - Discord webhook URL (optional)"
echo ""
echo "3. Run the examples:"
echo "   python3 examples.py"
echo ""
echo "4. Or start the full system:"
echo "   python3 -c 'import asyncio; from automata import EnterpriseManager; asyncio.run(EnterpriseManager().start())'"
echo ""
echo "Documentation:"
echo "   - IMPLEMENTATION_COMPLETE.md - Full feature documentation"
echo "   - README_FINAL.md - Quick start guide"
echo "   - .env.template - All configuration options"
echo ""
echo "🚀 Your autonomous business automation system is ready!"
echo ""
